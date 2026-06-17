"""
CLI principal do portfolio-gen.

Entry point: portfolio-gen (definido em pyproject.toml [project.scripts])

Subcomandos:
  scan      — escaneia diretório e gera portfolio JSON
  validate  — valida arquivo de portfolio contra o schema
  report    — exibe relatório legível do portfolio
"""
from __future__ import annotations

import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from cli._logging import configure_logging

console = Console()

DEFAULT_SCAN_PATH = "/home/yves_marinho/Documentos/DevOps/"
ALLOWED_SCOPE = "/home/yves_marinho/Documentos/DevOps/"
SCHEMA_PATH = Path("schemas/portfolio-schema-v1.json")


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
    from extractor.metadata_extractor import scan_project
    from generator.portfolio_generator import PortfolioGenerator
    from scanner.directory_scanner import DirectoryScanner, validate_path_scope

    scan_path = Path(path)

    if not validate_path_scope(scan_path):
        console.print(f"[red]Erro: path fora do escopo permitido: {path}[/red]")
        console.print(f"[dim]Escopo permitido: {ALLOWED_SCOPE}[/dim]")
        raise SystemExit(1)

    if not scan_path.exists() or not scan_path.is_dir():
        console.print(f"[red]Erro: diretório não existe: {path}[/red]")
        raise SystemExit(1)

    console.print(f"[bold cyan]portfolio-gen scan[/bold cyan] → [cyan]{scan_path}[/cyan]")

    config: dict[str, object] = {
        "root_path": str(scan_path),
        "excluded_dirs": [],
        "max_depth": 3,
    }
    scanner = DirectoryScanner(config)
    project_paths = scanner.list_projects(scan_path)

    if not project_paths:
        console.print("[yellow]Nenhum projeto encontrado.[/yellow]")
        raise SystemExit(0)

    console.print(f"[dim]{len(project_paths)} diretórios encontrados — iniciando extração...[/dim]")

    n_workers = workers if workers else min(4, os.cpu_count() or 1)
    results: list[dict[str, object]] = []
    skipped = 0
    start_time = time.monotonic()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task_id = progress.add_task("Escaneando projetos...", total=len(project_paths))

        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            future_to_path = {executor.submit(scan_project, p): p for p in project_paths}
            for future in as_completed(future_to_path):
                result = future.result()
                if result is None:
                    skipped += 1
                else:
                    results.append(result)
                progress.advance(task_id)

    duration = time.monotonic() - start_time

    gen_config: dict[str, object] = {
        "schema_path": str(SCHEMA_PATH),
        "generator_version": "1.0.0",
    }
    gen = PortfolioGenerator(gen_config)
    meta: dict[str, object] = {
        "scan_path": str(scan_path),
        "scan_duration_seconds": round(duration, 3),
        "skipped_projects": skipped,
    }
    portfolio = gen.build_portfolio(results, meta)

    _print_scan_summary(portfolio, skipped, duration, dry_run)

    if dry_run:
        console.print("[yellow]dry-run: nenhum arquivo criado.[/yellow]")
        raise SystemExit(0)

    if not gen.validate_schema(portfolio, SCHEMA_PATH):
        console.print("[red]Aviso: portfolio não passou na validação do schema.[/red]")

    date_str = datetime.now(UTC).strftime("%Y-%m-%d")
    output_path = Path(output) if output else Path(f"output/portfolio-{date_str}.json")

    if gen.write_output(portfolio, output_path):
        console.print(f"[green]✓ Portfolio salvo em:[/green] {output_path}")
    else:
        console.print(f"[red]Erro ao salvar portfolio em {output_path}[/red]")
        raise SystemExit(1)

    raise SystemExit(0 if skipped == 0 else 2)


def _print_scan_summary(
    portfolio: dict[str, object],
    skipped: int,
    duration: float,
    dry_run: bool,
) -> None:
    """Exibe sumário do scan em tabela Rich."""
    total = int(str(portfolio.get("total_projects") or 0))
    table = Table(title="Resultado do Scan", show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="dim")
    table.add_column("Valor", justify="right")
    table.add_row("Projetos catalogados", str(total))
    table.add_row("Projetos pulados", str(skipped))
    table.add_row("Duração", f"{duration:.2f}s")
    if dry_run:
        table.add_row("Modo", "[yellow]dry-run[/yellow]")
    console.print(table)

    projects = portfolio.get("projects", [])
    if isinstance(projects, list) and projects:
        preview = Table(show_header=True, header_style="bold", box=None)
        preview.add_column("Projeto", style="cyan")
        preview.add_column("Tipo", style="dim")
        preview.add_column("Linguagem")
        preview.add_column("Status", style="dim")
        for proj in sorted(projects, key=lambda p: str(p.get("name", "") if isinstance(p, dict) else ""))[:10]:
            lang = proj.get("language", {}) if isinstance(proj, dict) else {}
            preview.add_row(
                str(proj.get("name", "") if isinstance(proj, dict) else ""),
                str(proj.get("type", "") if isinstance(proj, dict) else ""),
                str(lang.get("primary", "") if isinstance(lang, dict) else ""),
                str(proj.get("status", "") if isinstance(proj, dict) else ""),
            )
        if len(projects) > 10:
            preview.add_row(f"... +{len(projects) - 10} mais", "", "", "")
        console.print(preview)


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
