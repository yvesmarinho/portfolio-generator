# Implementation Plan: Portfolio Generator CLI

**Branch**: `001-portfolio-gen-spec` | **Date**: 2026-06-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-portfolio-gen-spec/spec.md`

---

## Summary

Build a CLI tool (`portfolio-gen`) que escaneia um diretório de projetos DevOps, extrai
metadados estruturados de cada projeto (linguagem, métricas, git info, descrição) e produz
um catálogo JSON validado. O tool processa 100+ projetos via workers paralelos, trata erros
com skip-and-continue, e opcionalmente usa IA para gerar descrições de projetos sem README adequado.

---

## Technical Context

**Language/Version**: Python 3.12+ (type hints modernos, `match` statements, `tomllib` stdlib)

**Primary Dependencies**:
- `click` — CLI subcommands, options, validação de argumentos
- `rich` — progress bars, tabelas, output colorido
- `loguru` — logging estruturado (DEBUG: fluxo de dados, INFO: progresso)
- `pandas` — agregação e filtragem de metadados
- `gitpython` — extração de metadados de controle de versão
- `pygments` — detecção de linguagem por conteúdo de arquivo
- `tree-sitter` — detecção por AST (fallback, nível 3 da cascata)
- `pyyaml` — leitura de YAML de projetos analisados
- `tomllib` — leitura de `pyproject.toml` dos projetos
- `jsonschema` — validação do output contra `schemas/portfolio-schema-v1.json`
- `anthropic` — geração de descrição via IA (opcional; lê key de `.secrets/api_config.json`)
- `chardet` — detecção de encoding para arquivos não-UTF-8

**Storage**: JSON em `output/portfolio-YYYY-MM-DD.json`; logs em `logs/scan-YYYYMMDD.log`

**Testing**: `pytest` + `pytest-cov` (90%+ cobertura de branches); `tmp_path` para fixtures de filesystem

**Target Platform**: Linux (máquina local, single-user); Python 3.12+; `uv` para gestão de env

**Project Type**: CLI tool

**Performance Goals**:
- Scan de 100 projetos em < 30 segundos (meta: < 10s)
- 1 projeto processado em < 2 segundos com todos os metadados
- RAM < 512 MB durante scan completo

**Constraints**:
- Processar SOMENTE `/home/yves_marinho/Documentos/DevOps/` — validado em runtime antes de qualquer leitura
- Credenciais SOMENTE em `.secrets/api_config.json` — nunca hardcoded
- `--workers N` default: `min(4, os.cpu_count())`

**Scale/Scope**: 100–500 projetos em disco; output JSON < 5 MB

---

## Constitution Check

*GATE: Deve passar antes da Fase 0. Re-verificado após Fase 1.*

| Princípio | Gate | Status |
|-----------|------|--------|
| I. Modular Architecture | packages por responsabilidade; Factory Pattern; máx 300 linhas/arquivo | ✅ PASS — 5 packages (scanner/extractor/analyzer/generator/cli), cada um com factory em `__init__.py` |
| II. Test-First (90%+) | TDD; pytest; 90%+ cobertura de branches; testes de integração | ✅ PASS — plano de testes definido na fase de tasks; fixtures via `tmp_path` |
| III. Security by Default | .secrets/ only; sem curl com credenciais; bandit em CI | ✅ PASS — API key de `.secrets/api_config.json`; scope guard valida path antes de qualquer leitura |
| IV. Performance Contracts | < 30s/100 projetos; < 512 MB RAM; workers configuráveis | ✅ PASS — ProcessPoolExecutor com max_workers; throttling via --workers flag |
| V. Graceful Degradation | skip-and-continue; bug-report; loguru WARNING | ✅ PASS — `scan_project()` retorna None em erro; bug-report gerado em `docs/bugs/` |
| VI. CLI-First UX | click; rich; --dry-run; --verbose/--quiet; help com exemplos | ✅ PASS — 3 subcomandos: `scan`, `validate`, `report`; todos com --dry-run e --verbose |

**Constitution Gate: ✅ APROVADO — sem violações. Prosseguindo para Fase 0.**

---

## Project Structure

### Documentation (this feature)

```text
specs/001-portfolio-gen-spec/
├── spec.md              ← especificação da feature
├── plan.md              ← este arquivo
├── research.md          ← Fase 0: decisões e racional
├── data-model.md        ← Fase 1: design do schema de entidades
├── quickstart.md        ← Fase 1: quick-start para desenvolvedores
├── checklists/
│   └── requirements.md  ← checklist de qualidade da spec
└── contracts/
    ├── cli-schema.md    ← contrato da interface CLI
    └── portfolio-schema.md ← contrato do schema JSON de saída
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── scanner/
│   ├── __init__.py               ← factory: create_scanner(config) → DirectoryScanner
│   └── directory_scanner.py      ← scan_directory(), list_projects(), filter_excluded()
├── extractor/
│   ├── __init__.py               ← factory: create_extractor(config) → MetadataExtractor
│   ├── git_extractor.py          ← extract_git_info(path) → GitInfo | None
│   ├── language_extractor.py     ← detect_language(path) → LanguageInfo (cascata 3 níveis)
│   └── metrics_extractor.py      ← extract_metrics(path) → ProjectMetrics
├── analyzer/
│   ├── __init__.py               ← factory: create_analyzer(config) → ProjectAnalyzer
│   ├── readme_parser.py          ← parse_readme(path) → str | None; word_count(); token_count()
│   └── ai_summarizer.py          ← generate_summary(project_data) → str | None
├── generator/
│   ├── __init__.py               ← factory: create_generator(config) → PortfolioGenerator
│   └── portfolio_generator.py    ← build_portfolio(projects) → dict; validate_schema(portfolio)
└── cli/
    ├── __init__.py
    └── main.py                   ← click app: portfolio-gen scan | validate | report

schemas/
└── portfolio-schema-v1.json      ← JSON schema para validação do output

tests/
├── unit/
│   ├── test_scanner.py
│   ├── test_language_extractor.py
│   ├── test_git_extractor.py
│   ├── test_metrics_extractor.py
│   ├── test_readme_parser.py
│   ├── test_ai_summarizer.py
│   └── test_portfolio_generator.py
├── integration/
│   ├── test_scan_flow.py         ← scan → extract → generate end-to-end
│   └── test_cli.py               ← click runner tests
└── fixtures/
    ├── python_project/           ← projeto Python fake para testes
    ├── empty_project/            ← diretório vazio (edge case)
    ├── no_git_project/           ← projeto sem git
    ├── no_readme_project/        ← projeto sem README
    └── corrupted_project/        ← arquivos intencionalmente quebrados

output/                           ← portfolios gerados (gitignored)
logs/                             ← scan logs (gitignored)
```

**Structure Decision**: Packages por responsabilidade (CLI tool — opção 1), alinhado com
SOLID Single Responsibility Principle e Princípio I da Constitution.

---

## Complexity Tracking

*Sem violações da constitution que precisem de justificativa.*

---

## Phase 0: Research Findings

*Ver [research.md](research.md) para detalhes completos.*

Todos os pontos técnicos foram resolvidos via `objetivo-init.yaml` e debate de arquitetura
(`docs/debates/architecture-debate-portfolio-generator.md`). Sem marcadores NEEDS CLARIFICATION.

**Decisões chave**:
- Modelo de processamento: `ProcessPoolExecutor` (paralelismo CPU-bound + throttling) — Debate 1
- Detecção de linguagem: cascata 3 níveis (extensão → pygments → tree-sitter) — Debate 2
- Trigger de IA: threshold duplo (ausente OU < 30 palavras OU > 2000 tokens) — Debate 3
- Estrutura JSON: nested por domínio semântico — Debate 4
- Tratamento de erros: skip-and-continue + bug-report automático — Debate 5
- Estrutura de módulos: packages por responsabilidade + Factory Pattern — Debate 6

---

## Phase 1: Design Artifacts

*Ver [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md).*

### Data Flow

```
CLI (click)
  └─ subcomando: scan
       ├─ DirectoryScanner.list_projects(root_path)
       │    └─ [Path, ...] — 1 por projeto válido
       │
       └─ ProcessPoolExecutor (max_workers configurável)
            └─ por projeto (paralelo):
                 ├─ MetadataExtractor
                 │    ├─ LanguageExtractor.detect() → LanguageInfo
                 │    ├─ GitExtractor.extract() → GitInfo | None
                 │    └─ MetricsExtractor.extract() → ProjectMetrics
                 │
                 ├─ ProjectAnalyzer
                 │    ├─ ReadmeParser.parse() → str | None
                 │    └─ AISummarizer.generate() → str | None  (condicional)
                 │
                 └─ ProjectEntry (dict montado)
                      │
            PortfolioGenerator
                 ├─ build_portfolio([ProjectEntry, ...]) → dict
                 ├─ validate_schema(portfolio) → bool
                 └─ write_output(portfolio, output_path)
```

### Error Handling Flow

```python
def scan_project(path: Path) -> dict | None:
    try:
        return _build_project_entry(path)
    except Exception as e:
        logger.warning(f"Skipping {path.name}: {e}")
        _write_bug_report(path, e)  # → docs/bugs/bug-report-YYYYMMDD-HHmm.md
        return None

# Na agregação:
results = [r for r in parallel_results if r is not None]
```

---

## Extension Hooks

**Optional Hook**: git
Command: `/speckit-git-commit`
Description: Auto-commit após planejamento de implementação
Prompt: Commit plan changes?
To execute: `/speckit-git-commit`

**Optional Hook**: agent-context
Command: `/speckit-agent-context-update`
Description: Atualizar contexto do agente após planejamento
Prompt: Execute speckit.agent-context.update?
To execute: `/speckit-agent-context-update`
