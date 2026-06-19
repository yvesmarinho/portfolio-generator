# CLI Contract: portfolio-gen

**Tool name**: `portfolio-gen`  
**Version**: 1.0.0  
**Created**: 2026-06-17

---

## Subcommands

### `portfolio-gen scan`

Escaneia o diretório alvo e gera o arquivo de portfólio.

```
portfolio-gen scan [OPTIONS]

Options:
  --path PATH          Diretório raiz dos projetos
                       Default: /home/yves_marinho/Documentos/DevOps/
                       Deve estar dentro do escopo permitido.

  --output PATH        Caminho do arquivo JSON de saída
                       Default: output/portfolio-YYYY-MM-DD.json

  --workers INTEGER    Número máximo de workers paralelos
                       Default: min(4, cpu_count())
                       Range: 1–16

  --no-ai              Desativar geração de descrição via IA
                       Projetos sem README adequado ficam com descrição vazia

  --ai-min-words INT   Mínimo de palavras no README para não usar IA
                       Default: 30

  --ai-max-tokens INT  Máximo de tokens no README antes de usar IA para resumo
                       Default: 2000

  --exclusions-file PATH  Arquivo JSON com lista de pastas a excluir do scan
                          Default: config/scan-exclusions.json
                          Se não existir, usa lista padrão embutida.
                          Schema esperado: {"excluded_dirs": ["pasta1", "pasta2"]}

  --dry-run            Rodar análise completa sem escrever nenhum arquivo
  --verbose / --quiet  Nível de output no terminal
  --help               Exibir ajuda com exemplos

Exit codes:
  0  Sucesso — arquivo gerado e validado
  1  Erro crítico (diretório não encontrado, schema inválido, exclusions-file inválido)
  2  Sucesso com avisos (projetos pulados por erro)
```

**Exemplo**:
```bash
portfolio-gen scan --path ~/Documentos/DevOps/ --workers 2 --verbose
portfolio-gen scan --no-ai --dry-run
portfolio-gen scan --exclusions-file config/my-exclusions.json
```

---

### `portfolio-gen validate`

Valida um arquivo de portfólio existente contra o schema publicado.

```
portfolio-gen validate [OPTIONS] FILE

Arguments:
  FILE  Caminho para o arquivo JSON de portfólio a validar

Options:
  --schema PATH  Schema JSON alternativo (default: schemas/portfolio-schema-v1.json)
  --verbose      Exibir detalhe de cada campo validado
  --help         Exibir ajuda

Exit codes:
  0  Válido
  1  Inválido — lista de violações exibida no stderr
```

**Exemplo**:
```bash
portfolio-gen validate output/portfolio-2026-06-17.json
portfolio-gen validate output/portfolio-2026-06-17.json --verbose
```

---

### `portfolio-gen report`

Exibe um relatório legível do portfólio em tabela Rich.

```
portfolio-gen report [OPTIONS] FILE

Arguments:
  FILE  Caminho para o arquivo JSON de portfólio

Options:
  --format [table|json|csv]  Formato de saída (default: table)
  --top INTEGER              Exibir apenas os N primeiros projetos
  --sort-by [name|language|size|date]  Ordenar por (default: name)
  --help  Exibir ajuda

Exit codes:
  0  Sucesso
  1  Arquivo não encontrado ou inválido
```

**Exemplo**:
```bash
portfolio-gen report output/portfolio-2026-06-17.json
portfolio-gen report output/portfolio-2026-06-17.json --format csv --top 20
```

---

## Terminal Output Contract

### Progress (scan em execução)
```
Scanning projects... ████████░░░░░░░░ 45/120 [00:08] project-name
```

### Summary (após conclusão)
```
✅ Portfolio generated: output/portfolio-2026-06-17.json
   Projects: 118 cataloged, 2 skipped
   AI descriptions: 12 generated
   Time: 8.4s | Size: 2.1 MB
   Warnings: see logs/scan-20260617.log
```

### Error messages
```
❌ Error: Directory not found: /path/to/dir
❌ Error: Path outside allowed scope. Only /home/yves_marinho/Documentos/DevOps/ is allowed.
⚠ Warning: Skipped project-name (corrupted git history) — see docs/bugs/
```
