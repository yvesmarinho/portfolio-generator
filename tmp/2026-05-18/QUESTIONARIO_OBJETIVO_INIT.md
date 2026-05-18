# Questionário para Completar objetivo-init.yaml

**Projeto**: portfolio-generator
**Data**: 2026-05-18
**Fase**: Pré-especificação (não gerar código)
**Objetivo**: Coletar informações necessárias para completar objetivo-init.yaml

---

## 📋 Instruções de Preenchimento

### Como usar este questionário:

1. **Leia cada seção com atenção** — orientações contextuais precedem cada grupo de perguntas
2. **Responda de forma objetiva** — respostas diretas facilitam a integração no YAML
3. **Use exemplos quando apropriado** — ajudam a esclarecer intenções
4. **Marque "N/A" para itens não aplicáveis** — nem tudo é obrigatório
5. **Priorize clareza sobre completude** — melhor responder menos com qualidade

### Estrutura do questionário:

- **Seção 1-3**: Informações básicas e escopo
- **Seção 4-5**: Infraestrutura e tecnologias
- **Seção 6-7**: Funcionalidades e tarefas
- **Seção 8**: Validação e próximos passos

---

## SEÇÃO 1: Descrição e Contexto do Projeto

### 📖 Orientação:
O objetivo atual menciona "escanear pastas em /home/yves_marinho/Documentos/DevOps/ para gerar portfólio profissional em JSON". Isso parece ser um objetivo **diferente** do propósito documentado do portfolio-generator (que é testar e validar scaffolding do Enterprise Template).

### ❓ Perguntas:

**1.1** Este projeto (portfolio-generator) será usado para:
- [ ] A) Criar uma ferramenta de análise de portfólio (como descrito em `description`)
- [ ] B) Testar e validar o Enterprise Template (como descrito em `.copilot-rules.md`)
- [x] C) Ambos (dual purpose)
- [ ] D) Outro: _______________

**1.2** Se a resposta for **A ou C**, descreva em 2-3 parágrafos:
- Qual problema o gerador de portfólio resolve?
- Quem é o usuário/cliente final?
- Qual o diferencial desta solução?

```
RESPOSTA:
- Qual problema o gerador de portfólio resolve? não é problema, mas demanda de ter todos os meus trabalhos catalogados com resumo para publicar em outro projeto.
- Quem é o usuário/cliente final? é para meu uso profissional
- Qual o diferencial desta solução? é uma automação de analise que pode ser usada em outras demandas.


```

**1.3** Se a resposta for **B**, confirme se o objetivo-init.yaml deve ser atualizado para refletir o propósito de validação do template:
- [ ] Sim, atualizar description para refletir propósito de validação
- [x] Não, manter description atual sobre portfólio

---

## SEÇÃO 2: Especificação Técnica

### 📖 Orientação:
Campos vazios ou incompletos na seção `specification` do YAML.

### ❓ Perguntas:

**2.1** `docstyle` — Qual padrão de documentação será usado?
- [x] Google Style (recomendado para Python)
- [ ] NumPy/SciPy Style
- [ ] reStructuredText (reST)
- [ ] Markdown simples
- [ ] Outro: _______________
- [ ] N/A (sem código, apenas validação)

**2.2** Se o projeto incluir análise com Pandas/IA (conforme mencionado), especifique:

**2.2.1** Modelos de IA necessários:
```
Exemplo: OpenAI GPT-4, Claude, modelos locais (llama.cpp), etc.

RESPOSTA:
Opcional: Claude 3.5 Sonnet via API para gerar resumos automáticos
apenas quando README.md não existir ou for muito extenso.
Análise principal será feita sem IA usando metadados estruturados.

```

**2.2.2** Bibliotecas de análise requeridas:
```
Exemplo: pandas, numpy, scikit-learn, langchain, etc.

RESPOSTA:
Essenciais: pandas, pathlib, pyyaml, tomli, gitpython
Análise de código: tree-sitter, pygments, chardet
CLI/UX: click, loguru, rich
IA (opcional): anthropic ou openai (para resumos apenas)

```

**2.2.3** Volume estimado de dados a processar:
- [ ] < 100 MB (pequeno)
- [ ] 100 MB - 1 GB (médio)
- [x] 1 GB - 10 GB (grande)
- [ ] > 10 GB (muito grande)

**2.3** Linguagens de programação do projeto:
```
Exemplo: Python 3.12+, TypeScript, Shell script

RESPOSTA (liste todas):
python 3.12+, mas aceito propostas para outras linguagens se influenciar na qualidade da entrega.

```

---

## SEÇÃO 3: Regras do Projeto

### 📖 Orientação:
A primeira regra em `rules` está vazia. Além das regras P0/P1 do `.copilot-rules.md`, há regras específicas para este projeto?

### ❓ Perguntas:

**3.1** Regras de desenvolvimento específicas do projeto (se houver):
```
Exemplo:
- "Todos os scripts devem ser idempotentes"
- "Análise de código deve usar AST, não regex"
- "JSON gerado deve seguir schema específico (link para schema)"

RESPOSTA:
- "Aplicar as melhores práticas e frameworks do mercados. Como SOLID, design pattern Fabric e outros."
- "Utilizar programação em módulos por responsabilidades e evitar longos arquivos de código"
- "Utilizar biblioteca python CLI"
- "Utilizar Loguru, com logs detalhados que demonstrem o fluxo que o programa percorre."

```

**3.2** Regras de qualidade de código:
- [x] Linting obrigatório antes de commit (ruff, pylint, etc.)
- [x] Cobertura de testes mínima: 90%
- [x] Type hints obrigatórios em Python
- [ ] Documentação obrigatória para funções públicas
- [x] Outras: docuemtnação obrigatória em todas as funções e classes. Headers com detalhes em cada arquivo de código.

**3.3** Regras de segurança adicionais:
```
Exemplo:
- "Nunca processar arquivos fora de /home/yves_marinho/Documentos/DevOps/"
- "Validar todas as entradas de usuário"
- "Usar sandbox para execução de código não confiável"

RESPOSTA:
- "Validar todas as entradas de usuário"
- "Validar dados na entradas de função/classes incluindo tipagem"
- "Utilizar arquivos JSON com dados sensíveis, que nunca devem ser fixos no código"

```

---

## SEÇÃO 4: Resultado Esperado (Expected Outcome)

### 📖 Orientação:
Campo `expected_outcome` está completamente vazio. Descreva o que constitui "sucesso" para este projeto.

### ❓ Perguntas:

**4.1** Critérios de sucesso mensuráveis:
```
Exemplo:
- "Scaffold upgrade executado sem erros em 5 projetos de teste"
- "Portfólio JSON gerado para 50+ projetos em < 5 minutos"
- "100% das configurações MCP validadas automaticamente"

RESPOSTA (liste 3-5 critérios):
1. Sistema capaz de analisar arquivos e gerar um resumo com informações de qualidade
2. Gerar arquivo JSON contendo Nome do projeto, tipo do projeto, resumo rico em detalhes.
3. A execução do código tem de respeitar a tulização de máquina para evitar travamentos.
4.
5.
```

**4.2** Entregáveis concretos ao final do projeto:
```
Exemplo:
- "Ferramenta CLI funcional (portfolio-gen)"
- "Documentação completa em docs/"
- "Suite de testes com 80%+ cobertura"
- "Relatório de validação do Enterprise Template"

RESPOSTA (liste todos):
- "Ferramenta CLI funcional (portfolio-gen)"
- "Documentação completa em docs/"
- "Suite de testes com 80%+ cobertura"
- "Relatório de validação do Enterprise Template"


```

**4.3** Casos de uso de demonstração:
```
Exemplo:
- "Gerar portfólio de projetos Python"
- "Validar upgrade de template em projeto legacy"
- "Exportar métricas de código para dashboard"

RESPOSTA:
- "Gerar portfólio de projetos Python da pasta `/home/yves_marinho/Documentos/DevOps/Vya-Jobs/enterprise-python-snipetts`"


```

---

## SEÇÃO 5: Infraestrutura

### 📖 Orientação:
Campo `infrastructure` está vazio. Descreva requisitos de ambiente, deploy e operação.

### ❓ Perguntas:

**5.1** Ambiente de desenvolvimento:
```
RESPONDA:
- Sistema operacional: Linux Mint (Linux/macOS/Windows/WSL)
- Python version: 3.12+
- Gerenciador de pacotes: uv
- IDE/Editor: VS Code
- Git workflow: a ser definido
```

**5.2** Dependências externas:
```
- [x] Acesso à internet (para modelos de IA, APIs)
- [ ] Banco de dados: _______________ (SQLite/PostgreSQL/MongoDB/N/A)
- [ ] Cache/Storage: _______________ (Redis/disk/S3/N/A)
- [ ] Message Queue: _______________ (RabbitMQ/Kafka/N/A)
RESPOSTA:
- [x] Acesso à internet (para modelos de IA, APIs)

```

**5.3** Deploy e distribuição:
```
Como o projeto será distribuído/usado?
- [x] Script local (execução direta via python/shell)
- [ ] CLI instalável (pip install, uv tool install)
- [ ] Serviço web (API REST/GraphQL)
- [ ] Container (Docker/Podman)
- [ ] Outro: _______________

RESPOSTA:
- [x] Script local (execução direta via python/shell)

```

**5.4** Configuração e secrets:
```
Como serão gerenciadas configurações sensíveis?
- [ ] Arquivo .env local (não versionado)
- [x] Secrets em .secrets/ (já no .gitignore)
- [ ] Variáveis de ambiente do sistema
- [ ] Vault externo (HashiCorp Vault, AWS Secrets Manager)
- [ ] Outro: _______________

RESPOSTA:
- [x] Secrets em .secrets/ (já no .gitignore)

```

**5.5** Monitoramento e logs:
```
Requisitos de observabilidade:
- Logging: _______________ (Python logging, structlog, loguru)
- Métricas: _______________ (Prometheus, statsd, N/A)
- Tracing: _______________ (OpenTelemetry, N/A)
- Alertas: _______________ (e-mail, Slack, N/A)

RESPOSTA:
- Logging: loguru
- Métricas: N/A
- Tracing: N/A
- Alertas: N/A
```

---

## SEÇÃO 6: Funcionalidades a Implementar

### 📖 Orientação:
Campo `features_to_implement` está vazio. Liste features/capacidades planejadas em ordem de prioridade.

### ❓ Perguntas:

**6.1** Funcionalidades principais (MVP - Minimum Viable Product):
```
RESPOSTA (formato: "Feature Name - Descrição curta"):
1. Scanner de Diretórios - Varredura recursiva com filtros e exclusões (.git, node_modules)
2. Extrator de Metadados - Coleta dados estruturados (linguagens, deps, git info)
3. Analisador de Arquivos README - Parser de README.md para extrair descrições
4. Gerador de JSON - Exporta portfólio em schema definido com validação
5. CLI Interativo - Interface com progress bars, verbose/quiet, seleção de pastas
```

**6.2** Funcionalidades secundárias (pós-MVP):
```
RESPOSTA:
1. Análise de Qualidade de Código - Métricas de complexidade, duplicação, coverage
2. Geração de Relatório HTML - Dashboard visual do portfólio
3. Comparação Temporal - Rastrear evolução dos projetos ao longo do tempo
4. Exportação Multi-formato - Markdown, HTML, CSV além de JSON
5. Detecção de Padrões Arquiteturais - Identificar MVC, microservices, monolith
```

**6.3** Integrações planejadas:
```
O projeto precisará integrar com:
- [ ] GitHub API (para análise de repos)
- [ ] OpenAI/Anthropic APIs (para IA)
- [ ] VS Code Extension API (para tooling)
- [ ] MCP Servers (para contexto)
- [ ] Outras: _______________

RESPOSTA:
N/A

```

**6.4** Features de UX/CLI:
```
Interface de usuário planejada:
- [ ] CLI interativo (prompts, progress bars)
- [ ] CLI não-interativo (flags/args only)
- [ ] Configuração via arquivo YAML/JSON
- [ ] Modos verbose/quiet/debug
- [ ] Output formatado (JSON/YAML/Markdown/HTML)

RESPOSTA:
- [x] CLI interativo (prompts, progress bars)
- [x] Modos verbose/quiet/debug
- [x] Output formatado (JSON/YAML/Markdown/HTML)

```

---

## SEÇÃO 7: Tarefas Pendentes

### 📖 Orientação:
Campo `pending_tasks` está vazio. Liste tarefas imediatas para iniciar o projeto.

### ❓ Perguntas:

**7.1** Tarefas de setup inicial (próximos passos):
```
RESPOSTA (marque com [x] as já concluídas):
- [x] Configurar ambiente virtual Python (.venv criado)
- [x] Definir schema JSON para portfólio (schemas/portfolio-schema-v1.json)
- [ ] Criar estrutura de pastas src/
- [ ] Instalar dependências (pandas, click, rich, loguru, gitpython, etc.)
- [ ] Criar módulo scanner de diretórios
- [ ] Criar módulo extrator de metadados
- [ ] Criar módulo analisador de README
- [ ] Criar módulo gerador de JSON
- [ ] Criar CLI principal
- [ ] Definir testes unitários
- [ ] Documentar casos de uso e exemplos
```

**7.2** Prioridade das tarefas:
```
Das tarefas listadas acima, ordene as 5 mais urgentes:
1. Criar estrutura de pastas src/ (organização)
2. Instalar dependências base (pandas, click, rich, loguru, gitpython)
3. Implementar scanner de diretórios (primeira feature)
4. Criar módulo extrator de metadados (segunda feature)
5. Criar CLI básico (integração)
```

**7.3** Blockers/Dependências:
```
Há algo que precisa ser resolvido ANTES de começar?
Exemplo: "Aguardando aprovação de schema JSON pelo cliente"

RESPOSTA:
N/A

```

---

## SEÇÃO 8: Validação e Próximos Passos

### 📖 Orientação:
Garantir alinhamento antes de gerar spec.md/plan.md/tasks.md.

### ❓ Perguntas:

**8.1** Workflow SpecKit está correto para este projeto?
```
O objetivo-init.yaml menciona "workflow-specify: Geração automática de spec.md, plan.md e tasks.md"

CONFIRME:
- [x] Sim, usar SpecKit para gerar especificação
- [ ] Não, usar outro método

OBSERVAÇÃO:
Workflow SpecKit será executado APÓS completar objetivo-init.yaml.
Sequência:
1. Atualizar objetivo-init.yaml com respostas deste questionário
2. Executar SpecKit (gerar spec.md, plan.md, tasks.md)
3. Revisar especificação gerada
4. Iniciar implementação seguindo tasks.md
```

**8.2** Perfil do desenvolvedor está adequado?
```
Perfil atual: "copilot-assisted-developer" - nível "intermediate"

AJUSTAR?
- [ ] Manter como está
- [x] Mudar role e nível
- Configuração recomendada:
  * python-developer: advanced
  * data-analyst: intermediate
  * cli-tool-developer: intermediate
  * copilot-assisted-developer: advanced
```

**8.3** Revisão de escopo:
```
Após preencher este questionário, o escopo está:
- [x] Claro e bem definido
- [ ] Precisa de refinamento (especifique): _______________
- [ ] Muito amplo (precisa reduzir escopo)
- [ ] Muito restrito (pode expandir)

COMENTÁRIOS:
Todas as orientações técnicas foram aplicadas. MVP com 5 features bem definidas,
bibliotecas selecionadas, IA opcional, schema JSON criado. Pronto para objetivo-init.yaml.

```

**8.4** Próxima ação recomendada:
```
Após completar este questionário:
1. [X] Atualizar objetivo-init.yaml com respostas
2. [ ] Executar SpecKit para gerar spec.md
3. [ ] Revisar com stakeholders antes de prosseguir
4. [ ] Outra: _______________
```

---

## 📝 Notas Adicionais

```
Espaço para comentários, dúvidas ou contexto adicional:





```

---

## ✅ Checklist Final

Antes de submeter, verifique:

- [x] Todas as seções foram lidas
- [x] Perguntas críticas (1.1, 4.1, 6.1) foram respondidas
- [ ] Respostas são objetivas e acionáveis
- [ ] Escopo está claro o suficiente para gerar spec.md
- [ ] Não há contradições entre respostas

---

**Data de preenchimento**: 18/05/2026
**Preenchido por**: Yves Marinho
**Revisado por**: Copilot

---

## 🎯 Próximos Passos (após preenchimento)

1. **Revisar respostas** com time/stakeholders
2. **Atualizar objetivo-init.yaml** baseado nas respostas
3. **Executar SpecKit** para gerar `spec.md`, `plan.md`, `tasks.md`
4. **Validar especificação** antes de iniciar implementação
5. **Documentar decisões** em `docs/decisions/`

---

*Este questionário foi gerado automaticamente baseado em análise do objetivo-init.yaml e .copilot-rules.md*
*Versão: 1.0 | Data: 2026-05-18*
