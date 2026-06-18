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

    console.print(f"\n[bold cyan]portfolio-gen init[/bold cyan] → [cyan]{scan_path}[/cyan]\n")
    console.print("[bold]Opções para cada pasta:[/bold]")
    console.print("  [green bold]y[/green bold]  →  esta pasta É um projeto único (marca e não entra dentro)")
    console.print("  [cyan bold]r[/cyan bold]  →  entrar dentro para buscar sub-projetos  [dim](padrão)[/dim]")
    console.print("  [yellow bold]s[/yellow bold]  →  pular esta subárvore inteira")
    console.print("  [red bold]e[/red bold]  →  excluir permanentemente do scan\n")
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
                (
                    e for e in current.iterdir()
                    if e.is_dir()
                    and not e.name.startswith(".")
                    and e.name not in DEFAULT_EXCLUDED
                    and e.name not in existing_excluded
                ),
                key=lambda e: e.name.lower(),
            )
        except PermissionError:
            return

        for entry in entries:
            rel = entry.relative_to(scan_path)
            already = (entry / MARKER_FILE).exists()
            suffix = "  [dim](já marcado)[/dim]" if already else ""
            console.print(f"\n[bold]📁 {rel}/[/bold]{suffix}")
            logger.debug(f"Init: inspecionando '{rel}/'")
            choice = Prompt.ask(
                "  Opção",
                choices=["y", "r", "s", "e"],
                default="r",
                show_choices=True,
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
                console.print("  [green]✓ Projeto marcado[/green]")
            elif choice == "r":
                logger.debug(f"Init: entrando em '{rel}/'")
                _walk(entry, depth + 1)
            elif choice == "e":
                existing_excluded.add(entry.name)
                if not dry_run:
                    _save_exclusion(entry.name, EXCLUSIONS_PATH)
                excluded_added.append(entry)
                logger.info(f"Init: '{rel}/' adicionado às exclusões permanentes")
                console.print("  [red]✗ Excluído do scan permanentemente[/red]")
            else:  # "s"
                skipped.append(entry)
                logger.debug(f"Init: '{rel}/' subárvore ignorada")
                console.print("  [dim]↷ Subárvore ignorada[/dim]")

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
    logger.info(f"Scan iniciado em '{scan_path}' (no_ai={no_ai}, dry_run={dry_run})")

    exclusions = _load_exclusions(EXCLUSIONS_PATH)
    config: dict[str, object] = {
        "root_path": str(scan_path),
        "excluded_dirs": exclusions.get("excluded_dirs", []),
        "max_depth": 3,
    }
    scanner = DirectoryScanner(config)
    project_paths = scanner.list_projects(scan_path)

    if not project_paths:
        logger.warning("Nenhum projeto encontrado — execute portfolio-gen init")
        console.print(
            "[yellow]Nenhum projeto encontrado.[/yellow]\n"
            "[dim]Execute [bold]portfolio-gen init[/bold] para marcar raízes de projeto.[/dim]"
        )
        raise SystemExit(0)

    logger.info(f"{len(project_paths)} projetos encontrados para escanear")
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
    logger.info(
        f"Extração concluída: {len(results)} projetos catalogados, "
        f"{skipped} pulados, {duration:.2f}s"
    )

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
        logger.info(f"Portfolio salvo em '{output_path}' — scan finalizado")
    else:
        console.print(f"[red]Erro ao salvar portfolio em {output_path}[/red]")
        logger.error(f"Falha ao salvar portfolio em '{output_path}'")
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
      portfolio-gen report output/portfolio-2026-06-17.json --sort-by size --top 10
    """
    import csv
    import sys

    from rich.panel import Panel

    file_path = Path(file)
    if not file_path.exists():
        console.print(f"[red]Erro: arquivo não encontrado: {file}[/red]")
        raise SystemExit(1)

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        console.print(f"[red]Erro ao ler {file_path.name}: {exc}[/red]")
        raise SystemExit(1) from None

    projects: list[dict[str, object]] = data.get("projects", []) if isinstance(data, dict) else []

    sort_keys: dict[str, object] = {
        "name": lambda p: str(p.get("name", "")).lower(),
        "language": lambda p: str((p.get("language") or {}).get("primary", "")).lower(),
        "size": lambda p: int((p.get("metrics") or {}).get("size_bytes", 0) or 0),
        "date": lambda p: str(p.get("last_modified", "")),
    }
    reverse_sort = sort_by in ("size", "date")
    projects = sorted(projects, key=sort_keys[sort_by], reverse=reverse_sort)  # type: ignore[arg-type]

    if top is not None:
        projects = projects[:top]

    if output_format == "json":
        console.print_json(json.dumps({"projects": projects}, default=str))
        raise SystemExit(0)

    if output_format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow([
            "name", "type", "language", "git", "branch",
            "status", "file_count", "size_bytes", "last_modified", "technologies",
        ])
        for p in projects:
            lang = p.get("language") or {}
            git = p.get("git") or {}
            metrics = p.get("metrics") or {}
            techs = p.get("technologies") or []
            writer.writerow([
                p.get("name", ""),
                p.get("type", ""),
                (lang.get("primary", "") if isinstance(lang, dict) else ""),
                ("sim" if (git.get("initialized") if isinstance(git, dict) else False) else "não"),
                (git.get("branch", "") if isinstance(git, dict) else ""),
                p.get("status", ""),
                (metrics.get("file_count", 0) if isinstance(metrics, dict) else 0),
                (metrics.get("size_bytes", 0) if isinstance(metrics, dict) else 0),
                p.get("last_modified", ""),
                ", ".join(str(t) for t in techs) if isinstance(techs, list) else "",
            ])
        raise SystemExit(0)

    # format=table (default)
    generated_at = str(data.get("generated_at", ""))[:19].replace("T", " ")
    scan_path = str(data.get("scan_path", ""))
    total = int(str(data.get("total_projects") or 0))
    skipped = int(str(data.get("skipped_projects") or 0))
    duration = float(str(data.get("scan_duration_seconds") or 0))

    header = (
        f"[bold]Portfolio:[/bold] {scan_path}  "
        f"[dim]|[/dim]  [bold]Projetos:[/bold] {total}  "
        f"[dim]|[/dim]  [bold]Pulados:[/bold] {skipped}  "
        f"[dim]|[/dim]  [bold]Duração:[/bold] {duration:.1f}s  "
        f"[dim]|[/dim]  [bold]Gerado:[/bold] {generated_at}"
    )
    console.print(Panel(header, title=f"[bold cyan]{file_path.name}[/bold cyan]", expand=False))

    if top is not None:
        console.print(f"[dim]Exibindo {len(projects)} de {total} projetos (--top {top})[/dim]")

    table = Table(show_header=True, header_style="bold cyan", row_styles=["", "dim"])
    table.add_column("#", style="dim", justify="right", width=3)
    table.add_column("Nome", min_width=24)
    table.add_column("Tipo", min_width=14)
    table.add_column("Linguagem", min_width=12)
    table.add_column("Git", justify="center", width=5)
    table.add_column("Branch", min_width=8)
    table.add_column("Status", width=10)
    table.add_column("Arquivos", justify="right", width=8)
    table.add_column("Tamanho", justify="right", width=9)

    def _fmt_size(b: object) -> str:
        n = int(str(b or 0))
        if n >= 1_073_741_824:
            return f"{n / 1_073_741_824:.1f} GB"
        if n >= 1_048_576:
            return f"{n / 1_048_576:.1f} MB"
        if n >= 1024:
            return f"{n / 1024:.0f} KB"
        return f"{n} B"

    status_style = {"active": "green", "archived": "yellow", "unknown": "dim"}

    for i, p in enumerate(projects, 1):
        lang = p.get("language") or {}
        git = p.get("git") or {}
        metrics = p.get("metrics") or {}
        git_ok = bool(git.get("initialized") if isinstance(git, dict) else False)
        branch = str(git.get("branch", "") if isinstance(git, dict) else "")
        status = str(p.get("status", "unknown"))
        file_count = str(metrics.get("file_count", 0) if isinstance(metrics, dict) else 0)
        size = _fmt_size(metrics.get("size_bytes", 0) if isinstance(metrics, dict) else 0)
        primary_lang = str(lang.get("primary", "") if isinstance(lang, dict) else "")
        proj_type = str(p.get("type", ""))
        name = str(p.get("name", ""))

        table.add_row(
            str(i),
            name,
            proj_type,
            primary_lang,
            "[green]✓[/green]" if git_ok else "[dim]—[/dim]",
            branch if git_ok else "",
            f"[{status_style.get(status, 'dim')}]{status}[/{status_style.get(status, 'dim')}]",
            file_count,
            size,
        )

    console.print(table)
    console.print(
        f"[dim]{len(projects)} projeto(s) | ordenado por: {sort_by}"
        + (f" | top {top}" if top else "")
        + "[/dim]"
    )
    raise SystemExit(0)


if __name__ == "__main__":
    cli()
