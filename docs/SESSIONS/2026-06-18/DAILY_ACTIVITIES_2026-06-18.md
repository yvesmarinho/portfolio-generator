# 📅 Daily Activities — 2026-06-18

**Projeto**: portfolio-generator
**Branch**: `001-portfolio-gen-spec`
**Sessão iniciada**: 2026-06-18

---

### Início de Sessão — Ritual de Session Start

**~00:00 — ✅ COMPLETO**

**Objetivo**: Executar ritual de início de sessão recorrente
**Contexto**: Sessão anterior (2026-05-18) concluída com scaffold e especificação. Retomando implementação.
**Passos executados**:
1. Verificação MCP config (`.vscode/mcp.json`) — memory ✅ + sequential-thinking ✅
2. Recuperação de contexto via `docs/TODO.md` e `SESSION_RECOVERY_2026-05-18.md`
3. Scan de segurança — `.secrets/` no gitignore, pre-commit hook ativo
4. `git status` + `git log --oneline -5` executados
5. Documentos de sessão criados

**Resultado**: Sessão iniciada com contexto recuperado — 17 tarefas P0/P1 pendentes

**Status**: ✅ Completo

---

### Scanner com Arquivo Marcador + Subcomando `init`

**~10:00 — ✅ COMPLETO**

**Objetivo**: Substituir heurística de detecção de projetos por arquivo marcador `.portfolio-project`, criar `portfolio-gen init` interativo e corrigir PermissionError em `.secrets/`

**Contexto**: O scanner tratava pastas-container (`Vya-Jobs/`, `Projetos/`) como projetos individuais. Solução: somente diretórios marcados com `.portfolio-project` são projetos.

**Passos executados**:
1. Reescrita de `src/scanner/directory_scanner.py` — removido `_is_project_root()` heurístico, adicionado `MARKER_FILE`, `_scan_recursive()` com parada em marcadores
2. Adicionado `.secrets` ao `DEFAULT_EXCLUDED` para evitar PermissionError
3. Implementado `portfolio-gen init` em `src/cli/main.py` com opções `[y/n/s/e]`
4. Adicionado `_load_exclusions()` / `_save_exclusion()` — opção `[e]` persiste em `config/scan-exclusions.json`
5. Atualizado `tests/conftest.py` — fixtures com `.portfolio-project` em vez de `.git/`
6. Adicionados testes `TestDirectoryScannerMarkerDetection` com 5 novos casos

**Resultado**: 240 testes passando, cobertura 96%

**Artefatos modificados**:
| Arquivo | O que mudou |
|---------|-------------|
| `src/scanner/directory_scanner.py` | Detecção por marcador `.portfolio-project` |
| `src/cli/main.py` | Subcomando `init` com [y/r/s/e], `_load_exclusions`, `_save_exclusion` |
| `tests/conftest.py` | Fixtures com `.portfolio-project` |
| `tests/unit/test_scanner.py` | Testes de detecção por marcador |

**Commits**: `2123d1e`, `e1b8288`

**Status**: ✅ Completo

---

### Correção de UX do `init` + Logging

**~15:00 — ✅ COMPLETO**

**Objetivo**: Corrigir UX confusa do `init` após análise de log de produção revelar markers incorretos em pastas-container

**Contexto**: Usuário executou `init` e pressionou `[y]` para `Projetos/` e `Vya-Jobs/`, marcando-as como projetos únicos. O scan então processou cada container como um projeto, causando PermissionError em `.secrets/` dentro de `Vya-Jobs/`. O log não mostrava nenhuma informação de progresso.

**Problemas identificados**:
- `[n]` significava "recursionar" mas o nome sugeria "não" — confuso
- Markers criados incorretamente em 9 pastas-container de produção
- `init` não produzia nenhuma linha de log (usava só `console.print`)
- `scan` não logava início, quantidade de projetos, conclusão
- `ProcessPoolExecutor` com `fork` sem `enqueue=True` = escritas concorrentes inseguras

**Passos executados**:
1. Removidos 9 markers `.portfolio-project` incorretos das pastas-container
2. Trocado `[n]` → `[r]` ("entrar e buscar sub-projetos") com default=`r`
3. Adicionado `logger.info/debug` em cada ação do `init`
4. Redesenhado display do `init`: legenda clara com cores + prompt com `show_choices=True`
5. Adicionado `not e.name.startswith(".")` para excluir pastas ocultas
6. Ordenação `key=lambda e: e.name.lower()` no `init` e no `_scan_recursive`
7. Adicionado `enqueue=True` ao handler de arquivo no `_logging.py`
8. Adicionado `logger.info` em 5 pontos do comando `scan`
9. Adicionado `logger.info` por projeto em `metadata_extractor.py` (início e conclusão)

**Artefatos modificados**:
| Arquivo | O que mudou |
|---------|-------------|
| `src/cli/main.py` | [n]→[r], logging init, logging scan (início/fim/arquivo) |
| `src/cli/_logging.py` | `enqueue=True` no handler de arquivo |
| `src/scanner/directory_scanner.py` | Exclusão de ocultos, sort case-insensitive |
| `src/extractor/metadata_extractor.py` | `logger.info` por projeto (início + conclusão) |

**Commits**: `36faf32`, `1fcbc96`, `1587a56`, `028a47d`

**Status**: ✅ Completo

---

### Implementação do `portfolio-gen report`

**~19:00 — ✅ COMPLETO**

**Objetivo**: Implementar o subcomando `report` que estava como stub desde a Phase 6

**Contexto**: `portfolio-gen report output/portfolio-2026-06-18.json` retornava "⚠ Módulo report ainda não implementado". Com 55 projetos no JSON de produção, o usuário precisava de uma visualização útil.

**Passos executados**:
1. Inspecionado JSON de produção para entender estrutura (55 projetos, campos confirmados)
2. Implementado formato `table` com Rich `Panel` (metadados) + `Table` (9 colunas)
3. Implementado formato `csv` com `csv.writer` para stdout
4. Implementado formato `json` com `console.print_json`
5. Implementadas ordenações: `name` (a-z), `language` (a-z), `size` (desc), `date` (desc)
6. Opção `--top N` com mensagem "Exibindo N de Total"
7. Formatação de tamanho (B/KB/MB/GB) e cores por status (active=verde, archived=amarelo)

**Testado em produção**:
- `portfolio-gen report output/portfolio-2026-06-18.json` → tabela 55 projetos ✓
- `portfolio-gen report ... --sort-by size --top 5` → 5 maiores projetos ✓

**Artefatos modificados**:
| Arquivo | O que mudou |
|---------|-------------|
| `src/cli/main.py` | Implementação completa de `report` (table/csv/json) |

**Commits**: `301701a`

**Status**: ✅ Completo

---

### Encerramento de Sessão

**~19:30 — ✅ COMPLETO**

**Objetivo**: Ritual de session-end — docs, gitignore, commit, push

**Passos executados**:
1. Identificado `.portfolio-project` na raiz do projeto sem gitignore → adicionado
2. Adicionado `docs/bugs/` ao `.gitignore`
3. Security scan nos docs de sessão → 🟢 LIMPO
4. Atualização de DAILY_ACTIVITIES e TODO.md
5. Commit de sessão e push

**Status**: ✅ Completo

---
