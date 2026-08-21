<!-- Criado em: 21/08/2026 12:52 -->
<!-- Modificado em: 21/08/2026 12:53 -->

# Relatório — Revisão das Descrições de Projetos (portfolio-generator)

**Sessão**: 2026-08-21
**Branch**: `001-portfolio-gen-spec`
**Escopo**: revisão de conteúdo das 55 descrições em `output/portfolio-2026-06-18.json` + correção da causa raiz no parser + geração de `output/portfolio-2026-06-18-revisado.json`

---

## Resumo

| Métrica | Valor |
|---|---|
| Projetos no scan original | 55 |
| Projetos removidos (não existem mais no disco) | 3 |
| Projetos no output revisado | 52 |
| Descrições corrigidas pelo parser (`extract_description`) | 6 |
| Descrições regeneradas manualmente (README/estrutura sem conteúdo útil) | 5 |
| `description_source` normalizado (`generated` → `ai-generated`, descrição mantida) | 7 |
| Descrições sem mudança | 34 |
| Testes novos adicionados | 7 (todos passando) |
| Validação do schema | ✅ `portfolio-gen validate` passou |

---

## 1. Causa raiz corrigida no código

`src/analyzer/readme_parser.py::extract_description()` pegava o primeiro "parágrafo" do README sem filtrar:
- linhas de badges/shields markdown (`[![...]](...)`, `![...]`)
- blocos de código (` ``` `)
- cabeçalhos de metadados (`**Version**: 1.0.0`, `> **Última atualização:** ...`)

Isso fazia com que READMEs bem escritos gerassem descrições poluídas com lixo markdown. Corrigido com três novos filtros de linha, mantendo a lógica original de "primeiro parágrafo real". 7 novos testes cobrindo os casos (badges isolados, múltiplos badges, bloco de código, metadados com dois-pontos dentro/fora do negrito, e o caso negativo — frase inteira em negrito que **não** deve ser tratada como metadado).

Nenhuma mudança de schema foi necessária: `description_source: "ai-generated"` já era o valor correto no código atual (`metadata_extractor.py:188`); o valor `"generated"` no output antigo era de uma versão anterior do gerador.

## 2. Projetos removidos do portfólio revisado

Não encontrados no disco durante a revisão (busca por variações de nome também não encontrou realocação):

| Projeto | Caminho original |
|---|---|
| `Cognitive-Speech-TTS` | `Projetos/Cognitive-Speech-TTS` |
| `knowledge-lab` | `Projetos/knowledge-lab` |
| `pmm-dev` | `Projetos/pmm-dev` |

**Ação recomendada**: rodar `portfolio-gen scan` novamente para capturar o estado atual real do diretório `~/Documentos/DevOps` — este relatório trabalhou em cima de um scan de 2026-06-18, hoje desatualizado em pelo menos esses 3 casos.

## 3. Descrições corrigidas pelo parser (Fila 1)

| Projeto | Antes | Depois |
|---|---|---|
| `ai-local-setup` | badges markdown | `> Projeto para configuração de IDE Code para utilizar Continue e Ollama` |
| `cmdb-platform` | badges markdown | `> Configuration Management Database (CMDB) with Service→ServiceComponent architecture...` |
| `enterprise-database-docker` | frase real + linha de status grudada | frase real isolada |
| `enterprise-kubernets` | `**Version**: 1.0.0 **Status**:...` | `Comprehensive audit and validation system for K8S clusters...` |
| `enterprise-observability-dashboards` | `> **Última atualização:**...` | `> Sistema enterprise de templates de dashboards Grafana...` |
| `enterprise-python-n8n-collector` | badges markdown | `> **Coletor empresarial de métricas** para N8N...` |

## 4. Descrições regeneradas manualmente — Claude (Fila 2, README sem conteúdo útil)

Nestes casos o README não tinha parágrafo descritivo real (só comando de terminal, bloco de diretrizes internas, ou frase genérica demais). Escritas com base em estrutura de arquivos, código-fonte e, quando disponível, `graphify-out/GRAPH_REPORT.md` (god nodes/comunidades) do próprio projeto:

| Projeto | Graphify usado | Antes | Depois |
|---|---|---|---|
| `code-snippet` | ✅ (Flask-AppBuilder: Snippets, Categories, Languages) | `Projeto concluído.` | API Flask para snippets de código por categoria/linguagem |
| `synch_folder` | ✅ (ChangeHandler, sync_file(), backup_and_upload()) | `ssh-keygen -t rsa...` | Utilitário de sincronização/backup de pastas via watchdog |
| `enterprise-docker` | — | `Docker projects` | Catálogo de configs Docker Swarm para serviços internos |
| `enterprise-observability` | — | lista de bullets técnicos | Stack de observabilidade enterprise (logs/métricas/dashboards) |
| `enterprise-pgbounc-dynamic-setup` | — | bloco de aviso "NUNCA EXECUTAR..." | Automação de setup dinâmico de PgBouncer |

## 5. `description_source` normalizado, descrição mantida (Fila 2b)

Nestes 7, a descrição **já existente** (gerada por uma versão anterior do `ai_summarizer`, `source="generated"`) já era tecnicamente precisa e não precisava ser reescrita — só o rótulo do campo `description_source` foi corrigido para `"ai-generated"` (valor válido no schema atual):

`arduino`, `domotica`, `wifi-qrcode-generator`, `yvesmarinho_git_profile`, `enterprise-insurance`, `enterprise-kubernets-operation`, `modelos_variados`.

## 6. Achados adicionais (fora do escopo desta revisão, registrar para o TODO)

- `wifi-qrcode-generator` tem o README nomeado `READE.md` (typo) — não é reconhecido por `README_NAMES` em `readme_parser.py`, então o parser nunca o lê; a descrição boa vinha só da IA. Vale considerar um fallback mais tolerante a typos comuns, ou renomear o arquivo na origem.
- `enterprise-kubernets-operation` usa `CLUSTER_README.md`/`START_HERE.md` em vez de `README.md` — mesmo problema de nomenclatura não padrão.
- `report --format table/csv` continua sem exibir a coluna `description` (item UX-03 do TODO, não tratado aqui).

## 7. Arquivos gerados/alterados nesta sessão

- `src/analyzer/readme_parser.py` — filtro de badges/fences/metadados em `extract_description()`
- `tests/unit/test_readme_parser.py` — 7 testes novos
- `output/portfolio-2026-06-18-revisado.json` — portfólio revisado (52 projetos, válido contra o schema)
- Este relatório

Nada foi commitado — segue em stage/working tree conforme pedido na sessão.
