# Portfolio Generator — Especificação do Projeto

> **Baseado em**: Análise de objetivo-init.yaml (2026-05-18)
> **Status**: Definição de requisitos concluída
> **Próximo passo**: Gerar spec.md via SpecKit

---

## 🎯 Propósito do Projeto

### Objetivo Dual

Este projeto serve a dois propósitos complementares:

1. **Gerador de Portfólio Profissional** (primário)
   - Escanear projetos em `/home/yves_marinho/Documentos/DevOps/`
   - Extrair metadados estruturados de cada projeto
   - Gerar arquivo JSON consolidado para publicação

2. **Validação do Enterprise Template** (secundário)
   - Testar processo de scaffolding automático
   - Validar rituais de sessão (`session-start-first`, `session-start`)
   - Verificar configurações de MCP e VS Code

---

## 📊 Especificação Técnica

### Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.12+ |
| Estilo de código | PEP 8 (Google Style docstrings) |
| Gerenciador de pacotes | uv |
| Linting | ruff |
| Type hints | Obrigatório em todas funções públicas |
| Cobertura de testes | Mínimo 90% |
| Framework CLI | click |
| Logging | loguru |
| Progress/UI | rich |

### Bibliotecas Principais

#### Análise Local (sem IA) — Abordagem Recomendada

```python
# Essenciais
pandas==2.2.0           # Manipulação de dados
pathlib                 # (built-in) Navegação de arquivos
tomli==2.0.1           # Parser TOML (pyproject.toml)
pyyaml==6.0.1          # Parser YAML
gitpython==3.1.43      # Informações do Git

# Análise de código
tree-sitter==0.22.0    # Parser de código (multi-linguagem)
pygments==2.17.2       # Detecção de linguagens
chardet==5.2.0         # Detecção de encoding

# CLI e UX
click==8.1.7           # Framework CLI
loguru==0.7.2          # Logging
rich==13.7.0           # Progress bars e formatação
```

#### IA Opcional (apenas para resumos)

```python
# Opcional - apenas se README não existir
anthropic==0.23.1      # Claude 3.5 Sonnet
tiktoken==0.6.0        # Contagem de tokens
```

**Decisão**: Iniciar sem IA, adicionar incrementalmente se necessário.

### Volume de Dados

- **Estimativa**: 1-10 GB de código-fonte
- **Tempo de processamento esperado**: 5-15 minutos (análise local)

---

## 🏗️ Arquitetura

### Princípios de Design

- **SOLID**: Aplicar em todos os módulos
- **Design Patterns**: Factory, Strategy, Builder conforme necessário
- **Modularização**: Separação por responsabilidades
- **Arquivos pequenos**: Evitar classes/arquivos > 300 linhas

### Estrutura de Módulos

```
src/
├── core/                    # Lógica de negócio
│   ├── scanner.py          # Varredura de diretórios
│   ├── extractor.py        # Extração de metadados
│   ├── analyzer.py         # Análise de README/código
│   └── generator.py        # Geração de JSON
├── api/                     # Interface CLI
│   └── cli.py              # Comandos do portfolio-gen
└── shared/                  # Utilitários
    ├── logging.py          # Configuração do loguru
    ├── validators.py       # Validação de entrada
    └── config.py           # Gerenciamento de configurações
```

---

## ✅ Funcionalidades MVP

### 1. Scanner de Diretórios
- Varredura recursiva com filtros por extensão
- Respeito a `.gitignore` e padrões de exclusão
- Progress bar durante scan
- Detecção automática de tipo de projeto (Python, Node.js, etc.)

### 2. Extrator de Metadados
- **Dados estruturados**:
  - Nome do projeto (pasta raiz)
  - Linguagens de programação detectadas (via Pygments)
  - Dependências (package.json, requirements.txt, pyproject.toml)
  - Estatísticas: total de arquivos, linhas de código, tamanho
  - Informações Git: último commit, branch, número de commits
  - Data de criação/modificação

### 3. Analisador de README
- Parser de README.md
- Extração de título, descrição, badges
- Identificação de seções (Installation, Usage, etc.)
- Fallback: análise de docstrings se README ausente

### 4. Gerador de JSON
- Schema definido (ver `schemas/portfolio-schema-v1.json`)
- Validação contra schema antes de exportar
- Opções de formato:
  - JSON minificado (produção)
  - JSON pretty (debug)
  - YAML (alternativa)
  - Markdown (relatório legível)

### 5. CLI Interativo
- Progress bars (rich)
- Modo verbose (`-v`, `-vv`) e quiet (`-q`)
- Output configurável (`--format json|yaml|md`)
- Dry-run mode (`--dry-run`)

---

## 📋 Regras de Desenvolvimento

### Regras P0 (Críticas)

1. **Validação de entrada**: Todas entradas de usuário devem ser validadas
2. **Type hints**: Obrigatório em todas funções e classes
3. **Documentação**: Docstrings Google Style em todas funções/classes
4. **Headers**: Detalhes em cada arquivo de código
5. **Configuração externa**: Dados sensíveis em `.secrets/`, nunca hardcoded
6. **Idempotência**: Múltiplas execuções devem produzir mesmo resultado
7. **Performance**: Respeitar recursos da máquina, evitar travamentos

### Regras P1 (Importantes)

1. Linting obrigatório antes de commit (`ruff check`)
2. Cobertura de testes mínima: 90%
3. Logs detalhados com loguru mostrando fluxo do programa
4. AST parsing para análise de código (não regex)
5. Módulos com responsabilidades bem definidas

---

## 🎯 Critérios de Sucesso

### Funcionais

1. ✅ Sistema capaz de analisar 50+ projetos e gerar resumo com informações de qualidade
2. ✅ JSON gerado contém: nome, tipo, resumo rico, metadados completos
3. ✅ Execução respeita recursos da máquina (sem travamentos)
4. ✅ Tempo de processamento: < 5 minutos para 1-10 GB

### Entregáveis

1. ✅ Ferramenta CLI funcional (`portfolio-gen`)
2. ✅ Documentação completa em `docs/`
3. ✅ Suite de testes com 90%+ cobertura
4. ✅ Relatório de validação do Enterprise Template

### Caso de Uso de Demonstração

**Target**: Gerar portfólio de projetos Python da pasta:
```
/home/yves_marinho/Documentos/DevOps/Vya-Jobs/enterprise-python-snippets
```

---

## 🛠️ Infraestrutura

### Ambiente

| Item | Especificação |
|------|---------------|
| SO | Linux Mint |
| Python | 3.12+ |
| Package manager | uv |
| IDE | VS Code |
| Git workflow | Feature branches (conforme .copilot-rules.md) |

### Dependências Externas

- ✅ Acesso à internet: Opcional (apenas para IA)
- ❌ Banco de dados: Não necessário
- ❌ Cache/Storage: Apenas disco local
- ❌ Message Queue: N/A

### Deploy

- **Modo**: Script local (execução direta via `uv run`)
- **Distribuição**: Repositório Git (sem publicação em PyPI por enquanto)

### Segurança

- Secrets em `.secrets/` (já no `.gitignore`)
- Validação de caminhos (restringir a `/home/yves_marinho/Documentos/DevOps/`)
- Nenhum processamento de arquivos fora do escopo definido

### Observabilidade

- **Logging**: loguru com níveis DEBUG/INFO/WARNING/ERROR
- **Métricas**: N/A
- **Tracing**: N/A
- **Alertas**: N/A

---

## 📦 Schema do JSON de Portfólio

Ver arquivo completo em: [schemas/portfolio-schema-v1.json](../../schemas/portfolio-schema-v1.json)

**Estrutura básica**:
```json
{
  "portfolio": {
    "generated_at": "2026-05-18T20:00:00Z",
    "total_projects": 42,
    "projects": [
      {
        "name": "project-name",
        "path": "/absolute/path",
        "type": "python",
        "summary": "Rich description",
        "metadata": {
          "languages": ["Python"],
          "dependencies": [...],
          "stats": {...},
          "git": {...}
        }
      }
    ]
  }
}
```

---

## 🚀 Próximos Passos

1. ✅ Questionário de objetivo-init.yaml completado
2. ⏳ Atualizar `objetivo.yaml` com decisões tomadas
3. ⏳ Executar `speckit.specify` para gerar `spec.md`
4. ⏳ Executar `speckit.plan` para gerar plano de implementação
5. ⏳ Executar `speckit.tasks` para gerar tarefas detalhadas
6. ⏳ Iniciar implementação

---

**Documento criado**: 2026-05-18  
**Baseado em**: tmp/2026-05-18/RESUMO_ANALISE.md, QUESTIONARIO_OBJETIVO_INIT.md, ORIENTACOES_COPILOT.md  
**Autor**: GitHub Copilot (Claude Sonnet 4.5)  
**Versão**: 1.0
