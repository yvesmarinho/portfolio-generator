# Data Model: Portfolio Generator CLI

**Created**: 2026-06-18
**Updated**: 2026-06-18 (adicionado ScanConfig com exclusions_file)
**Feature**: [spec.md](spec.md)

---

## Entidades Principais

### Project

Representa um único projeto — um subdiretório imediato do diretório alvo.

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `name` | `str` | ✅ | Nome do diretório do projeto |
| `path` | `Path` | ✅ | Caminho absoluto (interno; não serializado no JSON) |
| `type` | `str` | ✅ | Tipo inferido: `"python"`, `"node"`, `"go"`, `"infra"`, `"unknown"` |
| `description` | `str \| None` | — | Descrição em texto livre |
| `description_source` | `str` | ✅ | `"readme"`, `"ai-generated"`, `"ai-unavailable"`, `"filename"` |
| `language` | `LanguageInfo` | ✅ | Resultado da cascata de detecção de linguagem |
| `metrics` | `ProjectMetrics` | ✅ | Métricas quantitativas |
| `git` | `GitInfo \| None` | — | Metadados de controle de versão (None se sem git) |
| `technologies` | `list[str]` | ✅ | Lista de tecnologias detectadas (frameworks, tools) |
| `last_modified` | `datetime` | ✅ | Data da última modificação em disco |

**Regras de validação**:
- `name` não pode ser vazio
- `type` deve ser um dos valores enumerados
- `description_source` deve ser um dos valores enumerados
- `last_modified` deve ser timezone-aware (UTC)

---

### LanguageInfo

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `primary` | `str` | Linguagem principal (ex: `"Python"`) |
| `secondary` | `list[str]` | Linguagens secundárias detectadas |
| `confidence` | `float` | Score de confiança: 0.0–1.0 |
| `detection_level` | `int` | Nível da cascata usado: 1 (extensão), 2 (pygments), 3 (tree-sitter) |

---

### ProjectMetrics

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `file_count` | `int` | Total de arquivos no projeto |
| `line_count_estimated` | `int` | Linhas estimadas (amostragem) |
| `size_bytes` | `int` | Tamanho total em bytes |

---

### GitInfo

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `initialized` | `bool` | True se o diretório tem `.git/` |
| `branch` | `str \| None` | Branch atual |
| `last_commit_hash` | `str \| None` | SHA do último commit (7 chars) |
| `last_commit_date` | `datetime \| None` | Data do último commit (UTC) |
| `last_commit_author` | `str \| None` | Nome do autor do último commit |
| `commit_count` | `int \| None` | Total de commits no branch atual |

---

### PortfolioCatalog

O artefato de saída completo — serializado em JSON.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `generated_at` | `datetime` | Timestamp de geração (UTC, ISO-8601) |
| `generator_version` | `str` | Versão do `portfolio-gen` |
| `total_projects` | `int` | Total de projetos catalogados |
| `projects` | `list[Project]` | Entradas de cada projeto |

---

### ExecutionReport

Sumário de execução (exibido no terminal e salvo em log).

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `scanned` | `int` | Projetos processados com sucesso |
| `skipped` | `int` | Projetos pulados por erro |
| `ai_used` | `int` | Projetos que usaram IA para descrição |
| `elapsed_seconds` | `float` | Tempo total de execução |
| `output_path` | `Path \| None` | Caminho do arquivo gerado (None em dry-run) |

---

### ScanConfig

Configuração de execução do scan — lida do CLI e do arquivo de exclusões.

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `root_path` | `Path` | `/home/.../DevOps/` | Diretório raiz dos projetos |
| `output_path` | `Path \| None` | `output/portfolio-YYYY-MM-DD.json` | Saída JSON |
| `workers` | `int` | `min(4, cpu_count())` | Workers paralelos |
| `dry_run` | `bool` | `False` | Não escrever arquivos |
| `no_ai` | `bool` | `False` | Desativar IA |
| `ai_min_words` | `int` | `30` | Mínimo de palavras para não usar IA |
| `ai_max_tokens` | `int` | `2000` | Máximo de tokens antes de usar IA para resumo |
| `exclusions_file` | `Path` | `config/scan-exclusions.json` | Arquivo JSON de pastas excluídas |
| `excluded_dirs` | `list[str]` | `DEFAULT_EXCLUSIONS` | Lista resolvida de exclusões (carregada do arquivo ou fallback) |

**Regras de resolução de exclusões**:
1. Se `--exclusions-file` fornecido, carregar desse path
2. Senão, tentar `config/scan-exclusions.json` na raiz do projeto
3. Se nenhum existir, usar `DEFAULT_EXCLUSIONS` embutido no código

---

## Transições de Estado — Descrição de Projeto

```
[sem README] ──────────────────────────────► use_ai=True
[README < ai_min_words] ───────────────────► use_ai=True
[README > ai_max_tokens tokens] ───────────► use_ai=True
[README adequado] ──────────────────────────► use_readme=True
[--no-ai flag] + [sem README adequado] ────► description="" (source="ai-unavailable")
[IA indisponível] + [sem README adequado] ─► description="" (source="ai-unavailable")
```

---

## Schema JSON de Saída (referência)

Ver [contracts/portfolio-schema.md](contracts/portfolio-schema.md) para o schema completo validado pelo `jsonschema`.
