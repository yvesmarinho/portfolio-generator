"""
Extração de métricas de projetos: contagem de arquivos, tamanho e linhas estimadas.

Exclui automaticamente diretórios de build e dependências para métricas precisas.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loguru import logger

EXCLUDED_DIRS: frozenset[str] = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", "tmp", ".secrets"}
)


@dataclass
class ProjectMetrics:
    """Métricas quantitativas de um projeto."""

    file_count: int
    size_bytes: int
    line_count_estimated: int


def extract_metrics(project_path: Path) -> ProjectMetrics:
    """
    Extrai métricas de um diretório de projeto.

    Conta arquivos, soma tamanhos e estima linhas de código.
    Exclui .git, node_modules, __pycache__, .venv, tmp.
    Trata erros de encoding graciosamente (usa replace).

    :param project_path: Caminho do diretório do projeto.
    :type project_path: Path
    :return: Métricas do projeto.
    :rtype: ProjectMetrics

    >>> from pathlib import Path
    >>> result = extract_metrics(Path("/nonexistent_xyzabc"))
    >>> result.file_count
    0
    """
    if not isinstance(project_path, Path) or not project_path.exists():
        return ProjectMetrics(file_count=0, size_bytes=0, line_count_estimated=0)
    try:
        return _compute_metrics(project_path)
    except Exception as exc:
        logger.warning(f"Erro ao extrair métricas de '{project_path}': {exc}")
        return ProjectMetrics(file_count=0, size_bytes=0, line_count_estimated=0)


def _compute_metrics(root: Path) -> ProjectMetrics:
    """Itera recursivamente pelo projeto e calcula as métricas."""
    import os

    file_count = 0
    size_bytes = 0
    line_count = 0

    def _on_error(err: OSError) -> None:
        logger.debug(f"Acesso negado (ignorado): {err.filename}")

    for dirpath, dirnames, filenames in os.walk(root, onerror=_on_error):
        # Poda in-place: remove dirs excluídos para não descer neles
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]

        for fname in filenames:
            fpath = Path(dirpath) / fname
            file_count += 1
            try:
                stat = fpath.stat()
                size_bytes += stat.st_size
            except OSError:
                continue
            try:
                raw = fpath.read_bytes()
                text = raw.decode("utf-8", errors="replace")
                line_count += text.count("\n")
            except OSError:
                continue

    return ProjectMetrics(
        file_count=file_count,
        size_bytes=size_bytes,
        line_count_estimated=line_count,
    )
