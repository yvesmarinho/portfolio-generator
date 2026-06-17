# Research: Portfolio Generator CLI

**Created**: 2026-06-17  
**Feature**: [spec.md](spec.md)  
**Source**: objetivo-init.yaml + architecture debate (docs/debates/architecture-debate-portfolio-generator.md)

---

## Decisão 1 — Modelo de Processamento Paralelo

**Decision**: `concurrent.futures.ProcessPoolExecutor` com `max_workers=min(4, os.cpu_count())`

**Rationale**: A tarefa é CPU-bound (contagem de arquivos, parsing) + I/O-bound (leitura de muitos
arquivos). ProcessPoolExecutor contorna o GIL Python. Workers configuráveis via `--workers N` permitem
throttling para não sobrecarregar o sistema durante análise de 1–10 GB de projetos.

**Alternatives considered**:
- `asyncio` + `aiofiles` — rejeitado: overhead para I/O em filesystem local; não contorna GIL para CPU-bound
- Threading — rejeitado: GIL impede paralelismo real para CPU-bound
- Sequential loop — rejeitado: inviável para 100+ projetos com meta de < 30s

---

## Decisão 2 — Estratégia de Detecção de Linguagem

**Decision**: Cascata de 3 níveis:
1. Contagem de extensões (`.py`, `.js`, `.go`, etc.) → linguagem primária
2. `pygments.lexers.guess_lexer_for_filename()` → validação e resolução de ambiguidades
3. `tree-sitter` parse → SOMENTE se níveis 1+2 retornarem "unknown" ou score < 60%

**Rationale**: Para 100+ projetos, tree-sitter em todos seria inviável em < 30s. Nível 1 resolve
~85% dos casos com zero overhead. Nível 2 resolve ~90%+. Tree-sitter fica como fallback de alta
precisão (~99%) para casos ambíguos.

**Alternatives considered**:
- tree-sitter em todos os projetos — rejeitado: muito lento para o volume alvo
- Apenas extensões — rejeitado: baixa precisão para linguagens compartilhando extensões

---

## Decisão 3 — Trigger de Integração com IA

**Decision**: Threshold duplo:
```python
USE_AI = (
    readme_path is None            # README ausente
    or word_count(readme) < 30     # README muito curto (configurável: --ai-min-words)
    or token_count(readme) > 2000  # README muito extenso (configurável: --ai-max-tokens)
)
```

**Rationale**: Cobre os três cenários que justificam custo de API: ausência total, presença mas
inútil (< 30 palavras), e README longo demais para usar diretamente no portfólio.
`--no-ai` desativa completamente para uso offline ou sem créditos.

**Alternatives considered**:
- Sempre usar IA — rejeitado: custo alto; maioria dos projetos tem README adequado
- Apenas quando ausente — rejeitado: ignora READMEs curtos ou excessivamente longos

---

## Decisão 4 — Estrutura do JSON de Saída

**Decision**: Nested por domínio semântico (ver contrato em [contracts/portfolio-schema.md](contracts/portfolio-schema.md))

```json
{
  "generated_at": "ISO-8601",
  "generator_version": "1.0.0",
  "total_projects": 42,
  "projects": [
    {
      "name": "...",
      "language": {"primary": "Python", "secondary": [], "confidence": 0.92},
      "metrics": {"file_count": 42, "line_count_estimated": 1200, "size_bytes": 184320},
      "git": {"initialized": true, "last_commit_date": "2026-06-01", ...}
    }
  ]
}
```

**Rationale**: Nested facilita seleção de subconjuntos (`project.git.*`), validação por seção
no schema, e extensibilidade futura sem quebrar consumidores existentes.

**Alternatives considered**:
- Flat (todos os campos no nível raiz) — rejeitado: dificulta validação por seção; prejudica legibilidade

---

## Decisão 5 — Tratamento de Erros

**Decision**: Skip-and-continue com bug-report automático:
- `scan_project()` retorna `None` em qualquer exceção
- `logger.warning()` com path e tipo de erro
- Bug-report salvo em `docs/bugs/bug-report-YYYYMMDD-HHmm.md`
- Relatório de execução inclui contagem de projetos processados vs pulados

**Rationale**: Com 100+ projetos heterogêneos (alguns legados, encoding antigo, git corrompido),
fail-fast seria inviável. Skip-and-continue garante que 1 projeto problemático não bloqueie o
portfólio inteiro.

**Alternatives considered**:
- Fail-fast — rejeitado: inviável em produção com 100+ projetos
- Partial-data (incluir projeto com campos vazios) — rejeitado: complica schema (campos nullable)

---

## Decisão 6 — Estrutura de Módulos

**Decision**: Packages por responsabilidade + Factory Pattern

**Rationale**: SOLID Single Responsibility Principle. Cada package é independentemente testável.
Factory functions em `__init__.py` permitem injeção de dependências e mocking nos testes.

**Alternatives considered**:
- Flat (`src/scanner.py`) — rejeitado: não escala; sem separação clara de responsabilidades

---

## Dependências — Análise de Risco

| Dependência | Risco | Mitigação |
|------------|-------|----------|
| `anthropic` | API externa; custo por uso | `--no-ai` flag; cache de resultados (futuro) |
| `tree-sitter` | Build nativo (C extension) | Fallback para pygments se import falhar |
| `gitpython` | Repositórios git corrompidos | try/except; retorna None em erro |
| `pandas` | Overhead de import (~200ms) | Lazy import; usado apenas na agregação final |

---

**Conclusão**: Sem NEEDS CLARIFICATION. Todos os pontos resolvidos. Pronto para Phase 1 Design.
