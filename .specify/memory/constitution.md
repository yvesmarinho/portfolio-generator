<!-- Sync Impact Report
Version change: template → 1.0.0
Added sections: Core Principles (6), Quality Standards, Development Workflow, Governance
Modified principles: N/A (first version)
Removed sections: N/A
Templates requiring updates:
  ✅ .specify/templates/plan-template.md — referências a princípios verificadas
  ✅ .specify/templates/spec-template.md — escopo alinhado
  ✅ .specify/templates/tasks-template.md — categorias de tarefas alinhadas
Follow-up TODOs: None
Ratification: 2026-06-17 (Yves Marinho + Claude Sonnet 4.6)
-->

# portfolio-generator Constitution

## Core Principles

### I. Modular Architecture (SOLID)

O código é organizado em packages por responsabilidade dentro de `src/`:
`scanner/`, `extractor/`, `analyzer/`, `generator/`, `cli/`. Cada package:
- Contém um `__init__.py` que expõe uma factory function (Factory Pattern)
- É independentemente testável e importável
- Tem responsabilidade única e bem definida (SRP)
- Não importa de outros packages do mesmo nível exceto via interfaces explícitas (DIP)

Nenhum arquivo Python deve ultrapassar 300 linhas. Se ultrapassar, dividir em sub-módulos.
Nenhuma função deve ultrapassar 50 linhas. Lógica complexa → métodos privados nomeados.

### II. Test-First (90%+ Coverage) — NON-NEGOTIABLE

TDD obrigatório: testes escritos e aprovados antes da implementação.
Ciclo: Escreve teste → Teste falha (Red) → Implementa → Teste passa (Green) → Refatora.

Requisitos não negociáveis:
- `pytest --cov` com cobertura de **branches** >= 90% em todos os módulos
- Fixtures de sistema de arquivos em `tests/fixtures/` para simular projetos reais
- Nenhum commit aceito sem todos os testes passando
- Testes de integração obrigatórios para o fluxo completo (scan → extract → generate)
- Tempo máximo de execução da suite: 5 segundos (sem testes flaky)

### III. Security by Default

Credenciais e dados sensíveis:
- SOMENTE em `.secrets/*.json` — nunca hardcoded, nunca em `.env` commitado
- NUNCA usar `curl` com tokens ou senhas — sempre `python requests` lendo de `.secrets/`
- Mascarar IPs, tokens e senhas ao exibir logs ou output no terminal (`***`)

Pipeline de segurança:
- `bandit` (análise estática de segurança) e `safety` (vulnerabilidades em deps) em CI e pre-commit
- `.secrets/` verificado no `.gitignore` a cada sessão — scan automatizado no session-start
- API key da Anthropic lida de `.secrets/api_config.json`; nunca passada via argumento CLI

Escopo de processamento: SOMENTE `/home/yves_marinho/Documentos/DevOps/` — validado em runtime
antes de qualquer leitura de arquivo.

### IV. Performance Contracts

Contratos mensuráveis, verificados nos testes de carga:
- Scan de 100+ projetos em **< 30 segundos** (alvo: < 10s em hardware típico)
- Processamento de 1 projeto em **< 2 segundos** com todos os metadados
- Uso de RAM **< 512 MB** durante análise completa (100 projetos)
- Uso de CPU: throttleable via `--workers N` (default: `min(4, os.cpu_count())`)

Motor de processamento: `concurrent.futures.ProcessPoolExecutor` para paralelismo real
(CPU-bound + I/O-bound). Asyncio descartado — overhead desnecessário para este workload.

### V. Graceful Degradation

O sistema NUNCA para por um projeto individual problemático:
- Skip-and-continue para projetos com arquivos corrompidos, encoding inválido ou git history quebrado
- Todo skip gera `logger.warning()` via loguru com path e exceção completa
- Bug-report automático em `docs/bugs/bug-report-YYYYMMDD-HHmm.md` para cada erro não-esperado
- `None` retornado por `scan_project()` em caso de erro — filtrado na agregação
- Relatório de execução sempre inclui: projetos processados, projetos pulados, erros encontrados

### VI. CLI-First UX

A ferramenta é operada via linha de comando com experiência clara e previsível:
- `click` para subcomandos, opções e validação de argumentos
- `rich` para progress bars, tabelas e output colorido
- `--dry-run` obrigatório em todos os subcomandos que escrevem arquivos
- `--verbose` / `--quiet` disponíveis em todos os subcomandos
- Help completo (`--help`) com exemplos de uso em cada subcomando
- Mensagens de erro claras com sugestão de ação corretiva (não apenas stack trace)
- `loguru` para logs detalhados de execução (DEBUG mostra fluxo; INFO mostra progresso)

---

## Quality Standards

Padrões técnicos de qualidade exigidos em todo código:

**Type hints**: Obrigatórios em 100% das funções e métodos públicos — `mypy --strict` sem violações.

**Formatação e linting**: `black` (formatação), `ruff` (linting + imports), `pylint` (análise estática).
Zero violações permitidas antes de commit.

**Docstrings**: Padrão reStructuredText (PEP 257) com exemplos Doctest em toda função e classe pública:
```python
def exemplo(param: str) -> bool:
    """
    Descrição da função.

    :param param: Descrição.
    :type param: str
    :return: True se sucesso, False se erro.
    :rtype: bool

    >>> exemplo("valor")
    True
    >>> exemplo("")
    False
    """
```

**Tratamento de erros**: Todo código envolvido em `try/except`; funções retornam `False` (não exception)
em caso de erro; parâmetros validados quanto a vazio e tipagem antes da lógica principal.

**Pre-commit hooks**: black, ruff, mypy, bandit, safety — todos obrigatórios antes de qualquer commit.
`--no-verify` PROIBIDO.

---

## Development Workflow

**Branches**: Convenção `NNN-nome-da-feature` (ex: `001-scanner-modulo`). Features retornam para
`main` após conclusão e testes. Branches merged são deletadas.

**Commits**: Atômicos; mensagem em português com tipo convencional (`feat`, `fix`, `docs`, etc.);
co-autoria `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`; nunca sem testes passando.

**Sessões**: Todo trabalho logado em `docs/SESSIONS/YYYY-MM-DD/` com timestamps, decisões e outcomes.
Security scan (find credentials) executado no início e fim de cada sessão.

**ADRs**: Decisões arquiteturais documentadas em `docs/architecture/adr/` como
`ADR-NNN-titulo.md` no momento da decisão — não retroativamente.

**Package manager**: `uv` para ambiente Python e dependências. `pip` direto é proibido.

---

## Governance

Esta constitution é o documento de maior autoridade no projeto. Supersede qualquer outro guia,
README ou instrução ad-hoc.

**Emendas**: Toda alteração requer:
1. ADR documentando o motivo e as alternativas consideradas
2. Atualização deste arquivo com bump de versão (semver)
3. Atualização dos templates dependentes (`plan-template.md`, `spec-template.md`, `tasks-template.md`)
4. Commit com mensagem: `docs: amend constitution to vX.Y.Z (descrição da mudança)`

**Versionamento semântico**:
- MAJOR: Remoção ou redefinição incompatível de princípio
- MINOR: Novo princípio ou seção adicionada
- PATCH: Clarificações, correções de redação, refinamentos não-semânticos

**Compliance**: Todo PR verificado contra esta constitution antes de merge. Violations bloqueiam merge.

**Arquivo de runtime guidance**: `objetivo-init.yaml` (especificação detalhada) + `CLAUDE.md` (regras do assistente AI).

**Version**: 1.0.0 | **Ratified**: 2026-06-17 | **Last Amended**: 2026-06-17
