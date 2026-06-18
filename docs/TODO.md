# 📝 TODO — Portfolio Generator

**Last Updated**: 2026-06-18 — Sessão 2026-06-18 ✅ Concluída
**Status**: 🟢 Em andamento — 8 phases implementadas, produção funcional

---

## ✅ Concluído (todas as 8 phases implementadas)

- [x] **Phase 1**: Scanner de Diretórios (`src/scanner/`) — detecção por `.portfolio-project`
- [x] **Phase 2**: Extratores (`src/extractor/`) — git, language, metrics, readme_parser
- [x] **Phase 3**: CLI MVP (`portfolio-gen scan`) — scan + output JSON
- [x] **Phase 4**: US2 — tratamento robusto de projetos problemáticos (bug reports)
- [x] **Phase 5**: US3 — dry-run com sumário enriquecido
- [x] **Phase 6**: US4 — subcomando `validate` + `report` implementado
- [x] **Phase 7**: Integração IA — `ai_summarizer.py` via Anthropic API
- [x] **Phase 8**: Polish — cobertura 96%, ADRs, quickstart

---

## 🟠 Pendente — Melhorias de UX e Produção

- [ ] **UX-01**: Testes de produção completos após `init` correto
  - Prioridade: P0
  - Ação: executar `portfolio-gen init` na pasta DevOps completa com novo UX ([r]=entrar)
  - Depois: `portfolio-gen scan --no-ai --dry-run` para validar detecção

- [ ] **UX-02**: Subcomando `init` — mostrar indicador de progresso (quantas pastas visitadas)
  - Prioridade: P2

- [ ] **UX-03**: Subcomando `report` — adicionar coluna de descrição curta (--verbose)
  - Prioridade: P2

- [ ] **INFRA-01**: `config/scan-exclusions.json` — revisar lista e adicionar pastas problemáticas
  - Prioridade: P1
  - Contexto: `enterprise-python-analysis/.secrets/clients/` ainda causa PermissionError no `language_extractor`
  - Ação: melhorar `language_extractor` para capturar PermissionError interno por arquivo

- [ ] **INFRA-02**: GitHub Actions CI — verificar se pipeline está passando em `001-portfolio-gen-spec`
  - Prioridade: P1

- [ ] **DOC-01**: Atualizar `README.md` com instruções do `init` + novo fluxo de marcação
  - Prioridade: P2

---

## 🔵 Backlog — Futuro

- [ ] **FEAT-01**: Subcomando `init --reset` — remover todos os markers e recomeçar
- [ ] **FEAT-02**: Subcomando `scan --path Vya-Jobs/` — scan parcial de subárvore
- [ ] **FEAT-03**: Portfolio em HTML/markdown além de JSON
- [ ] **FEAT-04**: Integração com GitHub API para complementar metadados
- [ ] **FEAT-05**: Modo watch — re-scan automático quando projetos mudam

---

## 📊 Estado Atual

| Métrica | Valor |
|---------|-------|
| Testes | 240 passando |
| Cobertura | 96% |
| Projetos detectados (produção) | 55 |
| Lint/Type | ruff ✅ / mypy ✅ |
| Branch | `001-portfolio-gen-spec` |
