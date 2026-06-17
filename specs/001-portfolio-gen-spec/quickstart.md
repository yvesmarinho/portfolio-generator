# Developer Quick-Start: portfolio-generator

**Created**: 2026-06-17  
**Target**: Desenvolvedor configurando o ambiente pela primeira vez

---

## Pré-requisitos

```bash
python3 --version   # ≥ 3.12
uv --version        # ≥ 0.11
git --version       # ≥ 2.30
```

---

## Setup (< 2 minutos)

```bash
# 1. Clonar e entrar no diretório
git clone <repo-url> portfolio-generator
cd portfolio-generator

# 2. Criar ambiente virtual e instalar dependências
uv sync

# 3. (Opcional) Configurar API Anthropic para descrições via IA
mkdir -p .secrets
cat > .secrets/api_config.json << 'EOF'
{
  "token": "sk-ant-...",
  "model": "claude-sonnet-4-6"
}
EOF

# 4. Verificar instalação
uv run portfolio-gen --help
```

---

## Primeiro uso

```bash
# Scan com dry-run (sem criar arquivos)
uv run portfolio-gen scan --dry-run --verbose

# Scan real (gera output/portfolio-YYYY-MM-DD.json)
uv run portfolio-gen scan

# Validar output gerado
uv run portfolio-gen validate output/portfolio-$(date +%Y-%m-%d).json

# Ver relatório em tabela
uv run portfolio-gen report output/portfolio-$(date +%Y-%m-%d).json
```

---

## Rodar testes

```bash
# Suite completa
uv run pytest

# Com cobertura (deve ser ≥ 90%)
uv run pytest --cov=src --cov-report=term-missing

# Apenas testes unitários (mais rápido)
uv run pytest tests/unit/

# Testes de integração
uv run pytest tests/integration/
```

---

## Linting e qualidade

```bash
# Formatação
uv run black src/ tests/

# Linting
uv run ruff check src/ tests/

# Type checking
uv run mypy src/ --strict

# Security scan
uv run bandit -r src/

# Todos de uma vez
make lint
```

---

## Makefile targets

```bash
make setup      # uv sync + pre-commit install
make test       # pytest --cov
make lint       # black + ruff + mypy + bandit
make run        # portfolio-gen scan (com configurações default)
make clean      # remover output/ e logs/
```

---

## Estrutura de arquivos relevantes

| Arquivo | Propósito |
|---------|-----------|
| `src/cli/main.py` | Entry point do CLI (click app) |
| `src/scanner/directory_scanner.py` | Lógica de varredura de diretórios |
| `src/extractor/language_extractor.py` | Cascata de detecção de linguagem |
| `src/generator/portfolio_generator.py` | Geração e validação do JSON |
| `schemas/portfolio-schema-v1.json` | Schema de validação do output |
| `.secrets/api_config.json` | Credenciais da API Anthropic (não versionado) |
| `pyproject.toml` | Configuração do projeto, dependências, ferramentas |

---

## Variáveis de ambiente (alternativa a .secrets/)

Não suportado em v1. Toda configuração sensível via `.secrets/api_config.json`.

---

## Troubleshooting

**`ModuleNotFoundError: tree_sitter`**  
→ Reinstalar: `uv sync --reinstall tree-sitter`; se falhar, a cascata de detecção usa apenas
extensões e pygments (nível 3 desativado automaticamente).

**`Permission denied: /path/outside/scope`**  
→ O tool só processa `/home/yves_marinho/Documentos/DevOps/`. Verifique o parâmetro `--path`.

**`Error: .secrets/api_config.json not found`** (quando usando IA)  
→ Crie o arquivo conforme seção "Setup" acima, ou use `--no-ai` para desativar.
