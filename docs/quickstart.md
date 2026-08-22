# Quickstart — portfolio-gen

Guia de início rápido para instalar, configurar e usar o `portfolio-gen` em menos de 5 minutos.

---

## Pré-requisitos

| Ferramenta | Versão mínima | Verificação |
|---|---|---|
| Python | 3.12 | `python --version` |
| uv | 0.4+ | `uv --version` |
| Git | 2.x | `git --version` |

---

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/yvesmarinho/portfolio-generator.git
cd portfolio-generator

# 2. Criar e ativar ambiente virtual
uv venv
source .venv/bin/activate  # Linux/macOS

# 3. Instalar dependências
uv pip install -e ".[dev]"

# 4. Verificar instalação
portfolio-gen --version
```

---

## Uso básico

### Escanear projetos (dry-run — sem criar arquivos)

```bash
portfolio-gen scan --dry-run
```

Saída esperada: tabela Rich com contagem de projetos, tamanho estimado do JSON
e número de projetos elegíveis para enriquecimento por IA.

### Escanear e gerar portfólio JSON

```bash
portfolio-gen scan --path ~/Documentos/DevOps/
```

O arquivo é salvo em `output/portfolio-YYYY-MM-DD.json`.

### Escanear com paralelismo customizado

```bash
portfolio-gen scan --workers 4
```

### Validar portfólio existente

```bash
portfolio-gen validate output/portfolio-2026-06-17.json
```

Saída em caso de sucesso:
```
✓ Portfolio válido — portfolio-2026-06-17.json
```

Saída em caso de violações:
```
✗ Portfolio inválido — 2 violação(ões) em portfolio-2026-06-17.json
Path JSON         Violação
$.total_projects  'nao-e-inteiro' is not of type 'integer'
```

### Validar com schema alternativo

```bash
portfolio-gen validate output/portfolio.json --schema schemas/portfolio-schema-v2.json
```

---

## Opções globais

| Flag | Descrição |
|---|---|
| `--verbose` / `-v` | Exibe logs DEBUG no terminal |
| `--version` | Exibe versão do CLI |
| `--help` | Exibe ajuda |

---

## Estrutura do portfólio gerado

```json
{
  "generated_at": "2026-06-17T10:00:00+00:00",
  "generator_version": "1.0.0",
  "scan_path": "/home/usuario/Documentos/DevOps/",
  "total_projects": 42,
  "skipped_projects": 0,
  "scan_duration_seconds": 12.3,
  "projects": [
    {
      "name": "meu-projeto",
      "path": "/home/usuario/Documentos/DevOps/meu-projeto",
      "type": "api-service",
      "description": "Serviço REST para gerenciamento de pedidos.",
      "description_source": "readme",
      "language": { "primary": "Python", "secondary": ["YAML"], "confidence": 0.95 },
      "metrics": { "file_count": 42, "size_bytes": 153600, "line_count_estimated": 1200 },
      "git": { "initialized": true, "branch": "main", "last_commit_hash": "abc1234",
               "last_commit_date": "2026-06-01T10:00:00+00:00",
               "last_commit_author": "Dev Name", "commit_count": 85 },
      "technologies": ["Python/uv", "Docker", "GitHub Actions"],
      "status": "active",
      "last_modified": "2026-06-01T10:00:00+00:00"
    }
  ]
}
```

---

## Solução de problemas

### `portfolio-gen: command not found`

O ambiente virtual não está ativado. Execute `source .venv/bin/activate`.

### `Erro: path fora do escopo permitido`

O `--path` deve estar dentro de `/home/yves_marinho/Documentos/DevOps/`.
Esse limite de segurança previne varredura de áreas sensíveis do sistema.

### `Erro: schema não encontrado`

Execute o comando a partir da raiz do projeto (onde `schemas/` está localizado),
ou passe `--schema caminho/para/portfolio-schema-v1.json`.

### Projetos pulados (skipped)

Verifique os relatórios em `docs/bugs/bug-report-*.md` e os logs em `logs/scan-YYYY-MM-DD.log`.
