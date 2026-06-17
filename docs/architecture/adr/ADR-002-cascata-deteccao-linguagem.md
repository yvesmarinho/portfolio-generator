# ADR-002 — Cascata de 3 níveis para detecção de linguagem

**Status**: Aceito  
**Data**: 2026-06-17  
**Decisores**: yves_marinho

---

## Contexto

Determinar a linguagem principal de um projeto a partir dos arquivos presentes
é um problema com soluções de custo e precisão variáveis. As abordagens avaliadas:

1. **Contagem de extensões** — rápida, zero dependências externas.
2. **Pygments** — análise de conteúdo real dos arquivos; mais precisa.
3. **tree-sitter** — parsers completos por linguagem; máxima precisão, alto custo.
4. **GitHub Linguist** — requer Ruby; impraticável como dependência Python.

## Decisão

Implementamos uma **cascata de 3 níveis** com limiar de confiança (`CONFIDENCE_THRESHOLD = 0.60`):

```
Nível 1: Contagem de extensões
    └── confiança ≥ 0.60 → resultado final
    └── confiança < 0.60 → Nível 2

Nível 2: Confirmação via Pygments
    └── resultados de Pygments → resultado final
    └── falha ou vazio → resultado do Nível 1 com confiança original

Nível 3: tree-sitter (reservado para versões futuras)
```

## Justificativa

- **Nível 1** é O(n_files) sem I/O extra além de `rglob`. Cobre 90% dos projetos
  com uma única linguagem dominante.
- **Nível 2** (Pygments) é acionado apenas quando a confiança é baixa (projetos
  poliglota ou de infraestrutura). O custo é justificado porque a classificação
  incorreta prejudica a utilidade do portfólio.
- **Nível 3** (tree-sitter) não foi implementado no MVP. Seria ativado quando Pygments
  também diverge do Nível 1 com confiança insuficiente.

## Consequências

- **Positivo**: desempenho excelente no caso comum; precisão adicional quando necessário.
- **Negativo**: `pygments` é uma dependência obrigatória (não opcional), mesmo que
  seja chamado raramente.
- **Testabilidade**: `_confirm_with_pygments` é testado diretamente como função
  privada; mock de `pygments.lexers.guess_lexer_for_filename` cobre todos os ramos.
