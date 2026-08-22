---
description: Ritual de início e encerramento de sessão de trabalho. Use com argumento: start | end | pause [motivo] | resume | first-time
allowed-tools: Read, Write, Edit, Bash, TodoWrite
---

# Session Manager — Claude Code

## Uso

```
/session-manager start          # início de sessão recorrente
/session-manager end            # encerramento de sessão
/session-manager first-time     # configuração inicial do projeto
/session-manager pause café     # pausar time tracking
/session-manager resume         # retomar após pausa
```

## Argumento recebido

```
$ARGUMENTS
```

Interpretar o argumento e executar o workflow correspondente abaixo.

---

## Workflow: SESSION START (argumento: `start` ou vazio)

### Passo 1 — Git Status

```bash
git status
git log --oneline -5
```

Reportar: branch ativa, arquivos modificados não commitados, commits não pushados.

### Passo 2 — Recuperar Contexto

Ler na ordem:
1. `docs/TODO.md` — tarefas pendentes
2. `docs/INDEX.md` — mapa do projeto (se existir)
3. `docs/SESSIONS/` — data do último diretório e ler `FINAL_STATUS_*.md` dentro dele

Declarar ao usuário:
```
✅ Contexto recuperado. Última sessão: [data].
Tarefas P0/P1 pendentes: [lista do TODO.md]
Branch: [branch] | Commits não pushados: [N]
```

### Passo 3 — Scan de Segurança

```bash
find . -not -path './.git/*' -not -path './.secrets/*' \
  \( -name '*.env' -o -name '.env*' -o -name '*.key' -o -name '*.pem' \
     -o -name '*secret*' -o -name '*password*' -o -name '*token*' \) 2>/dev/null
```

Reportar: `🟢 LIMPO` ou `🔴 CREDENCIAIS EXPOSTAS: [arquivos]`

Se exposto: parar e reportar antes de continuar.

### Passo 4 — Criar Documentos de Sessão

Criar diretório `docs/SESSIONS/[YYYY-MM-DD]/` se não existir:

```bash
mkdir -p docs/SESSIONS/$(date +%Y-%m-%d)
```

Criar `docs/SESSIONS/[data]/SESSION_RECOVERY_[data].md` com:
```markdown
# Session Recovery — [YYYY-MM-DD]

**Sessão anterior**: [data da última sessão]
**Branch**: [branch ativa]
**Último commit**: [hash e mensagem]

## Contexto Recuperado
[resumo do FINAL_STATUS anterior]

## Tarefas P0/P1 para Esta Sessão
[lista do TODO.md]
```

Criar `docs/SESSIONS/[data]/DAILY_ACTIVITIES_[data].md` se não existir:
```markdown
# Daily Activities — [YYYY-MM-DD]

---
```

### Passo 5 — Iniciar Rastreamento de Tempo

```bash
python scripts/session-time-tracker.py start 2>/dev/null || echo "⚠ session-time-tracker não disponível"
```

### Passo 6 — Definir Escopo

Perguntar ao usuário:
```
📋 Escopo da sessão:
[1] Continuar tarefas pendentes da sessão anterior
[2] Iniciar novas tarefas

Modo de trabalho: PROGRAMMING | INFRASTRUCTURE | ANALYSIS
```

Usar `TodoWrite` para registrar as tarefas da sessão.

---

## Workflow: SESSION END (argumento: `end`)

### Passo 1 — Finalizar Documentação

Atualizar `docs/SESSIONS/[hoje]/DAILY_ACTIVITIES_[data].md` (append via Edit):
```markdown
---

### Encerramento da Sessão

**[HH:MM] — ENCERRADO**

**Resumo**: [o que foi feito]
**Commits desta sessão**: [lista]
**Status**: ✅ Encerrado
```

Criar/atualizar `docs/SESSIONS/[hoje]/FINAL_STATUS_[data].md`:
```markdown
# Final Status — [YYYY-MM-DD]

**Branch**: [branch]
**Último commit**: [hash]

## Tarefas Concluídas
- [lista]

## Tarefas Pendentes (próxima sessão)
- [lista do TODO.md não concluídas]

## Contexto para Próxima Sessão
[o que o próximo Claude precisa saber]
```

### Passo 2 — Atualizar TODO.md

Marcar tarefas concluídas com `[x]` usando `Edit`.

### Passo 3 — Scan de Segurança Final

Repetir o scan do Passo 3 do session-start.

### Passo 4 — Parar Rastreamento de Tempo

```bash
python scripts/session-time-tracker.py stop 2>/dev/null || echo "⚠ session-time-tracker não disponível"
```

### Passo 5 — Commit de Encerramento

```bash
git add docs/
git status
```

Criar commit:
```bash
git commit -m "$(cat <<'EOF'
docs(sessão): encerramento [YYYY-MM-DD]

Sessão [YYYY-MM-DD] encerrada.
- [lista de conquistas]
- [arquivos criados/modificados]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

### Passo 6 — Relatório Final

```
🏁 Sessão [YYYY-MM-DD] encerrada

✅ Documentação: DAILY_ACTIVITIES + FINAL_STATUS atualizados
✅ TODO.md: tarefas marcadas
✅ Segurança: 🟢 LIMPO
✅ Commit criado
```

---

## Workflow: PAUSE (argumento: `pause [motivo]`)

```bash
python scripts/session-time-tracker.py pause "[motivo]" 2>/dev/null || echo "⚠ Rastreamento não disponível"
```

Reportar: `⏸️ Pausado: [timestamp] | Motivo: [motivo]`
Informar: use `/session-manager resume` para retomar.

---

## Workflow: RESUME (argumento: `resume`)

```bash
python scripts/session-time-tracker.py resume 2>/dev/null || echo "⚠ Rastreamento não disponível"
```

Recuperar contexto do último trabalho (último commit, DAILY_ACTIVITIES).
Reportar: `▶️ Retomado: [timestamp] | Pausa: [duração]`

---

## Workflow: FIRST-TIME (argumento: `first-time`)

### Passo 1 — Verificar Pré-requisitos

```bash
python3 --version && git --version && uv --version 2>/dev/null || echo "uv não instalado"
```

### Passo 2 — Inicializar Estrutura

```bash
mkdir -p docs/SESSIONS docs/.tmp .secrets scripts src tests
```

Criar `docs/TODO.md` se não existir via `Write`.
Criar `docs/INDEX.md` se não existir via `Write`.

### Passo 3 — Segurança

```bash
grep -q '.secrets/' .gitignore 2>/dev/null || echo '.secrets/' >> .gitignore
```

### Passo 4 — Continuar com SESSION START

Executar o workflow de `start` após a inicialização.

---

## Regras de Documentação Durante a Sessão

Atualizar `DAILY_ACTIVITIES_[data].md` após atividades significativas (append via `Edit`):

```markdown
---

### [Título da Atividade]

**[HH:MM] — [STATUS]**

**Objetivo**: [o que foi feito]
**Resultado**: [sucesso/bloqueio]
**Arquivos**: [lista]
**Commits**: [`hash` — mensagem]

**Status**: ✅ Completo | 🔵 Em progresso | ❌ Bloqueado
```
