---
description: "Task list for portfolio-generator CLI implementation"
---

# Tasks: Portfolio Generator CLI

**Input**: Design documents from `/specs/001-portfolio-gen-spec/`

**Prerequisites**: ✅ spec.md, ✅ plan.md, ✅ research.md, ✅ data-model.md, ✅ contracts/

**Tests**: Incluídos — TDD obrigatório por Constitution Princípio II (test-first).

**Organization**: Tarefas agrupadas por user story para entrega incremental independente.

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Propósito**: Estrutura do projeto, ambiente, ferramentas de qualidade.

- [ ] T001 Criar estrutura de diretórios do projeto: `src/scanner/`, `src/extractor/`, `src/analyzer/`, `src/generator/`, `src/cli/`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`, `schemas/`, `output/`, `logs/`
- [ ] T002 Criar `pyproject.toml` com todas as dependências: click, rich, loguru, pandas, gitpython, pygments, tree-sitter, pyyaml, tomllib, jsonschema, anthropic, chardet, pytest, pytest-cov, black, ruff, mypy, bandit
- [ ] T003 [P] Configurar `Makefile` com targets: `setup`, `test`, `lint`, `run`, `clean`
- [ ] T004 [P] Configurar pre-commit hooks em `.pre-commit-config.yaml`: black, ruff, mypy, bandit
- [ ] T005 [P] Criar `schemas/portfolio-schema-v1.json` baseado no contrato em `contracts/portfolio-schema.md`
- [ ] T006 Criar arquivos `__init__.py` com factory functions em todos os packages `src/*/`
- [ ] T007 [P] Adicionar `output/` e `logs/` ao `.gitignore`
- [ ] T008 Rodar `uv sync` e verificar que `portfolio-gen --help` funciona

**Checkpoint**: `uv run portfolio-gen --help` exibe ajuda. `make lint` roda sem erros.

---

## Phase 2: Fundação (Bloqueante para todos os US)

**Propósito**: Infraestrutura compartilhada que TODAS as user stories dependem.

**⚠️ CRÍTICO**: Nenhum trabalho de user story pode começar até esta fase estar completa.

- [ ] T009 Implementar `src/cli/main.py` com estrutura click: grupo principal `portfolio-gen`, subcomandos `scan`, `validate`, `report` — sem lógica interna ainda (apenas scaffolding com `pass`)
- [ ] T010 Implementar scope guard: `validate_path_scope(path: Path) -> bool` em `src/scanner/directory_scanner.py` — recusa paths fora de `/home/yves_marinho/Documentos/DevOps/`
- [ ] T011 [P] Implementar `src/scanner/directory_scanner.py`: `list_projects(root: Path) -> list[Path]` com filtragem de `.git/`, `node_modules/`, `__pycache__/`, `.venv/`, `tmp/`
- [ ] T012 Implementar logging com loguru: configurar em `src/__init__.py` com DEBUG + INFO handlers; formato com timestamp e módulo
- [ ] T013 [P] Criar fixtures de teste em `tests/fixtures/`: `python_project/` (com README e git), `empty_project/`, `no_git_project/`, `no_readme_project/`, `corrupted_project/`
- [ ] T014 [P] Escrever testes unitários para scope guard e scanner em `tests/unit/test_scanner.py` — devem falhar antes da implementação (TDD)

**Checkpoint**: `make test tests/unit/test_scanner.py` — testes passam. Scope guard rejeita path inválido.

---

## Phase 3: US1 — Generate Complete Portfolio (P1) 🎯 MVP

**Goal**: Usuário executa `portfolio-gen scan` e obtém um arquivo JSON com catálogo completo.

**Independent Test**: Rodar `portfolio-gen scan --path tests/fixtures/` → arquivo JSON gerado com 5 entradas (uma por projeto fixture).

### Testes para US1 (TDD — escrever ANTES, garantir que FALHAM)

- [ ] T015 [P] [US1] `tests/unit/test_language_extractor.py` — testes para cascata 3 níveis: extensão Python detectada, ambiguidade .ts/.tsx resolvida por pygments, "unknown" quando nenhuma extensão reconhecida
- [ ] T016 [P] [US1] `tests/unit/test_git_extractor.py` — git info extraída de fixture com git, None retornado de fixture sem git
- [ ] T017 [P] [US1] `tests/unit/test_metrics_extractor.py` — file_count correto, size_bytes calculado, line_count_estimated razoável
- [ ] T018 [P] [US1] `tests/unit/test_readme_parser.py` — parse de README válido, None para arquivo inexistente, word_count() e token_count() corretos
- [ ] T019 [P] [US1] `tests/unit/test_portfolio_generator.py` — build_portfolio() monta estrutura correta, validate_schema() passa para JSON válido, falha para JSON inválido
- [ ] T020 [US1] `tests/integration/test_scan_flow.py` — scan end-to-end em `tests/fixtures/`: 5 projetos detectados, JSON gerado e válido contra schema

### Implementação de US1

- [ ] T021 [P] [US1] Implementar `src/extractor/language_extractor.py`: cascata 3 níveis (extensão → pygments → tree-sitter); retorna `LanguageInfo(primary, secondary, confidence)`
- [ ] T022 [P] [US1] Implementar `src/extractor/git_extractor.py`: `extract_git_info(path) → GitInfo | None`; try/except em toda operação git; retorna None se não inicializado ou corrompido
- [ ] T023 [P] [US1] Implementar `src/extractor/metrics_extractor.py`: `extract_metrics(path) → ProjectMetrics`; contar arquivos excluindo `.git/`, `node_modules/`, `__pycache__/`, `.venv/`
- [ ] T024 [P] [US1] Implementar `src/analyzer/readme_parser.py`: `parse_readme(path) → str | None`, `word_count(text) → int`, `token_count(text) → int` (estimativa: chars/4)
- [ ] T025 [US1] Implementar `src/extractor/__init__.py`: factory `create_extractor(config) → MetadataExtractor`; `MetadataExtractor.extract(path) → dict` orquestrando language, git, metrics
- [ ] T026 [US1] Implementar `src/generator/portfolio_generator.py`: `build_portfolio(projects, meta) → dict`, `validate_schema(portfolio, schema_path) → bool`, `write_output(portfolio, output_path)`
- [ ] T027 [US1] Implementar lógica principal do `scan` subcommand em `src/cli/main.py`: orchestrar scanner → extractor → analyzer → generator com `ProcessPoolExecutor`; rich progress bar; exit codes corretos
- [ ] T028 [US1] Integrar `scan` subcommand: `--path`, `--output`, `--workers`, `--dry-run`, `--verbose/--quiet`, `--no-ai`, `--ai-min-words`, `--ai-max-tokens` — todos os flags do contrato CLI
- [ ] T029 [US1] Validar que `make test` passa com ≥ 90% de cobertura de branches nos módulos US1

**Checkpoint**: `portfolio-gen scan --path tests/fixtures/ --dry-run` → sumário mostra 5 projetos. `portfolio-gen scan --path tests/fixtures/` → JSON gerado e válido.

---

## Phase 4: US2 — Handle Problem Projects Without Stopping (P2)

**Goal**: Projetos com erros são pulados e reportados; os demais são catalogados normalmente.

**Independent Test**: Scan em fixtures incluindo `corrupted_project/` → 4/5 no JSON, 1 skip reportado, bug-report em `docs/bugs/`.

### Testes para US2 (TDD)

- [ ] T030 [P] [US2] `tests/unit/test_scanner.py` — adicionar testes: `scan_project()` retorna None para `corrupted_project/`, warning logado, bug-report criado
- [ ] T031 [US2] `tests/integration/test_scan_flow.py` — adicionar cenário: scan com projeto corrompido → N-1 projetos no output, execution report com skipped_projects=1

### Implementação de US2

- [ ] T032 [US2] Implementar `scan_project(path) → dict | None` com try/except completo: `None` em qualquer exceção, `logger.warning()` com path e erro
- [ ] T033 [US2] Implementar `_write_bug_report(path, exc) → None` em módulo utilitário: cria `docs/bugs/bug-report-YYYYMMDD-HHmm.md` com path, tipo de erro, stack trace, status OPEN
- [ ] T034 [US2] Adicionar `skipped_projects` ao output final: contagem de None results filtrados
- [ ] T035 [US2] Exibir relatório de execução pós-scan: "Projetos: N catalogados, M pulados" com Rich; avisos para verificar `logs/scan-YYYYMMDD.log`
- [ ] T036 [US2] Implementar exit code 2 quando há projetos pulados (sucesso com avisos) vs exit code 1 (erro crítico)

**Checkpoint**: Scan com `corrupted_project/` fixture → exit code 2, JSON com N-1 projetos, bug-report em `docs/bugs/`.

---

## Phase 5: US3 — Preview Before Writing (P3)

**Goal**: `--dry-run` executa toda a análise sem criar arquivos.

**Independent Test**: `portfolio-gen scan --dry-run` → nenhum arquivo criado em `output/`, sumário exibido no terminal.

### Testes para US3 (TDD)

- [ ] T037 [P] [US3] `tests/integration/test_cli.py` — usar click CliRunner: `portfolio-gen scan --dry-run` → exit 0, nenhum arquivo em `output/`, sumário no stdout

### Implementação de US3

- [ ] T038 [US3] Garantir que `--dry-run` pula `write_output()` e qualquer escrita em disco; execução completa até o ponto de geração do dict
- [ ] T039 [US3] Output do `--dry-run`: exibir sumário Rich com: projetos detectados, projetos que usariam IA, tamanho estimado do JSON, lista de projetos (primeiras 10 linhas)

**Checkpoint**: `portfolio-gen scan --dry-run --verbose` → relatório completo no terminal, zero arquivos criados.

---

## Phase 6: US4 — Validate Existing Catalog (P4)

**Goal**: `portfolio-gen validate <file>` verifica um catálogo existente contra o schema.

**Independent Test**: `validate` em JSON válido → exit 0. `validate` em JSON com campo faltando → exit 1 com localização do erro.

### Testes para US4 (TDD)

- [ ] T040 [P] [US4] `tests/integration/test_cli.py` — adicionar: `validate` em JSON válido → exit 0; `validate` em JSON inválido (campo faltando) → exit 1 com mensagem de erro específica

### Implementação de US4

- [ ] T041 [US4] Implementar subcommand `validate` em `src/cli/main.py`: carregar JSON, validar contra `schemas/portfolio-schema-v1.json`, exibir pass/fail com Rich; `--schema` para schema alternativo
- [ ] T042 [US4] Output de falha de validação: listar cada violação com campo, valor esperado vs encontrado, path no JSON

**Checkpoint**: `portfolio-gen validate output/portfolio-2026-06-17.json` → "✅ Portfolio válido" ou lista de erros.

---

## Phase 7: IA Integration — AI Description Generation (US1 extension)

**Propósito**: Geração de descrições via Anthropic API quando README ausente/inadequado.

> **Dependência**: Requer US1 completo. Pode ser desenvolvido em paralelo a US2/US3/US4.

### Testes para IA (TDD)

- [ ] T043 [P] `tests/unit/test_ai_summarizer.py` — mock do cliente Anthropic: gera descrição quando README ausente, retorna None quando `--no-ai`, retorna None quando API indisponível (exception mockada)

### Implementação de IA

- [ ] T044 Implementar `src/analyzer/ai_summarizer.py`: `generate_summary(project_data, config) → str | None`; lê credenciais de `.secrets/api_config.json`; `--no-ai` retorna None sem chamar API
- [ ] T045 Integrar `ai_summarizer` no fluxo do extractor: verificar threshold duplo (word_count < 30 OU token_count > 2000 OU README ausente) antes de chamar IA
- [ ] T046 Tratar falhas de API graciosamente: exception → description_source = "ai-unavailable", description = ""

**Checkpoint**: Scan de projeto sem README com IA configurada → description_source = "ai-generated" no JSON.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Propósito**: Qualidade, documentação e segurança finais.

- [ ] T047 [P] Rodar `make lint` — zero violações ruff, mypy strict, bandit
- [ ] T048 [P] Verificar cobertura de testes: `pytest --cov=src --cov-report=term-missing` — ≥ 90% em todos os módulos
- [ ] T049 [P] Validar `quickstart.md`: executar todos os comandos da seção "Primeiro uso" do zero e confirmar funcionamento
- [ ] T050 [P] Atualizar `README.md` com: instalação, uso rápido, exemplos de output, lista de dependências
- [ ] T051 Criar ADRs em `docs/architecture/adr/`: ADR-001 (ProcessPoolExecutor vs asyncio), ADR-002 (cascata de detecção de linguagem), ADR-003 (JSON nested vs flat)
- [ ] T052 [P] Security scan final: verificar `.gitignore` inclui `.secrets/`, `output/`, `logs/`; `bandit -r src/` verde; sem credentials hardcoded
- [ ] T053 Teste de carga real: `portfolio-gen scan --path /home/yves_marinho/Documentos/DevOps/` — verificar < 30s, < 512 MB RAM, JSON válido

**Checkpoint Final**: `make test` passa com ≥ 90% cobertura. `make lint` sem violações. Scan real em < 30s.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — iniciar imediatamente
- **Fundação (Phase 2)**: Depende de Phase 1 — BLOQUEIA todas as user stories
- **US1 (Phase 3)**: Depende de Phase 2 — é o MVP completo
- **US2/US3/US4/IA (Phases 4–7)**: Dependem de Phase 2; US1 recomendado primeiro; podem ser paralelas após US1
- **Polish (Phase 8)**: Depende de todas as user stories desejadas

### Parallel Opportunities

- T002, T003, T004, T005, T006, T007 → paralelas (diferentes arquivos)
- T015–T019 → paralelas (diferentes arquivos de teste)
- T021–T024 → paralelas (diferentes extractors)
- Phases 4, 5, 6, 7 → paralelas entre si após Phase 3 completa

### MVP Delivery

1. Completar Phases 1–3 → MVP funcional (US1: Generate Complete Portfolio)
2. `portfolio-gen scan` produz JSON válido → demonstrável ao recrutador
3. Phases 4–8 adicionam robustez, preview, validação, IA

---

## Implementation Strategy

### MVP First

1. Phase 1: Setup → ambiente configurado
2. Phase 2: Fundação → scanner + logging + fixtures
3. Phase 3: US1 → scan completo + JSON gerado
4. **PARAR E VALIDAR**: testar US1 com projetos reais
5. Demo com `portfolio-gen scan --path ~/Documentos/DevOps/`

### Incremental Delivery

- US1 (Phase 3) → MVP básico demonstrável
- + US2 (Phase 4) → robusto para projetos problemáticos
- + US3 (Phase 5) → preview antes de escrever
- + US4 (Phase 6) → validação de catálogos existentes
- + IA (Phase 7) → descrições automáticas para projetos sem README

---

## Notes

- [P] = pode rodar em paralelo (diferentes arquivos, sem dependências entre si)
- [US1/US2/US3/US4] = mapeamento para user story para rastreabilidade
- Cada user story deve ser independentemente testável
- Testes DEVEM ser escritos antes da implementação e falhar primeiro (TDD)
- Commitar após cada task ou grupo lógico concluído
- Parar em cada Checkpoint para validar a user story independentemente
