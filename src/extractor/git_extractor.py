"""
Extração de informações de repositórios git usando gitpython.

Retorna None graciosamente para projetos sem git ou com repositório corrompido.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loguru import logger


@dataclass
class GitInfo:
    """Informações extraídas de um repositório git."""

    branch: str
    last_commit_hash: str
    last_commit_date: str
    last_commit_author: str
    commit_count: int


def extract_git_info(path: Path) -> GitInfo | None:
    """
    Extrai informações git de um diretório de projeto.

    Usa gitpython para acessar o repositório. Retorna None se o diretório
    não é um repositório git ou se ocorrer qualquer erro de acesso.

    :param path: Caminho do diretório do projeto.
    :type path: Path
    :return: Informações git ou None se não for repositório git.
    :rtype: GitInfo | None

    >>> from pathlib import Path
    >>> extract_git_info(Path("/nonexistent_xyzabc")) is None
    True
    >>> extract_git_info(Path("/tmp")) is None
    True
    """
    if not isinstance(path, Path) or not path.exists():
        return None
    try:
        import git

        repo = git.Repo(path, search_parent_directories=False)
        try:
            branch = repo.active_branch.name
        except TypeError:
            branch = repo.head.ref.name if not repo.head.is_detached else "HEAD"

        commit = repo.head.commit
        short_hash = commit.hexsha[:7]
        commit_date = commit.committed_datetime.isoformat()
        author = str(commit.author.name) if commit.author.name else "unknown"

        try:
            count_str = repo.git.rev_list("HEAD", count=True).strip()
            commit_count = int(count_str)
        except Exception:
            commit_count = sum(1 for _ in repo.iter_commits())

        return GitInfo(
            branch=branch,
            last_commit_hash=short_hash,
            last_commit_date=commit_date,
            last_commit_author=author,
            commit_count=commit_count,
        )
    except Exception as exc:
        logger.debug(f"Sem git em '{path}': {exc}")
        return None
