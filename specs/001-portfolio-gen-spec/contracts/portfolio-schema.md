# Portfolio JSON Schema Contract

**Schema file**: `schemas/portfolio-schema-v1.json`  
**Version**: v1  
**Created**: 2026-06-17

---

## Top-Level Structure

```json
{
  "generated_at": "2026-06-17T10:30:00Z",
  "generator_version": "1.0.0",
  "total_projects": 42,
  "skipped_projects": 2,
  "scan_duration_seconds": 8.4,
  "projects": [ ProjectEntry ]
}
```

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `generated_at` | string (ISO-8601) | ✅ | Timestamp da geração |
| `generator_version` | string (semver) | ✅ | Versão do portfolio-gen |
| `total_projects` | integer ≥ 0 | ✅ | Total de projetos catalogados |
| `skipped_projects` | integer ≥ 0 | ✅ | Total de projetos pulados por erro |
| `scan_duration_seconds` | number ≥ 0 | ✅ | Tempo total do scan |
| `projects` | array[ProjectEntry] | ✅ | Lista de entradas de projetos |

---

## ProjectEntry

```json
{
  "name": "portfolio-generator",
  "path": "portfolio-generator",
  "type": "cli-tool",
  "description": "CLI tool for automated project cataloging.",
  "description_source": "readme",
  "language": {
    "primary": "Python",
    "secondary": ["Bash", "YAML"],
    "confidence": 0.92
  },
  "metrics": {
    "file_count": 42,
    "line_count_estimated": 1200,
    "size_bytes": 184320
  },
  "git": {
    "initialized": true,
    "branch": "main",
    "last_commit_hash": "a48cd9c",
    "last_commit_date": "2026-06-17T10:00:00Z",
    "last_commit_author": "Yves Marinho",
    "commit_count": 87
  },
  "technologies": ["click", "pandas", "docker"],
  "status": "active",
  "last_modified": "2026-06-17T10:00:00Z"
}
```

### Campos obrigatórios

| Campo | Tipo | Valores válidos | Descrição |
|-------|------|----------------|-----------|
| `name` | string (não vazio) | — | Nome do diretório do projeto |
| `path` | string | path relativo | Caminho relativo ao diretório raiz |
| `type` | enum | `cli-tool`, `web-app`, `library`, `script`, `infrastructure`, `unknown` | Tipo inferido |
| `description` | string | — | Descrição (pode ser vazia se AI desativado e sem README) |
| `description_source` | enum | `readme`, `ai-generated`, `filename`, `empty` | Origem da descrição |
| `language.primary` | string | — | Linguagem principal detectada (`unknown` se não detectado) |
| `language.secondary` | array[string] | — | Linguagens secundárias (pode ser vazia) |
| `language.confidence` | number | 0.0 – 1.0 | Confiança na detecção |
| `metrics.file_count` | integer ≥ 0 | — | Total de arquivos (excluindo .git, node_modules) |
| `metrics.size_bytes` | integer ≥ 0 | — | Tamanho total em bytes |
| `git.initialized` | boolean | — | Se o projeto tem git inicializado |
| `technologies` | array[string] | — | Tecnologias detectadas (pode ser vazia) |
| `status` | enum | `active`, `archived`, `unknown` | Status inferido |
| `last_modified` | string (ISO-8601) | — | Data da última modificação |

### Campos opcionais (presentes somente quando disponíveis)

| Campo | Tipo | Condição |
|-------|------|---------|
| `metrics.line_count_estimated` | integer ≥ 0 | Quando cálculo de linhas for viável |
| `git.branch` | string | Quando git inicializado |
| `git.last_commit_hash` | string | Quando git inicializado e tem commits |
| `git.last_commit_date` | string (ISO-8601) | Quando git inicializado e tem commits |
| `git.last_commit_author` | string | Quando git inicializado e tem commits |
| `git.commit_count` | integer ≥ 0 | Quando git inicializado |

---

## Regras de Validação

1. `total_projects` DEVE ser igual ao `length` de `projects`
2. `description_source` de `"ai-generated"` REQUER `description` não vazio
3. `git.initialized: false` PROÍBE qualquer campo `git.*` adicional
4. `language.confidence` DEVE ser 0.0 quando `language.primary` é `"unknown"`
5. `path` DEVE ser relativo (sem `/` inicial ou path absoluto)
