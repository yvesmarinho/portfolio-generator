# 📝 TODO — Portfolio Generator

**Last Updated**: 2026-06-17T00:00:00Z
**Status**: 🟢 Em andamento

---

## 🟠 Em Progresso

- [ ] **DEV-Phase3**: Implementar Phase 3 — US1: Generate Complete Portfolio (MVP)
  - T015–T029: Extractors (language, git, metrics), readme_parser, portfolio_generator, scan CLI

## 🔵 Pendente - SpecKit Workflow

- [x] **SPEC-02**: Executar `speckit.specify` para gerar spec.md (2026-06-17)
  - Resultado: `specs/001-portfolio-gen-spec/spec.md` — 4 user stories, 16 FR, 8 SC
  - Checklist: `specs/001-portfolio-gen-spec/checklists/requirements.md` — ✅ PASSOU

- [x] **SPEC-03**: Executar `speckit.plan` para gerar plano de implementação (2026-06-17)
  - Resultado: `specs/001-portfolio-gen-spec/plan.md` + `research.md` + `contracts/` + `quickstart.md`
  - Constitution Check: ✅ APROVADO — 6/6 princípios satisfeitos

- [x] **SPEC-04**: Executar `speckit.tasks` para gerar tarefas detalhadas (2026-06-17)
  - Resultado: `specs/001-portfolio-gen-spec/tasks.md` — 53 tasks em 8 phases, organizadas por US

- [ ] **SPEC-05**: Executar `speckit.validate` para validação de qualidade
  - Prioridade: P1
  - Dependência: SPEC-04

## 🔵 Pendente - Implementação

- [ ] **DEV-01**: Implementar Scanner de Diretórios (MVP Feature #1)
  - Prioridade: P0
  - Dependência: SPEC-04
  - Componente: `src/core/scanner.py`

- [ ] **DEV-02**: Implementar Extrator de Metadados (MVP Feature #2)
  - Prioridade: P0
  - Dependência: DEV-01
  - Componente: `src/core/extractor.py`

- [ ] **DEV-03**: Implementar Analisador de README (MVP Feature #3)
  - Prioridade: P0
  - Dependência: DEV-02
  - Componente: `src/core/analyzer.py`

- [ ] **DEV-04**: Implementar Gerador de JSON (MVP Feature #4)
  - Prioridade: P0
  - Dependência: DEV-03
  - Componente: `src/core/generator.py`

- [ ] **DEV-05**: Implementar CLI Interativo (MVP Feature #5)
  - Prioridade: P0
  - Dependência: DEV-04
  - Componente: `src/api/cli.py`

## 🔵 Pendente - Testes e Qualidade

- [ ] **TEST-01**: Criar suite de testes unitários (cobertura ≥90%)
  - Prioridade: P0
  - Dependência: DEV-05

- [ ] **TEST-02**: Teste de integração com caso de uso real
  - Prioridade: P1
  - Target: `/home/yves_marinho/Documentos/DevOps/Vya-Jobs/enterprise-python-snippets`

- [ ] **DOC-01**: Documentar APIs e módulos
  - Prioridade: P1
  - Google Style docstrings obrigatório

- [ ] **DOC-02**: Criar guia de usuário para portfolio-gen CLI
  - Prioridade: P1

## 🔵 Pendente - Infraestrutura

- [ ] **INFRA-01**: Criar `pyproject.toml` com dependências
  - Prioridade: P0
  - Stack: uv + ruff + pytest + click + loguru + rich + pandas + gitpython

- [ ] **INFRA-02**: Configurar pre-commit hooks (ruff, mypy)
  - Prioridade: P1

## ✅ Concluído (Phase 2 — 2026-06-17)

- [x] **DEV-Phase1**: Phase 1 Setup completo (2026-06-17) — commit bb6a3d0
  - `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `schemas/portfolio-schema-v1.json`
  - Factory `__init__.py` para scanner/extractor/analyzer/generator
  - CLI stub `portfolio-gen --help` funcionando, ruff+mypy+bandit verdes

- [x] **DEV-Phase2**: Phase 2 Fundação completa (2026-06-17)
  - T009: CLI atualizado com `--verbose/-v` no grupo + `configure_logging()` 
  - T010: `validate_path_scope()` — scope guard de segurança (scope: `/home/yves_marinho/Documentos/DevOps/`)
  - T011: `DirectoryScanner.list_projects()` — filtra `.git`, `node_modules`, `__pycache__`, `.venv`, `tmp`
  - T012: `src/cli/_logging.py` — loguru com handler de arquivo (DEBUG) + stderr (INFO/DEBUG)
  - T013: Fixtures `no_git_project` + `scan_target` adicionadas ao conftest
  - T014 TDD: 26 testes em `tests/unit/test_scanner.py` — todos passando

## ✅ Concluído (histórico)

- [x] **SETUP-01**: Scaffold inicial gerado (2026-05-18T12:29:00Z)
- [x] **SETUP-02**: Ritual de primeira sessão completado (2026-05-18T20:43:00Z)
  - Ambiente virtual Python criado (.venv/)
  - MCP configurado e validado (4 servidores)
  - Git inicializado
  - Session-index e session-time inicializados
  - Memory system criado (.memory/)
  - Regras Copilot carregadas

- [x] **SPEC-01b**: Architecture debate documentado (2026-06-17)
  - Resultado: `docs/debates/architecture-debate-portfolio-generator.md` — 6 debates, decisões tomadas

- [x] **SPEC-01c**: Project Constitution criada (2026-06-17)
  - Resultado: `.specify/memory/constitution.md` — v1.0.0, 6 princípios, governance definida

- [x] **SPEC-01**: Atualizar `objetivo.yaml` com decisões do questionário (2026-05-18T21:11:00Z)
  - Especificação completa implementada
  - Backup criado (objetivo.yaml.bkp.20260518_201126)
  - Commit: e6febca
  - Referência: [docs/PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md)

- [x] **INFRA-03**: Adicionar CI/CD básico (GitHub Actions) (2026-05-18T20:55:00Z)
  - Workflow .github/workflows/ci.yml criado
  - Jobs: lint (ruff), test (pytest), security (bandit)
  - Python 3.12 e 3.13
  - Commit: e6febca
  - Scan de segurança: 🟢 LIMPO
- [x] **SPEC-00**: Análise de objetivo-init.yaml concluída (2026-05-18T12:30:00Z)
  - Questionário respondido
  - Decisões técnicas documentadas
  - Especificação consolidada em PROJECT_SPECIFICATION.md
- [x] **BUG-01**: Corrigido activate-mcp.sh regex que quebrava URLs (2026-05-18T17:38:00Z)

---

## 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Total de tarefas | 22 |
| Concluídas | 4 (18%) |
| Em progresso | 1 (5%) |
| Pendentes | 17 (77%) |
| Prioridade P0 | 10 |
| Prioridade P1 | 7 |
| Prioridade P2 | 1 |

---

**Convenções**:
- **P0**: Crítico / Bloqueante
- **P1**: Importante / Necessário para MVP
- **P2**: Melhoria / Nice to have
