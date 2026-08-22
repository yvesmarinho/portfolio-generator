# Architecture Debate — portfolio-generator

**Data**: 2026-06-17  
**Participantes**: Yves Marinho + Claude Sonnet 4.6  
**Base**: `objetivo-init.yaml` (revisão 2026-06-17)  
**Status**: ✅ Decisões tomadas

---

## Contexto

Antes de iniciar a implementação, as seguintes questões arquiteturais foram debatidas para
garantir que a constitution e a especificação reflitam escolhas conscientes, e não defaults
implícitos.

---

## Debate 1 — Modelo de Processamento: Sequencial vs Multiprocessing

### Posições

| Opção | Prós | Contras |
|-------|------|---------|
| Sequencial (`pathlib` + loop) | Simples, debugável, sem race conditions | Lento para 100+ projetos |
| `concurrent.futures.ProcessPoolExecutor` | Paralelismo real (CPU-bound), throttling via `max_workers` | Overhead de spawn por projeto; complexidade de error propagation |
| `asyncio` + `aiofiles` | I/O eficiente para muitas leituras de arquivo pequeno | Python GIL irrelevante para CPU-bound; overhead para stat/read |

### Decisão: `concurrent.futures.ProcessPoolExecutor` com throttling

**Justificativa**: A tarefa é CPU-bound (contagem de arquivos, parsing de código) e I/O-bound
(leitura de múltiplos projetos). ProcessPoolExecutor contorna o GIL e permite configurar
`max_workers` via CLI flag `--workers N`. Default: `min(4, os.cpu_count())`.

**Implementação**:
```python
from concurrent.futures import ProcessPoolExecutor, as_completed

def scan_all(projects: list[Path], workers: int = 4) -> list[dict]:
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(scan_project, p): p for p in projects}
        return [f.result() for f in as_completed(futures)]
```

**Limite de RAM**: Cada worker processa 1 projeto por vez. RAM máxima estimada: `workers × 50 MB` = 200 MB @ 4 workers (< 512 MB target).

---

## Debate 2 — Detecção de Linguagem: Estratégia e Prioridade

### Posições

| Estratégia | Precisão | Velocidade | Custo |
|-----------|---------|-----------|-------|
| Contagem de extensões (`pathlib.glob`) | ~85% | Muito rápida | Zero |
| `pygments.lexers.guess_lexer_for_filename` | ~90% | Rápida | Zero |
| `tree-sitter` (parse AST) | ~99% | Lenta (parse completo) | Alto |

### Decisão: Cascata de 3 níveis

```
Nível 1: Contagem de extensões → detecta linguagem primária
Nível 2: pygments → valida e resolve ambiguidades (.ts vs .tsx, .js vs .jsx)
Nível 3: tree-sitter → APENAS se nível 1+2 retornarem "unknown" ou score < 60%
```

**Justificativa**: Para 100+ projetos, tree-sitter em todos seria inviável em < 30s. A cascata
garante precisão suficiente com performance adequada.

---

## Debate 3 — Estratégia de Integração com IA (Claude API)

### Questão

Quando acionar o Claude claude-sonnet-4-6 para gerar resumo automático?

### Posições Debatidas

| Trigger | Risco | Custo API |
|---------|-------|-----------|
| README ausente | Seguro | Baixo |
| README presente mas < 50 palavras | Útil | Baixo |
| README > 5000 tokens | Garante relevância do resumo | Médio |
| Sempre (independente do README) | Consistência | Alto |

### Decisão: Threshold duplo

```python
USE_AI_IF = (
    readme_path is None                          # README ausente
    or word_count(readme) < MIN_WORDS            # README muito curto (default: 30 palavras)
    or token_count(readme) > MAX_TOKENS          # README muito extenso (default: 2000 tokens)
)
```

**Configuração via CLI**: `--ai-min-words 30 --ai-max-tokens 2000 --no-ai`  
**Credenciais**: lidas de `.secrets/api_config.json` → nunca hardcoded

---

## Debate 4 — Design do JSON Schema: Flat vs Nested

### Posições

**Opção A — Flat** (todos os campos no nível raiz de cada projeto):
```json
{
  "name": "meu-projeto",
  "language": "Python",
  "git_last_commit": "2026-06-01",
  "git_author": "Yves"
}
```

**Opção B — Nested** (agrupado por domínio):
```json
{
  "name": "meu-projeto",
  "language": {"primary": "Python", "secondary": ["Bash"]},
  "git": {"last_commit": "2026-06-01", "author": "Yves"}
}
```

### Decisão: Nested com grupos semânticos

**Justificativa**: O portfólio será consumido por ferramentas e templates. Nested facilita
seleção de subconjuntos (ex: `project.git.*`) e validação por seção no schema.

**Schema top-level** (definido em `schemas/portfolio-schema-v1.json`):
```json
{
  "generated_at": "ISO-8601",
  "generator_version": "1.0.0",
  "total_projects": 42,
  "projects": [
    {
      "name": "...",
      "path": "...",
      "type": "cli-tool | web-app | library | script | infrastructure | unknown",
      "description": "...",
      "description_source": "readme | ai-generated | filename",
      "language": {
        "primary": "Python",
        "secondary": ["Bash", "YAML"],
        "confidence": 0.92
      },
      "metrics": {
        "file_count": 42,
        "line_count_estimated": 1200,
        "size_bytes": 184320
      },
      "git": {
        "initialized": true,
        "branch": "main",
        "last_commit_hash": "abc123",
        "last_commit_date": "2026-06-01",
        "last_commit_author": "Yves Marinho",
        "commit_count": 87
      },
      "technologies": ["click", "pandas", "docker"],
      "status": "active | archived | unknown",
      "last_modified": "2026-06-01T10:00:00Z"
    }
  ]
}
```

---

## Debate 5 — Estratégia de Tratamento de Erros: Fail-Fast vs Skip-and-Continue

### Questão

O que fazer quando um projeto tem arquivos corrompidos, encoding inválido, ou git history
corrompido?

### Posições

| Estratégia | Comportamento | Trade-off |
|-----------|--------------|-----------|
| Fail-fast | Para o scan e reporta o erro | Seguro para debugging; inviável em produção |
| Skip-and-continue | Pula o projeto problemático, continua os outros | Robusto para 100+ projetos; pode mascarar problemas |
| Partial-data | Inclui o projeto com campos vazios onde falhou | Máxima completude; complexidade de schema (campos nullable) |

### Decisão: Skip-and-continue com bug-report automático

**Justificativa**: Com 100+ projetos heterogêneos (alguns legados, alguns com encoding antigo),
fail-fast seria impraticável. Skip-and-continue garante que um projeto problemático não bloqueie
o portfólio inteiro.

**Implementação**:
```python
def scan_project(path: Path) -> dict | None:
    try:
        return _do_scan(path)
    except Exception as e:
        _write_bug_report(path, e)  # docs/bugs/bug-report-YYYYMMDD-HHmm.md
        return None  # None é filtrado na agregação
```

**Log via Loguru**: Todo skip gera `logger.warning()` com path e exceção.

---

## Debate 6 — Estrutura de Módulos: Flat src/ vs Packages Hierárquicos

### Posições

| Opção | Estrutura | Trade-off |
|-------|-----------|-----------|
| Flat | `src/scanner.py`, `src/extractor.py` | Simples; ruim para crescimento |
| Packages | `src/scanner/__init__.py`, `src/extractor/__init__.py` | Extensível; permite sub-módulos |

### Decisão: Packages por responsabilidade (SOLID — Single Responsibility)

```
src/
├── __init__.py
├── scanner/          # Varredura de diretórios
│   ├── __init__.py
│   └── directory_scanner.py
├── extractor/        # Extração de metadados
│   ├── __init__.py
│   ├── git_extractor.py
│   ├── language_extractor.py
│   └── metrics_extractor.py
├── analyzer/         # Análise de README e descrição
│   ├── __init__.py
│   ├── readme_parser.py
│   └── ai_summarizer.py
├── generator/        # Geração e validação de JSON
│   ├── __init__.py
│   └── portfolio_generator.py
└── cli/              # Interface CLI (click)
    ├── __init__.py
    └── main.py
```

**Factory Pattern**: Cada sub-módulo expõe uma factory function no `__init__.py`:
```python
# src/extractor/__init__.py
def create_extractor(config: dict) -> MetadataExtractor:
    return MetadataExtractor(config)
```

---

## Resumo das Decisões Arquiteturais

| Decisão | Escolha | Razão Principal |
|---------|---------|----------------|
| Processamento | `ProcessPoolExecutor` + throttling | Performance CPU-bound + controle de RAM |
| Detecção de linguagem | Cascata 3 níveis (extensão → pygments → tree-sitter) | Velocidade + precisão adequada |
| Trigger de IA | Threshold duplo (ausente OU < 30 palavras OU > 2000 tokens) | Custo controlado + cobertura máxima |
| JSON Schema | Nested por domínio semântico | Consumibilidade + validação por seção |
| Error handling | Skip-and-continue + bug-report automático | Robustez para 100+ projetos heterogêneos |
| Estrutura de código | Packages por responsabilidade + Factory Pattern | SOLID + extensibilidade futura |

---

**Resultado**: Todas as decisões tomadas. Prontos para gerar a Project Constitution.
