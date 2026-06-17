"""
Orquestrador de extração de metadados de projetos.

MetadataExtractor coordena language, git, metrics e readme_parser para
produzir um dicionário completo de projeto. A função module-level
scan_project() é segura para uso com ProcessPoolExecutor.
"""
from __future__ import annotations

import traceback
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from loguru import logger

from analyzer.readme_parser import extract_description, parse_readme, token_count, word_count
from extractor.git_extractor import GitInfo, extract_git_info
from extractor.language_extractor import detect_language
from extractor.metrics_extractor import extract_metrics

EXCLUDED_DIRS: frozenset[str] = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", "tmp"}
)

_PROJECT_TYPE_SIGNALS: dict[str, list[str]] = {
    "infrastructure": ["Dockerfile", "terraform.tfvars", "main.tf", "variables.tf"],
    "cli-tool": ["pyproject.toml", "setup.py", "__main__.py", "cli.py"],
    "api-service": ["app.py", "server.py", "wsgi.py", "asgi.py", "manage.py"],
    "web-app": ["package.json", "index.html", "vite.config.ts", "next.config.js"],
    "data-analysis": ["notebook.ipynb", "analysis.py", "requirements.txt"],
    "automation": ["Makefile", "ansible.cfg", "playbook.yml", "tasks.yml"],
    "documentation": ["mkdocs.yml", "conf.py", "index.rst"],
    "script": ["main.py", "run.py", "script.py"],
    "library": ["setup.py", "setup.cfg", "pyproject.toml"],
}


class MetadataExtractor:
    """
    Orquestra a extração de metadados de um projeto DevOps.

    Coordena language_extractor, git_extractor, metrics_extractor
    e readme_parser para produzir dicionários de entrada no portfólio.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Inicializa o extrator com configuração fornecida.

        :param config: Configuração com chaves: no_ai, ai_min_words, ai_max_tokens.
        :type config: dict[str, Any]

        >>> e = MetadataExtractor({"no_ai": True, "ai_min_words": 30, "ai_max_tokens": 2000})
        >>> e is not None
        True
        """
        self._no_ai = bool(config.get("no_ai", True))
        self._ai_min_words = int(config.get("ai_min_words") or 30)
        self._ai_max_tokens = int(config.get("ai_max_tokens") or 2000)

    def extract(self, path: Path) -> dict[str, Any] | None:
        """
        Extrai todos os metadados de um projeto.

        :param path: Caminho do diretório do projeto.
        :type path: Path
        :return: Dicionário de metadados ou None em caso de erro.
        :rtype: dict[str, Any] | None

        >>> from pathlib import Path
        >>> e = MetadataExtractor({"no_ai": True})
        >>> e.extract(Path("/nonexistent")) is None
        True
        """
        return scan_project(path)


def _write_bug_report(path: Path, exc: Exception, out_dir: Path) -> None:
    """
    Grava um relatório de erro em markdown para um projeto que falhou no scan.

    Cria out_dir se necessário. Silencia erros de I/O para não mascarar o fluxo principal.

    :param path: Path do projeto que falhou.
    :type path: Path
    :param exc: Exceção capturada durante o scan.
    :type exc: Exception
    :param out_dir: Diretório de saída para os relatórios.
    :type out_dir: Path

    >>> from pathlib import Path
    >>> _write_bug_report(Path("/fake"), ValueError("test"), Path("/tmp/__test_bug_dir__"))
    """
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = out_dir / f"bug-report-{timestamp}.md"
        report_path.write_text(
            f"# Bug Report — {timestamp}\n\n"
            f"**Status**: OPEN\n"
            f"**Projeto**: `{path}`\n"
            f"**Tipo de erro**: `{type(exc).__name__}`\n"
            f"**Mensagem**: {exc}\n\n"
            f"## Stack Trace\n\n```\n{traceback.format_exc()}\n```\n",
            encoding="utf-8",
        )
    except Exception as write_exc:
        logger.warning(f"Não foi possível gravar bug report para '{path}': {write_exc}")


def scan_project(path: Path, bug_report_dir: Path | None = None) -> dict[str, Any] | None:
    """
    Extrai todos os metadados de um projeto. Seguro para ProcessPoolExecutor.

    Retorna None em caso de qualquer erro irrecuperável durante a extração.
    O path absoluto é retornado em 'path' — convertido para relativo em
    PortfolioGenerator.build_portfolio(). Quando bug_report_dir é fornecido,
    cria um arquivo bug-report-*.md em caso de falha.

    :param path: Caminho do diretório do projeto.
    :type path: Path
    :param bug_report_dir: Diretório onde gravar bug reports (opcional).
    :type bug_report_dir: Path | None
    :return: Dicionário de metadados do projeto ou None.
    :rtype: dict[str, Any] | None

    >>> from pathlib import Path
    >>> scan_project(Path("/nonexistent_xyzabc")) is None
    True
    """
    if not isinstance(path, Path) or not path.exists():
        return None
    try:
        lang_info = detect_language(path)
        git_info = extract_git_info(path)
        metrics = extract_metrics(path)
        readme_text = parse_readme(path)

        description = extract_description(readme_text) if readme_text else ""
        description_source = "readme" if readme_text else "empty"

        readme_words = word_count(readme_text) if readme_text else 0
        readme_tokens = token_count(readme_text) if readme_text else 0
        _ = readme_tokens  # reservado para Phase 7 (AI trigger)

        git_dict: dict[str, Any] = {"initialized": git_info is not None}
        if git_info is not None:
            git_dict["branch"] = git_info.branch
            git_dict["last_commit_hash"] = git_info.last_commit_hash
            git_dict["last_commit_date"] = git_info.last_commit_date
            git_dict["last_commit_author"] = git_info.last_commit_author
            git_dict["commit_count"] = git_info.commit_count

        return {
            "name": path.name,
            "path": str(path),
            "type": _infer_type(path),
            "description": description,
            "description_source": description_source,
            "language": {
                "primary": lang_info.primary,
                "secondary": lang_info.secondary,
                "confidence": lang_info.confidence,
            },
            "metrics": {
                "file_count": metrics.file_count,
                "size_bytes": metrics.size_bytes,
                "line_count_estimated": metrics.line_count_estimated,
            },
            "git": git_dict,
            "technologies": _infer_technologies(path),
            "status": _infer_status(git_info),
            "last_modified": _get_last_modified(path),
            "_readme_word_count": readme_words,
        }
    except Exception as exc:
        logger.warning(f"Projeto '{path}' pulado: {type(exc).__name__}: {exc}")
        if bug_report_dir is not None:
            _write_bug_report(path, exc, bug_report_dir)
        return None


def _infer_type(path: Path) -> str:
    """Infere o tipo do projeto a partir dos arquivos presentes."""
    try:
        files_in_root = {f.name for f in path.iterdir() if f.is_file()}
        dirs_in_root = {d.name for d in path.iterdir() if d.is_dir()}

        has_tf = any(f.endswith(".tf") for f in files_in_root)
        has_dockerfile = "Dockerfile" in files_in_root or "dockerfile" in files_in_root
        has_package_json = "package.json" in files_in_root
        has_pyproject = "pyproject.toml" in files_in_root
        has_setup_py = "setup.py" in files_in_root or "setup.cfg" in files_in_root
        has_main_py = any(f in files_in_root for f in ("main.py", "__main__.py", "cli.py"))
        has_server = any(f in files_in_root for f in ("app.py", "server.py", "wsgi.py", "asgi.py"))
        has_notebook = any(f.endswith(".ipynb") for f in files_in_root)
        has_ansible = any(f in files_in_root for f in ("ansible.cfg", "playbook.yml"))
        has_k8s = "k8s" in dirs_in_root or "kubernetes" in dirs_in_root
        has_docs = any(f in files_in_root for f in ("mkdocs.yml", "conf.py"))

        if has_tf or has_k8s:
            return "infrastructure"
        if has_dockerfile and not has_pyproject:
            return "infrastructure"
        if has_ansible:
            return "automation"
        if has_package_json:
            return "web-app"
        if has_notebook:
            return "data-analysis"
        if has_docs:
            return "documentation"
        if has_server:
            return "api-service"
        if (has_pyproject or has_setup_py) and has_main_py:
            return "cli-tool"
        if has_pyproject or has_setup_py:
            return "library"
        if has_main_py:
            return "script"
    except Exception as exc:
        logger.debug(f"Erro ao inferir tipo de '{path}': {exc}")
    return "unknown"


def _infer_technologies(path: Path) -> list[str]:
    """Detecta tecnologias/frameworks usados no projeto."""
    techs: list[str] = []
    try:
        files_in_root = {f.name for f in path.iterdir() if f.is_file()}

        if "Dockerfile" in files_in_root or "dockerfile" in files_in_root:
            techs.append("Docker")
        if "docker-compose.yml" in files_in_root or "docker-compose.yaml" in files_in_root:
            techs.append("Docker Compose")
        if any(f.endswith(".tf") for f in files_in_root):
            techs.append("Terraform")
        if "Makefile" in files_in_root:
            techs.append("Make")
        if "pyproject.toml" in files_in_root:
            techs.append("Python/uv")
        elif "requirements.txt" in files_in_root:
            techs.append("Python/pip")
        if "package.json" in files_in_root:
            techs.append("Node.js")
        if "go.mod" in files_in_root:
            techs.append("Go modules")
        if ".github" in {d.name for d in path.iterdir() if d.is_dir()} and (path / ".github" / "workflows").exists():
            techs.append("GitHub Actions")
        if "ansible.cfg" in files_in_root or "playbook.yml" in files_in_root:
            techs.append("Ansible")
    except Exception as exc:
        logger.debug(f"Erro ao inferir tecnologias de '{path}': {exc}")
    return techs


def _infer_status(git_info: object) -> str:
    """Infere o status do projeto com base na atividade git."""
    if not isinstance(git_info, GitInfo):
        return "unknown"
    try:
        last = datetime.fromisoformat(git_info.last_commit_date.replace("Z", "+00:00"))
        age = datetime.now(UTC) - last
        if age < timedelta(days=180):
            return "active"
        if age > timedelta(days=730):
            return "archived"
    except Exception:  # nosec B110
        pass
    return "unknown"


def _get_last_modified(path: Path) -> str:
    """Obtém a data/hora da modificação mais recente de qualquer arquivo do projeto."""
    max_mtime = 0.0
    try:
        for entry in path.rglob("*"):
            if not entry.is_file():
                continue
            try:
                rel_parts = entry.relative_to(path).parts
            except ValueError:
                continue
            if any(part in EXCLUDED_DIRS for part in rel_parts):
                continue
            try:
                mtime = entry.stat().st_mtime
                if mtime > max_mtime:
                    max_mtime = mtime
            except OSError:
                continue
    except (PermissionError, OSError):
        pass
    if max_mtime > 0:
        return datetime.fromtimestamp(max_mtime, tz=UTC).isoformat()
    return datetime.now(UTC).isoformat()
