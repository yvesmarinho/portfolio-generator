# Spec - portfolio-generator

## 1. Visão Geral

O projeto **portfolio-generator** tem como objetivo criar uma ferramenta CLI profissional para catalogar projetos localizados em `/home/yves_marinho/Documentos/DevOps/`, produzindo um portfólio estruturado em JSON com dados técnicos, resumo descritivo, métricas de código, tecnologias identificadas, metadados Git e indicadores de qualidade.

A solução deve priorizar análise determinística baseada em estrutura de arquivos e metadados locais. O uso de IA é opcional e restrito a cenários em que o `README.md` seja inexistente, excessivamente extenso, inválido ou insuficiente para gerar um resumo útil.

A ferramenta deve ser robusta, extensível, testável, segura e adequada a cenários de uso profissional com grandes volumes de dados locais.

---

## 2. Objetivo do Produto

Construir uma ferramenta de automação reutilizável para:

1. varrer diretórios de projetos com segurança;
2. identificar projetos candidatos;
3. extrair metadados estruturados e informações de tecnologia;
4. analisar documentação disponível;
5. enriquecer o entendimento do projeto com dados Git;
6. gerar um arquivo JSON padronizado e validado por schema;
7. oferecer interface CLI clara, observável e segura;
8. permitir futura expansão para relatórios HTML, análise temporal e exportações adicionais.

---

## 3. Problema a Ser Resolvido

O usuário possui múltiplos projetos em uma árvore local de diretórios e precisa consolidar um portfólio técnico de forma automatizada, reprodutível e com boa qualidade de informação.

Atualmente, esse tipo de catalogação costuma ser:

- manual;
- inconsistente;
- pouco escalável;
- suscetível a omissões;
- difícil de manter atualizado;
- sem padronização de saída.

A solução proposta reduz trabalho manual, padroniza o resultado e cria base para reaproveitamento em fluxos futuros.

---

## 4. Escopo

### 4.1 Em escopo

- varredura recursiva de projetos dentro de `/home/yves_marinho/Documentos/DevOps/`;
- exclusão de diretórios irrelevantes, como `.git`, `node_modules`, `.venv`, `dist`, `build`, `tmp` e equivalentes;
- detecção de projetos por heurísticas estruturais;
- leitura de arquivos de metadados e manifestos;
- leitura e interpretação de `README.md`;
- extração de metadados Git;
- identificação de linguagens e tecnologias predominantes;
- cálculo de métricas iniciais de código;
- exportação JSON validada por schema;
- interface CLI com logs e feedback visual;
- testes automatizados;
- documentação técnica e operacional;
- preparação do fluxo para `plan.md` e `tasks.md`.

### 4.2 Fora de escopo inicial

- edição automática de projetos analisados;
- execução de código dos projetos analisados;
- deploy remoto;
- integração contínua complexa com múltiplos ambientes;
- dashboard web completo na primeira versão;
- análise semântica profunda de arquitetura distribuída;
- inferência avançada por IA como mecanismo principal de análise.

---

## 5. Usuários e Perfis

### 5.1 Usuário principal

Desenvolvedor Python avançado, usuário Linux, com perfil técnico voltado a CLI, automação, análise de dados e uso assistido por Copilot.

### 5.2 Características relevantes

- prefere ferramentas locais;
- valoriza observabilidade;
- deseja modularidade;
- precisa de reutilização futura;
- possui preocupação com qualidade, testes e segurança;
- aceita IA apenas como apoio opcional.

---

## 6. Requisitos Funcionais

### RF-001 - Scanner seguro de diretórios

O sistema deve varrer recursivamente diretórios abaixo de `/home/yves_marinho/Documentos/DevOps/`.

#### Critérios
- rejeitar qualquer caminho fora da raiz permitida;
- aplicar filtros configuráveis;
- ignorar diretórios sabidamente não relevantes;
- operar com baixo risco de travamento.

### RF-002 - Detecção de projetos

O sistema deve identificar diretórios que representam projetos candidatos.

#### Heurísticas iniciais
- presença de `.git`;
- presença de `pyproject.toml`, `requirements.txt`, `package.json`, `Dockerfile`, `Makefile`, `README.md`, `setup.py`, `Cargo.toml`, `go.mod` ou arquivos equivalentes;
- densidade mínima de arquivos-fonte.

### RF-003 - Extração de metadados

O sistema deve coletar metadados relevantes por projeto.

#### Exemplos
- nome do projeto;
- caminho;
- tipo presumido;
- linguagens detectadas;
- dependências declaradas;
- arquivos relevantes;
- tamanho aproximado;
- indicadores básicos de estrutura.

### RF-004 - Análise de README

O sistema deve localizar e interpretar `README.md` ou variantes.

#### Objetivo
- extrair descrição;
- identificar propósito;
- detectar stack tecnológica;
- capturar comandos, badges e pistas arquiteturais quando possível.

### RF-005 - Fallback opcional com IA

O sistema poderá usar IA para resumo apenas quando a documentação local for insuficiente.

#### Restrições
- a IA não é parte obrigatória do fluxo principal;
- a falha de IA não pode impedir a análise;
- o uso deve ser explicitamente registrável e configurável.

### RF-006 - Metadados Git

O sistema deve extrair informações Git quando disponíveis.

#### Exemplos
- branch atual;
- último commit;
- data do último commit;
- autor do último commit;
- estado do repositório;
- existência de remoto;
- tags relevantes quando disponíveis.

### RF-007 - Geração de JSON

O sistema deve produzir um JSON validado por schema versionado.

#### Requisitos
- saída determinística sempre que possível;
- estrutura consistente;
- suporte a múltiplos projetos;
- suporte a erros por item sem invalidar o lote inteiro.

### RF-008 - CLI principal

O sistema deve expor uma CLI com comando principal `portfolio-gen`.

#### Capacidades mínimas
- selecionar diretório alvo;
- definir output;
- controlar verbosidade;
- exibir progresso;
- ativar ou desativar IA;
- limitar profundidade ou escopo;
- gerar mensagens de erro claras.

### RF-009 - Logging estruturado

O sistema deve registrar eventos relevantes com `loguru`.

#### Eventos mínimos
- início da execução;
- diretório validado;
- projeto detectado;
- falha de análise por projeto;
- export concluído;
- resumo final.

### RF-010 - Validação de schema

O sistema deve validar o JSON final usando schema versionado antes da persistência final ou imediatamente após gerá-lo.

---

## 7. Requisitos Não Funcionais

### RNF-001 - Segurança de caminho

O sistema nunca deve processar caminhos fora de `/home/yves_marinho/Documentos/DevOps/`.

### RNF-002 - Robustez

Falhas isoladas devem ser registradas e não interromper a análise total, salvo erro crítico de configuração ou entrada principal inválida.

### RNF-003 - Desempenho

O sistema deve operar adequadamente com volumes entre 1 GB e 10 GB, evitando leitura integral desnecessária de arquivos grandes e uso excessivo de memória.

### RNF-004 - Testabilidade

A arquitetura deve permitir testes unitários, de integração, contrato e ponta a ponta.

### RNF-005 - Observabilidade

Logs, status, resumo final e mensagens de erro devem ser suficientes para diagnóstico de falhas.

### RNF-006 - Manutenibilidade

O código deve ser modular, tipado, documentado, coeso e com baixo acoplamento.

### RNF-007 - Qualidade automatizada

A pipeline local e futura CI deve exigir:
- `ruff`;
- `pylint`;
- `mypy`;
- `pytest`;
- `pytest-cov >= 90%`.

### RNF-008 - Reprodutibilidade

Dada a mesma árvore de entrada e a mesma configuração, o sistema deve produzir resultado equivalente, exceto por campos naturalmente variáveis, como timestamps ou estado Git corrente.

---

## 8. Arquitetura Mínima Obrigatória

### 8.1 Estilo arquitetural

O sistema deve seguir:

- **Layered Architecture**
- **DDD leve**
- **Ports/Adapters simplificado**

### 8.2 Camadas

#### Presentation
Responsável por:
- CLI;
- parsing de argumentos;
- feedback ao usuário;
- renderização de progresso e saída amigável.

#### Application
Responsável por:
- casos de uso;
- orquestração;
- DTOs;
- coordenação entre domínio e infraestrutura.

#### Domain
Responsável por:
- entidades;
- value objects;
- invariantes;
- regras de negócio;
- contratos sem dependência de bibliotecas externas de interface ou infraestrutura.

#### Infrastructure
Responsável por:
- filesystem;
- Git;
- parsing;
- exportação;
- configuração;
- integrações de IA;
- persistência local de artefatos.

#### Shared
Responsável por:
- utilitários reutilizáveis;
- validadores;
- exceções compartilhadas;
- enums;
- logging bootstrap.

### 8.3 Restrições obrigatórias

- a CLI não deve conter regra de negócio;
- o domínio não deve depender de `click`, `rich`, `loguru`, `gitpython` ou SDKs de IA;
- integrações externas devem ser encapsuladas;
- contratos devem ser explícitos;
- validadores devem ser reutilizáveis;
- schema JSON deve ser versionado.

---

## 9. Modelo de Domínio Inicial

### 9.1 Entidades centrais

#### Project
Representa um projeto identificado na árvore local.

Atributos esperados:
- nome;
- caminho;
- tipo;
- stack;
- resumo;
- métricas;
- metadados Git;
- status da análise.

#### Portfolio
Representa o conjunto final consolidado de projetos analisados.

#### AnalysisResult
Representa o resultado da análise de um projeto específico, incluindo sucesso parcial, warnings e falhas.

### 9.2 Value Objects

- `ProjectPath`
- `LanguageStat`
- `TechnologyTag`
- `QualityMetric`
- `ExportTarget`

### 9.3 Serviços de domínio

- `ProjectClassifier`
- `SummaryResolver`
- `MetricAggregator`
- `PortfolioAssembler`

### 9.4 Invariantes

- todo `ProjectPath` deve estar dentro da raiz permitida;
- todo projeto deve possuir identificador mínimo válido;
- toda exportação deve obedecer ao schema;
- toda análise deve registrar status final.

---

## 10. Estratégia de Tratamento de Erros

### 10.1 Princípios

- falhar rápido em entradas inválidas;
- degradar graciosamente em falhas por projeto;
- registrar contexto suficiente;
- evitar mascaramento indevido de falhas.

### 10.2 Diretriz operacional

O usuário definiu preferência por `try/except` abrangente e retorno `False` em falhas. Para manter qualidade arquitetural, a especificação adota o seguinte equilíbrio:

- fronteiras externas devem usar `try/except`;
- operações de I/O e integrações devem usar `try/except`;
- funções internas críticas podem lançar exceções de domínio tipadas;
- retornos `False` são aceitáveis em contratos explicitamente booleanos ou em serviços operacionais documentados;
- todas as falhas precisam ser logadas.

### 10.3 Resultado esperado

O sistema deve:
- continuar o lote quando um projeto falhar;
- registrar projeto com erro ou warning;
- encerrar a execução apenas quando houver falha crítica global.

---

## 11. Estratégia de Testes

### 11.1 Tipos de teste obrigatórios

#### Unitários
Para:
- validadores;
- classificadores;
- parsers puros;
- agregadores de métricas;
- regras de domínio.

#### Integração
Para:
- scanner + filesystem;
- Git metadata extractor;
- exportador JSON;
- validação de schema.

#### Contrato
Para:
- estrutura do JSON final;
- contratos de adapters;
- comportamento de serviços expostos.

#### E2E
Para:
- execução CLI em cenário controlado.

### 11.2 Meta de cobertura

Cobertura mínima obrigatória de 90%.

### 11.3 Estratégia adicional

Priorizar TDD para:
- validação de paths;
- regras de classificação;
- parser de README;
- agregação de portfólio;
- schema validation.

---

## 12. Regras de Implementação

### 12.1 Linguagem e stack

- Python 3.12+
- `click`
- `loguru`
- `rich`
- `pandas`
- `gitpython`
- `pyyaml`
- `tomli`
- `tree-sitter`
- `pygments`
- `chardet`
- `pydantic`
- `jsonschema`

### 12.2 Estilo de código

- tipagem obrigatória;
- documentação obrigatória;
- docstring em **reStructuredText**;
- incluir **doctest** sempre que fizer sentido;
- módulos pequenos;
- arquivos coesos;
- evitar lógica duplicada.

### 12.3 Ferramentas de qualidade

- `ruff`
- `pylint`
- `mypy`
- `pytest`
- `pytest-cov`

### 12.4 Configuração

- usar `pyproject.toml`;
- segredos fora do código;
- `.secrets/` fora de versionamento;
- schema em pasta dedicada;
- logs em pasta dedicada.

---

## 13. Estrutura Inicial Recomendada

```text
portfolio-generator/
├── .github/
├── .git-hooks/
├── .memory/
├── .secrets/
├── .session-index/
├── .session-time/
├── .specify/
├── .vscode/
├── docs/
├── logs/
├── schemas/
├── scripts/
├── src/
│   └── portfolio_generator/
│       ├── cli/
│       ├── application/
│       │   ├── dto/
│       │   ├── services/
│       │   └── use_cases/
│       ├── domain/
│       │   ├── entities/
│       │   ├── value_objects/
│       │   ├── services/
│       │   ├── rules/
│       │   └── contracts/
│       ├── infrastructure/
│       │   ├── filesystem/
│       │   ├── git/
│       │   ├── parsers/
│       │   ├── exporters/
│       │   ├── ai/
│       │   └── config/
│       ├── shared/
│       └── main.py
├── test/
├── tmp/
├── pyproject.toml
├── README.md
└── objetivo.yaml
```

---

## 14. Fluxo Principal do Sistema

1. usuário executa a CLI;
2. argumentos são validados;
3. a raiz é validada contra a política de segurança;
4. o scanner localiza projetos candidatos;
5. cada projeto é enviado ao pipeline de análise;
6. metadados estruturados são coletados;
7. README é processado;
8. Git metadata é extraído;
9. resumo final é consolidado;
10. métricas são agregadas;
11. portfólio final é montado;
12. JSON é validado por schema;
13. arquivo final é salvo;
14. resumo de execução é apresentado ao usuário.

---

## 15. Critérios de Aceite

### CA-001
Dado um diretório válido dentro da raiz permitida, a CLI deve iniciar a análise sem erro crítico.

### CA-002
Dado um diretório fora da raiz permitida, o sistema deve rejeitar a operação com mensagem clara e log correspondente.

### CA-003
Dado um conjunto de projetos válidos, o sistema deve gerar um JSON consolidado e válido por schema.

### CA-004
Dado pelo menos um projeto com README adequado, o sistema deve extrair resumo ou descrição útil sem depender de IA.

### CA-005
Dado um projeto sem README útil, o sistema deve registrar fallback ou ausência de resumo sem quebrar a execução.

### CA-006
Dado um projeto com repositório Git, o sistema deve capturar metadados mínimos do repositório quando disponíveis.

### CA-007
Dado um lote contendo projetos válidos e inválidos, o sistema deve concluir a execução registrando falhas parciais.

### CA-008
A suíte automatizada deve atingir pelo menos 90% de cobertura.

### CA-009
A validação de lint, tipagem e testes deve fazer parte da rotina obrigatória de desenvolvimento.

---

## 16. Riscos Conhecidos

- heterogeneidade excessiva de projetos analisados;
- encodings inválidos;
- arquivos muito grandes;
- repositórios Git corrompidos;
- README inexistente ou mal estruturado;
- custo operacional de análise em árvores extensas;
- dependência opcional de serviços de IA;
- falso positivo na detecção de projeto.

---

## 17. Mitigações

- processamento incremental;
- limites configuráveis;
- timeouts lógicos por etapa, quando aplicável;
- fallback determinístico sem IA;
- logging detalhado;
- exclusões e filtros padrão;
- validação estrita de path;
- isolamento por projeto.

---

## 18. Decisões Técnicas Iniciais

1. Python 3.12+ como linguagem principal.
2. CLI baseada em `click`.
3. Logs com `loguru`.
4. Apresentação terminal com `rich`.
5. Arquitetura em camadas com DDD leve.
6. JSON final validado por schema versionado.
7. IA apenas como apoio opcional.
8. Qualidade obrigatória com lint, typing e testes.
9. Segurança de path como regra de domínio e infraestrutura.
10. Modularidade como requisito estrutural obrigatório.

---

## 19. Próximos Artefatos Derivados

Após esta especificação, devem ser gerados:

- `plan.md`
- `tasks.md`
- ADR inicial de arquitetura
- definição do schema final de saída
- esqueleto do pacote Python
- configuração de quality gates

---

## 20. Conclusão

Esta especificação define um padrão mínimo profissional para a construção do `portfolio-generator`, equilibrando robustez, segurança, modularidade, observabilidade e capacidade de evolução. O foco é entregar uma ferramenta confiável, extensível e adequada ao uso real, com baixa probabilidade de erro e bom alinhamento com práticas modernas de engenharia de software.