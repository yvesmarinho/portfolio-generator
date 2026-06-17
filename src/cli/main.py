"""
CLI principal do portfolio-gen.

Entry point: portfolio-gen (definido em pyproject.toml [project.scripts])

Subcomandos:
  scan      — escaneia diretório e gera portfolio JSON
  validate  — valida arquivo de portfolio contra o schema
  report    — exibe relatório legível do portfolio
"""
from __future__ import annotations

import click
from rich.console import Console

from cli._logging import configure_logging

console = Console()

DEFAULT_SCAN_PATH = "/home/yves_marinho/Documentos/DevOps/"
ALLOWED_SCOPE = "/home/yves_marinho/Documentos/DevOps/"


@click.group()
@click.version_option(version="1.0.0", prog_name="portfolio-gen")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Modo verbose: exibe logs DEBUG no terminal",
)
def cli(verbose: bool) -> None:
    """
    portfolio-gen — Gerador automatizado de portfólio profissional.

    Escaneia projetos DevOps e gera um catálogo JSON estruturado com
    metadados, métricas de código, tecnologias e informações Git.

    Exemplos:

    \b
      portfolio-gen scan --dry-run
      portfolio-gen scan --path ~/Documentos/DevOps/ --workers 4
      portfolio-gen validate output/portfolio-2026-06-17.json
      portfolio-gen report output/portfolio-2026-06-17.json
    """
    configure_logging(verbose=verbose)


@cli.command()
@click.option(
    "--path",
    default=DEFAULT_SCAN_PATH,
    show_default=True,
    type=click.Path(exists=False),
    help=f"Diretório raiz dos projetos. Deve estar em {ALLOWED_SCOPE}",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(),
    help="Caminho do arquivo JSON de saída. Default: output/portfolio-YYYY-MM-DD.json",
)
@click.option(
    "--workers",
    default=None,
    type=click.IntRange(1, 16),
    help="Número de workers paralelos. Default: min(4, cpu_count())",
)
@click.option("--no-ai", is_flag=True, default=False, help="Desativar descrição via IA")
@click.option("--ai-min-words", default=30, show_default=True, help="Mínimo de palavras no README para não usar IA")
@click.option("--ai-max-tokens", default=2000, show_default=True, help="Máximo de tokens no README antes de usar IA")
@click.option("--dry-run", is_flag=True, default=False, help="Executar análise sem criar arquivos")
def scan(
    path: str,
    output: str | None,
    workers: int | None,
    no_ai: bool,
    ai_min_words: int,
    ai_max_tokens: int,
    dry_run: bool,
) -> None:
    """
    Escaneia o diretório alvo e gera o arquivo de portfólio JSON.

    Exemplos:

    \b
      portfolio-gen scan
      portfolio-gen scan --path ~/Documentos/DevOps/ --workers 2
      portfolio-gen scan --no-ai --dry-run
    """
    console.print("[yellow]⚠ Módulo scan ainda não implementado (Phase 3)[/yellow]")
    console.print(f"  path={path}, dry_run={dry_run}, workers={workers}, no_ai={no_ai}")
    raise SystemExit(0)


@cli.command()
@click.argument("file", type=click.Path(exists=False))
@click.option(
    "--schema",
    default="schemas/portfolio-schema-v1.json",
    show_default=True,
    type=click.Path(),
    help="Schema JSON alternativo para validação",
)
@click.option("--verbose", is_flag=True, default=False, help="Detalhar cada campo validado")
def validate(file: str, schema: str, verbose: bool) -> None:
    """
    Valida um arquivo de portfólio existente contra o schema publicado.

    FILE: Caminho para o arquivo JSON de portfólio a validar.

    Exemplos:

    \b
      portfolio-gen validate output/portfolio-2026-06-17.json
      portfolio-gen validate output/portfolio-2026-06-17.json --verbose
    """
    console.print("[yellow]⚠ Módulo validate ainda não implementado (Phase 6)[/yellow]")
    console.print(f"  file={file}, schema={schema}")
    raise SystemExit(0)


@cli.command()
@click.argument("file", type=click.Path(exists=False))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    show_default=True,
    help="Formato de saída",
)
@click.option("--top", default=None, type=int, help="Exibir apenas os N primeiros projetos")
@click.option(
    "--sort-by",
    type=click.Choice(["name", "language", "size", "date"]),
    default="name",
    show_default=True,
    help="Campo de ordenação",
)
def report(file: str, output_format: str, top: int | None, sort_by: str) -> None:
    """
    Exibe relatório legível do portfólio em tabela Rich.

    FILE: Caminho para o arquivo JSON de portfólio.

    Exemplos:

    \b
      portfolio-gen report output/portfolio-2026-06-17.json
      portfolio-gen report output/portfolio-2026-06-17.json --format csv --top 20
    """
    console.print("[yellow]⚠ Módulo report ainda não implementado (Phase 6)[/yellow]")
    console.print(f"  file={file}, format={output_format}, top={top}")
    raise SystemExit(0)


if __name__ == "__main__":
    cli()
