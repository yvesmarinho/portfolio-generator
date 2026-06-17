# Claude Code — Instruções do Projeto

**Projeto**: `portfolio-generator` — Gerador de portfólio profissional  
**Comandos disponíveis**: `.claude/commands/` (`/session-manager`, `/speckit.*`, `/devops.*`, etc.)  
**Memória persistente**: gerenciada automaticamente via sistema de memória do Claude Code

---

## Idioma e Comunicação

Este projeto é brasileiro. Todas as interações em **Português do Brasil (pt-BR)**.

- Respostas: sempre em português (pt-BR)
- Código e variáveis: inglês (padrão internacional)
- Documentação e comentários: português
- Mensagens de commit: português (exceto tipos: `feat`, `fix`, `docs`, `chore`, etc.)

---

## Ferramentas do Claude Code

| Operação | Ferramenta |
|----------|-----------|
| Ler arquivo | `Read` |
| Criar arquivo novo | `Write` |
| Editar arquivo existente | `Edit` |
| Executar comandos shell | `Bash` |
| Buscar texto/padrão | `Bash(grep ...)` |
| Encontrar arquivos | `Bash(find ...)` |
| Rastrear tarefas da sessão | `TodoWrite` |
| Explorar codebase | `Agent(Explore)` |

---

## Regras P0 — CRÍTICO

### 1. Commits git

```bash
git commit -m "$(cat <<'EOF'
tipo(escopo): descrição

Corpo do commit aqui.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

Nunca pular hooks (`--no-verify`). Nunca force-push em `main`.

### 2. Segurança de credenciais

- Nunca versionar `.env*`, `*.key`, `*.pem`, `*secret*`, `*token*`, `*password*`
- `.secrets/` está no `.gitignore` — verificar a cada sessão
- MCP configs: usar `${env:VAR_NAME}` para tokens, nunca valor direto

### 3. Organização de arquivos

| Tipo | Localização |
|------|-------------|
| Documentação de sessão | `docs/SESSIONS/YYYY-MM-DD/` |
| Documentação técnica | `docs/` |
| Código fonte Python | `src/` |
| Scripts | `scripts/` |
| Testes | `tests/` |

Nunca criar arquivos de sessão/doc na raiz do projeto.

### 4. Documentos incrementais — nunca sobrescrever por completo

| Arquivo | Comportamento |
|---------|--------------|
| `README.md` | Atualizar seções; preservar conteúdo anterior |
| `docs/INDEX.md` | Adicionar entradas; manter histórico |
| `docs/TODO.md` | Marcar `[x]`; adicionar itens; nunca remover |
| `docs/SESSIONS/*/DAILY_ACTIVITIES_*.md` | Append de blocos com separador `---` |
| `docs/SESSIONS/*/SESSION_REPORT_*.md` | Append de seções |
| `docs/SESSIONS/*/FINAL_STATUS_*.md` | Adicionar linhas; nunca remover |

---

## Continuidade de Sessão

O Claude Code usa memória persistente em arquivos markdown. Para garantir continuidade:

### Início de sessão
Ao iniciar uma nova conversa neste projeto, o Claude deve **automaticamente**:
1. Ler `docs/TODO.md` para recuperar tarefas pendentes
2. Executar `git status` e `git log --oneline -5`
3. Verificar arquivos sensíveis expostos (scan de segurança)
4. Declarar o contexto recuperado antes de iniciar qualquer trabalho

Use `/session-manager` para o ritual completo de início/encerramento de sessão.

### Memória entre sessões
O Claude Code salva automaticamente em `~/.claude/projects/[projeto]/memory/`:
- Contexto do projeto (decisões, arquitetura, estado)
- Preferências e feedback do usuário
- Tarefas em andamento relevantes para próximas sessões

### Encerramento de sessão
Antes de encerrar, o Claude deve:
1. Atualizar `docs/TODO.md` com progresso
2. Criar commit de sessão com resumo do que foi feito
3. Salvar memórias relevantes para a próxima sessão

---

## Nomenclatura

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| Python | `snake_case.py` | `project_config.py` |
| Markdown docs | `SCREAMING_SNAKE.md` | `SESSION_REPORT.md` |
| JSON configs | `kebab-case.json` | `mcp-config.json` |
| Shell scripts | `kebab-case.sh` | `git-commit.sh` |
| Branch feat | `NNN-nome-da-feature` | `018-portfolio-generator` |
| Branch fix | `fix-descricao` | `fix-symlink-broken` |

---

## Padrões de Código Python

Aplicar **sempre** ao escrever ou revisar código Python:

### Tratamento de erros
- Todo código envolto em `try/except`
- Funções e classes retornam `False` em caso de erro (nunca lançar exceção sem tratar)

### Validação de parâmetros
- Toda função/classe valida os parâmetros recebidos quanto a **vazio** e **tipagem** antes de executar

### Documentação
- Docstrings no padrão **reStructuredText**, incluindo **doctest**

```python
def exemplo(param: str) -> bool:
    """
    Descrição da função.

    :param param: Descrição do parâmetro.
    :type param: str
    :return: True se sucesso, False se erro.
    :rtype: bool

    >>> exemplo("valor")
    True
    >>> exemplo("")
    False
    """
    if not param or not isinstance(param, str):
        return False
    try:
        # lógica aqui
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False
```

### Docker
- `docker-compose.yaml` **não** usa o parâmetro `version`
- Usar `docker compose` (plugin), nunca `docker-compose` (legado)

---

## MCP Servers Ativos

Configurados em `.claude/settings.json`:

- **`memory`** — grafo de conhecimento persistente entre sessões (`@modelcontextprotocol/server-memory`)
- **`sequential-thinking`** — raciocínio estruturado em etapas para tarefas complexas (`@modelcontextprotocol/server-sequential-thinking`)

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->
