# ADR-001 — ProcessPoolExecutor vs asyncio para paralelismo do scan

**Status**: Aceito  
**Data**: 2026-06-17  
**Decisores**: yves_marinho

---

## Contexto

O comando `scan` precisa extrair metadados de dezenas a centenas de projetos
em paralelo. As opções principais avaliadas foram:

1. **`concurrent.futures.ProcessPoolExecutor`** — paralelismo real via múltiplos processos.
2. **`asyncio` + executores** — event loop não-bloqueante para I/O.
3. **`ThreadPoolExecutor`** — threads compartilhando o GIL do CPython.

## Decisão

Adotamos `ProcessPoolExecutor` com número de workers configurável (`--workers`,
padrão `min(4, cpu_count())`).

## Justificativa

| Critério | ProcessPool | asyncio | ThreadPool |
|---|---|---|---|
| Paralelismo real (CPU-bound) | ✅ | ❌ (GIL) | ❌ (GIL) |
| Isolamento de falhas por projeto | ✅ | ❌ | ❌ |
| Complexidade de código | Média | Alta | Baixa |
| Compatibilidade com mocks de teste | ⚠️ Requer ThreadPool em testes | ✅ | ✅ |

A extração de metadados inclui leitura de disco, execução de git e análise
de linguagens — todas com componente CPU-bound relevante. O isolamento por
processo protege o processo principal de crashes em projetos corrompidos.

## Consequências

- **Positivo**: paralelismo real; falha em um projeto não interrompe outros.
- **Negativo**: objetos passados entre processos devem ser serializáveis (pickle).
  Solução adotada: `functools.partial(scan_project, bug_report_dir=...)` em vez
  de lambda (lambda não é picklável).
- **Testabilidade**: nos testes, substituímos por `ThreadPoolExecutor` via
  `patch("cli.main.ProcessPoolExecutor", ThreadPoolExecutor)` para que mocks
  funcionem dentro do mesmo processo.
