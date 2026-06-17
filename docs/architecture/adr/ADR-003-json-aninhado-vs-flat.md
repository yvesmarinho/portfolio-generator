# ADR-003 — Estrutura JSON aninhada vs. plana para o portfólio

**Status**: Aceito  
**Data**: 2026-06-17  
**Decisores**: yves_marinho

---

## Contexto

O JSON de saída do `portfolio-gen` pode organizar os dados de cada projeto de
duas formas principais:

**Flat** — todos os campos no mesmo nível:
```json
{
  "name": "meu-projeto",
  "language_primary": "Python",
  "language_secondary": ["YAML"],
  "language_confidence": 0.95,
  "git_initialized": true,
  "git_branch": "main",
  "metrics_file_count": 42
}
```

**Aninhado** — campos agrupados por domínio:
```json
{
  "name": "meu-projeto",
  "language": { "primary": "Python", "secondary": ["YAML"], "confidence": 0.95 },
  "git": { "initialized": true, "branch": "main" },
  "metrics": { "file_count": 42 }
}
```

## Decisão

Adotamos **estrutura aninhada** conforme definido em `schemas/portfolio-schema-v1.json`.

## Justificativa

- **Legibilidade**: grupos de campos relacionados ficam agrupados visualmente.
- **Extensibilidade**: adicionar `git.commit_count` ou `language.dialect` não
  exige reorganização do schema nem quebra clientes existentes.
- **Interoperabilidade**: ferramentas de front-end (dashboards, APIs REST) operam
  naturalmente com objetos aninhados; JSON Pointer (`$`-paths) funciona melhor.
- **Validação**: `jsonschema.Draft7Validator` representa melhor objetos aninhados
  com `$ref` e definições reutilizáveis.

## Consequências

- **Positivo**: schema versionado e extensível; erros de validação têm JSON paths
  claros (ex.: `$.projects[0].language.primary`).
- **Negativo**: queries analíticas simples (ex.: SQL sobre CSV exportado) requerem
  achatamento (flatten) dos campos. Ferramentas como `jq` e `pandas.json_normalize`
  tratam isso nativamente.
- **Compatibilidade**: o schema é versionado em `generator_version`. Mudanças
  breaking exigem um novo schema (v2) com migração opcional.
