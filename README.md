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
source .venv/bin/activate  # Linux/macOS

# Instalar dependências
uv pip install -e ".[dev]"

# Verificar instalação
portfolio-gen --version
```

### Uso Básico

```bash
# Prévia sem gravar arquivo (dry-run)
portfolio-gen scan --dry-run

# Escanear projetos e gerar portfólio JSON
portfolio-gen scan --path ~/Documentos/DevOps/

# Escanear com 4 workers paralelos
portfolio-gen scan --workers 4

# Validar portfólio gerado
portfolio-gen validate output/portfolio-2026-06-17.json

# Validar com detalhes
portfolio-gen validate output/portfolio-2026-06-17.json --verbose
```

> Guia completo: [docs/quickstart.md](docs/quickstart.md)

---

## 🏗️ Arquitetura

### Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Linguagem | Python 3.13+ |
| Package Manager | uv |
| CLI Framework | click |
| Logging | loguru |
| Progress/UI | rich |
| Linting | ruff |
| Validação de schema | jsonschema |
| Detecção de linguagem | pygments |
| Info Git | gitpython |
| Testing | pytest + coverage (≥96%) |

### Estrutura de Módulos

```
src/
├── analyzer/               # Análise de README e metadados textuais
│   └── readme_parser.py
├── cli/                    # Interface de linha de comando
│   ├── main.py             # Subcomandos: scan, validate, report
│   └── _logging.py         # Configuração loguru
├── extractor/              # Extração de metadados por projeto
│   ├── git_extractor.py
│   ├── language_extractor.py
│   ├── metadata_extractor.py
│   └── metrics_extractor.py
├── generator/              # Geração e validação do JSON de saída
│   └── portfolio_generator.py
└── scanner/                # Varredura de diretórios com scope guard
    └── directory_scanner.py
```

### Decisões de Arquitetura

Consulte os ADRs em [docs/architecture/adr/](docs/architecture/adr/):

- **ADR-001**: ProcessPoolExecutor vs asyncio para paralelismo
- **ADR-002**: Cascata de 3 níveis para detecção de linguagem
- **ADR-003**: Estrutura JSON aninhada vs. plana

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
