# 📚 Índice — Portfolio Generator

**Projeto**: `portfolio-generator`
**Criado em**: 2026-04-27T15:36:13Z
**Last Updated**: 2026-05-18T21:12:00Z
**Last Session**: 2026-05-18 (Primeira sessão - Concluída)

---

## Documentação Principal

| Arquivo | Descrição |
|---------|-----------|
| [README.md](../README.md) | Documentação pública completa |
| [PROJECT_SPECIFICATION.md](PROJECT_SPECIFICATION.md) | Especificação técnica completa do projeto |
| [TODO.md](TODO.md) | Tarefas pendentes (19 pendentes, 3 concluídas) |
| [TODAY_ACTIVITIES.md](TODAY_ACTIVITIES.md) | Atividades do dia |

## Documentação Técnica

| Pasta | Conteúdo |
|-------|----------|
| [architecture/](architecture/) | Documentação de arquitetura |
| [guides/](guides/) | Guias técnicos |
| [decisions/](decisions/) | Decisões de arquitetura (ADRs) |
| [debates/](debates/) | Debates técnicos |
| [retrospectives/](retrospectives/) | Retrospectivas de sessões |

## Schemas

| Arquivo | Descrição |
|---------|-----------|
| [../schemas/portfolio-schema-v1.json](../schemas/portfolio-schema-v1.json) | Schema JSON para saída do portfolio-gen |
| [../schemas/portfolio-example.json](../schemas/portfolio-example.json) | Exemplo de portfólio gerado |

## Sessões de Trabalho

```
SESSIONS/
└── 2026-05-18/                                    ← Primeira sessão
    ├── SESSION_RECOVERY_2026-05-18.md            (Contexto da sessão)
    └── DAILY_ACTIVITIES_2026-05-18.md            (Log de atividades)
```

### Histórico de Sessões

| Data | Tipo | Duração | Principais Atividades |
|------|------|---------|----------------------|
| 2026-05-18 | Primeira sessão | ~31 min | Ritual session-start-first, análise objetivo-init, especificação completa, GitHub repo, LICENSE, CI/CD, objetivo.yaml atualizado |

---

## Arquivos de Configuração

| Arquivo | Propósito |
|---------|-----------|
| [../.copilot-rules.md](../.copilot-rules.md) | Regras P0 genéricas (symlink) |
| [../.copilot-rules-portfolio-generator.md](../.copilot-rules-portfolio-generator.md) | Regras específicas do projeto |
| [../.vscode/mcp.json](../.vscode/mcp.json) | Configuração MCP (4 servidores) |
| [../objetivo-init.yaml](../objetivo-init.yaml) | Questionário inicial do projeto |
| [../objetivo.yaml](../objetivo.yaml) | Especificação completa (pronto para SpecKit) |
| [../LICENSE](../LICENSE) | Licença MIT |
| [../.github/workflows/ci.yml](../.github/workflows/ci.yml) | Pipeline CI/CD (lint, test, security) |

---

## Ferramentas e Scripts

| Script | Descrição |
|--------|-----------|
| [../scripts/activate-mcp.sh](../scripts/activate-mcp.sh) | Validar e ativar servidores MCP |
| [../scripts/session-index.py](../scripts/session-index.py) | Indexação de documentação de sessões |
| [../scripts/session-time-tracker.py](../scripts/session-time-tracker.py) | Rastreamento de tempo de sessões |
| [../scripts/create_memory_structure.py](../scripts/create_memory_structure.py) | Criar estrutura .memory/ |

---

*Atualizado automaticamente na sessão 2026-05-18*
