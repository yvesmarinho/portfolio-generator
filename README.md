# 📂 Portfolio Generator

> Ferramenta CLI para análise automatizada de projetos e geração de portfólio profissional em formato JSON estruturado.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Domínio**: programming | **Linguagem**: python  
**Criado em**: 2026-05-18  
**Status**: 🟡 Em desenvolvimento (MVP)

---

## 🎯 Sobre o Projeto

O **Portfolio Generator** é uma ferramenta de análise automatizada que escaneia projetos de desenvolvimento, extrai metadados estruturados e gera um portfólio profissional consolidado em JSON.

### Propósito Dual

1. **Gerador de Portfólio** (Primário)
   - Escanear projetos em diretórios especificados
   - Extrair metadados: linguagens, dependências, estatísticas Git
   - Analisar README e documentação
   - Gerar JSON estruturado para publicação

2. **Validação do Enterprise Template** (Secundário)
   - Testar scaffolding automático
   - Validar rituais de sessão
   - Verificar configurações MCP e VS Code

---

## ✨ Funcionalidades (MVP)

- 🔍 **Scanner de Diretórios**: Varredura recursiva com filtros inteligentes
- 📊 **Extrator de Metadados**: Linguagens, dependências, estatísticas de código
- 📝 **Analisador de README**: Parser de Markdown com extração de seções
- 📦 **Gerador de JSON**: Exportação em JSON/YAML/Markdown
- 🎨 **CLI Interativo**: Progress bars, modo verbose/quiet

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes)
- Git

### Instalação

```bash
# Clonar repositório
git clone https://github.com/yvesmarinho/portfolio-generator.git
cd portfolio-generator

# Criar ambiente virtual
uv venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# Instalar dependências (quando pyproject.toml estiver pronto)
uv pip install -e ".[dev]"
```

### Uso Básico

```bash
# Gerar portfólio (após implementação)
portfolio-gen scan /caminho/para/projetos

# Modo verbose
portfolio-gen scan /caminho/para/projetos -vv

# Exportar em YAML
portfolio-gen scan /caminho/para/projetos --format yaml

# Dry-run (sem gerar arquivo)
portfolio-gen scan /caminho/para/projetos --dry-run
```

---

## 🏗️ Arquitetura

### Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.12+ |
| Package Manager | uv |
| CLI Framework | click |
| Logging | loguru |
| Progress/UI | rich |
| Linting | ruff |
| Testing | pytest (cobertura ≥90%) |

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
    ├── logging.py          # Configuração loguru
    ├── validators.py       # Validação de entrada
    └── config.py           # Gerenciamento de configs
```

### Bibliotecas Principais

```python
# Análise e processamento
pandas==2.2.0           # Manipulação de dados
gitpython==3.1.43      # Informações Git
tree-sitter==0.22.0    # Parser de código
pygments==2.17.2       # Detecção de linguagens

# CLI e UX
click==8.1.7           # Framework CLI
loguru==0.7.2          # Logging
rich==13.7.0           # Progress bars

# Parsing
pyyaml==6.0.1          # YAML
tomli==2.0.1           # TOML
```

---

## 📊 Schema do Portfólio

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
        "summary": "Rich description from README",
        "metadata": {
          "languages": ["Python", "JavaScript"],
          "dependencies": ["click", "pandas"],
          "stats": {
            "total_files": 150,
            "lines_of_code": 5000,
            "size_bytes": 2048000
          },
          "git": {
            "last_commit": "2026-05-18T10:00:00Z",
            "branch": "main",
            "total_commits": 120
          }
        }
      }
    ]
  }
}
```

Ver schema completo: [schemas/portfolio-schema-v1.json](schemas/portfolio-schema-v1.json)

---

## 📚 Documentação

- 📖 [Especificação Técnica](docs/PROJECT_SPECIFICATION.md) - Detalhamento completo do projeto
- 📋 [TODO](docs/TODO.md) - Tarefas e roadmap (22 tarefas identificadas)
- 📚 [Índice](docs/INDEX.md) - Mapa completo da documentação
- 📝 [Sessões](docs/SESSIONS/) - Histórico de desenvolvimento

---

## 🛠️ Desenvolvimento

### Comandos Disponíveis

```bash
make help              # Listar todos comandos
make test              # Executar testes
make lint              # Verificar código (ruff)
make format            # Formatar código
make clean             # Limpar arquivos gerados
```

### Regras de Desenvolvimento

- **SOLID**: Aplicar em todos os módulos
- **Type hints**: Obrigatório em todas funções
- **Docstrings**: Google Style em todas funções/classes
- **Testes**: Cobertura mínima de 90%
- **Logs**: Detalhados com loguru

Ver regras completas: [.copilot-rules-portfolio-generator.md](.copilot-rules-portfolio-generator.md)

---

## 🎯 Roadmap

### ✅ Fase 1: Inicialização (Concluída)
- [x] Setup do projeto
- [x] Configuração MCP e ambiente
- [x] Documentação inicial
- [x] Especificação técnica

### 🔵 Fase 2: SpecKit Workflow (Atual)
- [ ] Atualizar objetivo.yaml
- [ ] Gerar spec.md via SpecKit
- [ ] Criar plano de implementação
- [ ] Detalhar tarefas

### ⏳ Fase 3: Implementação MVP
- [ ] Scanner de Diretórios
- [ ] Extrator de Metadados
- [ ] Analisador de README
- [ ] Gerador de JSON
- [ ] CLI Interativo

### ⏳ Fase 4: Testes e Validação
- [ ] Suite de testes (≥90%)
- [ ] Validação com projetos reais
- [ ] Documentação de usuário

---

## 🤝 Contribuindo

Este projeto segue o [Enterprise Default Project Template](https://github.com/yvesmarinho/default-project).

### Workflow Git

```bash
# Criar branch de feature
git checkout -b 001-nome-da-feature

# Commits com mensagem estruturada
git commit -F /tmp/commit-msg.txt

# Nunca: git commit -m "..." (regra P0)
```

---

## 📄 Licença

MIT License - Ver [LICENSE](LICENSE)

---

## 👤 Autor

**Yves Marinho**
- GitHub: [@yvesmarinho](https://github.com/yvesmarinho)
- Projeto: Gerador de portfólio profissional automatizado

---

## 🙏 Agradecimentos

- Enterprise Default Project Template
- Comunidade Python
- Ferramentas: uv, ruff, click, rich, loguru

---

**Status do Projeto**: 🟡 MVP em desenvolvimento  
**Última atualização**: 2026-05-18
