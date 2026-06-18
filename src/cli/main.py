"""
CLI principal do portfolio-gen.

Entry point: portfolio-gen (definido em pyproject.toml [project.scripts])

Subcomandos:
  init      — marca raízes de projetos interativamente (cria .portfolio-project)
  scan      — escaneia diretório e gera portfolio JSON
  validate  — valida arquivo de portfolio contra o schema
  report    — exibe relatório legível do portfolio
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import UTC, datetime
from functools import partial
from pathlib import Path

import click
from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from cli._logging import configure_logging

console = Console()

DEFAULT_SCAN_PATH = "/home/yves_marinho/Documentos/DevOps/"
ALLOWED_SCOPE = "/home/yves_marinho/Documentos/DevOps/"
SCHEMA_PATH = Path("schemas/portfolio-schema-v1.json")
EXCLUSIONS_PATH = Path("config/scan-exclusions.json")


def _load_exclusions(exclusions_path: Path) -> dict[str, list[str]]:
    """Carrega config/scan-exclusions.json; retorna estrutura vazia em caso de erro."""
    try:
        if exclusions_path.exists():
            data = json.loads(exclusions_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"excluded_dirs": []}


def _save_exclusion(dir_name: str, exclusions_path: Path) -> None:
    """Adiciona dir_name à lista excluded_dirs em config/scan-exclusions.json."""
    try:
        data = _load_exclusions(exclusions_path)
        excluded: list[str] = data.get("excluded_dirs", [])
        if dir_name not in excluded:
            excluded.append(dir_name)
            data["excluded_dirs"] = excluded
            exclusions_path.parent.mkdir(parents=True, exist_ok=True)
            exclusions_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        console.print(f"[yellow]Aviso: não foi possível salvar exclusão '{dir_name}': {exc}[/yellow]")


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
    help=f"Diretório raiz a percorrer. Deve estar em {ALLOWED_SCOPE}",
)
@click.option("--max-depth", default=3, show_default=True, type=int, help="Profundidade máxima de busca")
@click.option("--dry-run", is_flag=True, default=False, help="Simular sem criar arquivos")
def init(path: str, max_depth: int, dry_run: bool) -> None:
    """
    Marca raízes de projetos interativamente.

    Percorre o diretório raiz e pergunta sobre cada pasta encontrada.
    Quando confirmada, cria .portfolio-project no diretório — o arquivo que
    o subcomando `scan` usa para identificar projetos.

    Exemplos:

    \b
      portfolio-gen init
      portfolio-gen init --path ~/Documentos/DevOps/Vya-Jobs/
      portfolio-gen init --dry-run
    """
    from rich.prompt import Prompt

    from scanner.directory_scanner import DEFAULT_EXCLUDED, MARKER_FILE, validate_path_scope

    scan_path = Path(path)

    if not validate_path_scope(scan_path):
        console.print(f"[red]Erro: path fora do escopo permitido: {path}[/red]")
        raise SystemExit(1)

    if not scan_path.exists() or not scan_path.is_dir():
        console.print(f"[red]Erro: diretório não existe: {path}[/red]")
        raise SystemExit(1)

    if dry_run:
        console.print("[yellow]dry-run: nenhum arquivo será criado.[/yellow]")

    console.print(
        f"[bold cyan]portfolio-gen init[/bold cyan] → [cyan]{scan_path}[/cyan]\n"
        "[dim]Para cada pasta:\n"
        "  [bold][y][/bold] esta pasta É um projeto (marca e não entra dentro)\n"
        "  [bold][r][/bold] entrar dentro para buscar sub-projetos\n"
        "  [bold][s][/bold] pular esta subárvore inteira\n"
        "  [bold][e][/bold] excluir do scan permanentemente[/dim]\n"
    )
    logger.info(f"Init iniciado em '{scan_path}' (max_depth={max_depth}, dry_run={dry_run})")

    # Carrega exclusões já existentes para pular pastas já excluídas
    exclusions_data = _load_exclusions(EXCLUSIONS_PATH)
    existing_excluded: set[str] = set(exclusions_data.get("excluded_dirs", []))

    marked: list[Path] = []
    skipped: list[Path] = []
    excluded_added: list[Path] = []

    def _walk(current: Path, depth: int) -> None:
        if depth >= max_depth:
            return
        try:
            entries = sorted(
                e for e in current.iterdir()
                if e.is_dir() and e.name not in DEFAULT_EXCLUDED and e.name not in existing_excluded
            )
        except PermissionError:
            return

        for entry in entries:
            rel = entry.relative_to(scan_path)
            already = (entry / MARKER_FILE).exists()
            label = f"[cyan]{rel}/[/cyan]"
            if already:
                label += " [dim](já marcado)[/dim]"

            logger.debug(f"Init: inspecionando '{rel}/'")
            console.print(label)
            choice = Prompt.ask(
                "  [y] projeto  [r] entrar  [s] pular  [e] excluir",
                choices=["y", "r", "s", "e"],
                default="r",
                show_choices=False,
            )

            if choice == "y":
                marker = entry / MARKER_FILE
                if not dry_run:
                    marker.write_text(
                        json.dumps(
                            {
                                "portfolio_root": True,
                                "marked_at": datetime.now(UTC).isoformat(),
                            },
                            indent=2,
                        )
                        + "\n"
                    )
                marked.append(entry)
                logger.info(f"Init: '{rel}/' marcado como projeto raiz")
                console.print(f"  [green]✓ Marcado:[/green] {marker.name}\n")
            elif choice == "r":
                logger.debug(f"Init: entrando em '{rel}/'")
                _walk(entry, depth + 1)
            elif choice == "e":
                existing_excluded.add(entry.name)
                if not dry_run:
                    _save_exclusion(entry.name, EXCLUSIONS_PATH)
                excluded_added.append(entry)
                logger.info(f"Init: '{rel}/' adicionado às exclusões permanentes")
                console.print(
                    f"  [red]✗ Excluído do scan:[/red] {entry.name}"
                    f" → {EXCLUSIONS_PATH}\n"
                )
            else:  # "s"
                skipped.append(entry)
                logger.debug(f"Init: '{rel}/' subárvore ignorada")
                console.print("  [dim]↷ Subárvore ignorada[/dim]\n")

    _walk(scan_path, depth=0)

    logger.info(
        f"Init concluído: {len(marked)} marcados, "
        f"{len(excluded_added)} excluídos, {len(skipped)} ignorados"
    )
    console.print("\n[bold]Resumo:[/bold]")
    console.print(f"  Marcados      : [green]{len(marked)}[/green]")
    console.print(f"  Excluídos     : [red]{len(excluded_added)}[/red]")
    console.print(f"  Ignorados     : [dim]{len(skipped)}[/dim]")
    if dry_run:
        console.print("[yellow]dry-run: nenhum arquivo criado.[/yellow]")
    raise SystemExit(0)


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

    exclusions = _load_exclusions(EXCLUSIONS_PATH)
    config: dict[str, object] = {
        "root_path": str(scan_path),
        "excluded_dirs": exclusions.get("excluded_dirs", []),
        "max_depth": 3,
    }
    scanner = DirectoryScanner(config)
    project_paths = scanner.list_projects(scan_path)

    if not project_paths:
        console.print(
            "[yellow]Nenhum projeto encontrado.[/yellow]\n"
            "[dim]Execute [bold]portfolio-gen init[/bold] para marcar raízes de projeto.[/dim]"
        )
        raise SystemExit(0)

    console.print(f"[dim]{len(project_paths)} diretórios encontrados — iniciando extração...[/dim]")

    n_workers = workers if workers else min(4, os.cpu_count() or 1)
    bug_dir = Path("docs/bugs")
    ai_config: dict[str, object] = {
        "no_ai": no_ai,
        "ai_min_words": ai_min_words,
        "ai_max_tokens": ai_max_tokens,
        "secrets_path": ".secrets/api_config.json",
    }
    scan_fn = partial(scan_project, bug_report_dir=bug_dir, config=ai_config)
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
            future_to_path = {executor.submit(scan_fn, p): p for p in project_paths}
            for future in as_completed(future_to_path):
                try:
                    result = future.result()
                except Exception as exc:
                    proj_path = future_to_path[future]
                    console.print(f"[yellow]⚠ Worker falhou em '{proj_path.name}': {exc}[/yellow]")
                    result = None
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

    _print_scan_summary(portfolio, skipped, duration, dry_run, ai_min_words=ai_min_words)

    if skipped > 0:
        console.print(
            f"[yellow]⚠ {skipped} projeto(s) pulado(s). "
            f"Verifique {bug_dir}/ e logs/ para detalhes.[/yellow]"
        )

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
    ai_min_words: int = 30,
) -> None:
    """Exibe sumário do scan em tabela Rich (T039: tamanho JSON e elegíveis para IA)."""
    total = int(str(portfolio.get("total_projects") or 0))

    projects = portfolio.get("projects", [])
    ai_eligible = 0
    if isinstance(projects, list):
        ai_eligible = sum(
            1
            for p in projects
            if isinstance(p, dict)
            and int(str(p.get("_readme_word_count", 0) or 0)) < ai_min_words
        )

    try:
        json_bytes = len(json.dumps(portfolio, default=str).encode("utf-8"))
        json_size_str = f"{json_bytes / 1024:.1f} KB"
    except Exception:
        json_size_str = "—"

    table = Table(title="Resultado do Scan", show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="dim")
    table.add_column("Valor", justify="right")
    table.add_row("Projetos catalogados", str(total))
    table.add_row("Projetos pulados", str(skipped))
    table.add_row("Duração", f"{duration:.2f}s")
    table.add_row("Tamanho estimado (JSON)", json_size_str)
    table.add_row("Elegíveis para IA", str(ai_eligible))
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
@click.argument("file", type=click.Path(exists=True))
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
    import jsonschema

    file_path = Path(file)
    schema_path = Path(schema)

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Erro: JSON inválido em {file_path.name}: {exc}[/red]")
        raise SystemExit(1) from None
    except OSError as exc:
        console.print(f"[red]Erro ao ler {file_path}: {exc}[/red]")
        raise SystemExit(1) from None

    if not schema_path.exists():
        console.print(f"[red]Erro: schema não encontrado: {schema_path}[/red]")
        raise SystemExit(1)

    try:
        schema_data = json.loads(schema_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        console.print(f"[red]Erro ao carregar schema: {exc}[/red]")
        raise SystemExit(1) from None

    validator = jsonschema.Draft7Validator(schema_data)
    errors = sorted(validator.iter_errors(data), key=lambda e: str(e.message))

    if not errors:
        console.print(f"[green]✓ Portfolio válido[/green] — {file_path.name}")
        if verbose:
            n = data.get("total_projects", 0) if isinstance(data, dict) else 0
            console.print(f"  [dim]{n} projeto(s) catalogado(s)[/dim]")
        raise SystemExit(0)

    console.print(
        f"[red]✗ Portfolio inválido[/red] — "
        f"{len(errors)} violação(ões) em [bold]{file_path.name}[/bold]"
    )

    err_table = Table(show_header=True, header_style="bold red", box=None)
    err_table.add_column("Path JSON", style="cyan", no_wrap=True)
    err_table.add_column("Violação")

    for err in errors:
        path_parts = ["$"]
        for part in err.absolute_path:
            path_parts.append(f"[{part}]" if isinstance(part, int) else f".{part}")
        path_str = "".join(path_parts)
        err_table.add_row(path_str, err.message)

    console.print(err_table)
    raise SystemExit(1)


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
