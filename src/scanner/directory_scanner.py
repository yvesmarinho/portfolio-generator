"""
Scanner de diretórios para localizar projetos DevOps válidos.

Responsabilidade única: encontrar e listar projetos válidos em um diretório raiz.

Projetos são identificados pelo arquivo marcador .portfolio-project, criado pelo
subcomando `portfolio-gen init`. Diretórios sem o marcador são percorridos
recursivamente até max_depth.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from loguru import logger

ALLOWED_SCOPE = Path("/home/yves_marinho/Documentos/DevOps/")

MARKER_FILE = ".portfolio-project"

DEFAULT_EXCLUDED: frozenset[str] = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", "tmp", ".secrets"}
)


def validate_path_scope(path: Path) -> bool:
    """
    Valida que o path está dentro do escopo permitido de varredura.

    O escopo é exclusivamente: /home/yves_marinho/Documentos/DevOps/
    Paths fora deste escopo são rejeitados para prevenir varredura não autorizada.

    :param path: Caminho a ser validado.
    :type path: Path
    :return: True se o path está dentro do escopo, False caso contrário.
    :rtype: bool

    >>> validate_path_scope(Path("/home/yves_marinho/Documentos/DevOps/"))
    True
    >>> validate_path_scope(Path("/home/yves_marinho/Documentos/DevOps/projeto-x"))
    True
    >>> validate_path_scope(Path("/home/yves_marinho/Documentos/"))
    False
    >>> validate_path_scope(Path("/etc/passwd"))
    False
    >>> validate_path_scope(Path(""))
    False
    """
    if not isinstance(path, Path):
        return False
    if not path.parts:
        return False
    try:
        resolved = path.resolve()
        allowed_resolved = ALLOWED_SCOPE.resolve()
        return resolved.is_relative_to(allowed_resolved)
    except OSError as exc:
        logger.warning(f"Erro ao validar escopo do path '{path}': {exc}")
        return False


class DirectoryScanner:
    """
    Varredura de diretórios para localizar projetos DevOps válidos.

    Projetos são identificados pelo arquivo marcador .portfolio-project.
    Diretórios sem marcador são percorridos recursivamente até max_depth.
    Execute `portfolio-gen init` para marcar as raízes de projeto.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Inicializa o scanner com a configuração fornecida.

        :param config: Dicionário com chaves opcionais: root_path (str),
                       excluded_dirs (list[str]), max_depth (int).
        :type config: dict[str, Any]

        >>> scanner = DirectoryScanner({"root_path": "/tmp", "excluded_dirs": [], "max_depth": 1})
        >>> scanner is not None
        True
        """
        self._root_path = Path(str(config.get("root_path", "")))
        excluded_raw = config.get("excluded_dirs") or []
        excluded_list: list[str] = [str(d) for d in excluded_raw if d]
        self._excluded: frozenset[str] = DEFAULT_EXCLUDED | frozenset(excluded_list)
        self._max_depth = int(config.get("max_depth") or 3)

    def list_projects(self, root: Path) -> list[Path]:
        """
        Lista projetos válidos dentro do diretório raiz.

        Procura recursivamente por diretórios contendo o arquivo marcador
        .portfolio-project. Execute `portfolio-gen init` para marcar projetos.

        :param root: Diretório raiz para varredura.
        :type root: Path
        :return: Lista de caminhos de projetos válidos, em ordem alfabética.
        :rtype: list[Path]

        >>> from pathlib import Path
        >>> scanner = DirectoryScanner({"root_path": "/tmp", "excluded_dirs": [], "max_depth": 1})
        >>> scanner.list_projects(Path("/etc")) == []
        True
        """
        if not isinstance(root, Path):
            return []
        if not validate_path_scope(root):
            logger.warning(f"Path fora do escopo permitido: {root}")
            return []
        if not root.exists() or not root.is_dir():
            logger.warning(f"Diretório não existe ou não é diretório: {root}")
            return []
        try:
            return sorted(self._scan_recursive(root, depth=0))
        except (OSError, RuntimeError) as exc:
            logger.error(f"Erro ao listar projetos em '{root}': {exc}")
            return []

    def _scan_recursive(self, root: Path, depth: int) -> list[Path]:
        """
        Varre recursivamente procurando diretórios com .portfolio-project.

        Diretórios marcados são incluídos diretamente sem recursão interna.
        Diretórios sem marcador têm seus filhos inspecionados até max_depth.
        """
        if depth >= self._max_depth:
            return []

        projects: list[Path] = []
        try:
            for entry in sorted(root.iterdir()):
                if not entry.is_dir():
                    continue
                if entry.name in self._excluded:
                    continue
                if (entry / MARKER_FILE).exists():
                    projects.append(entry)
                else:
                    projects.extend(self._scan_recursive(entry, depth + 1))
        except PermissionError as exc:
            logger.warning(f"Sem permissão para ler '{root}': {exc}")
        return projects

    def _scan_dir(self, root: Path) -> list[Path]:
        """Delegação para _scan_recursive no nível 0 (compatibilidade)."""
        return self._scan_recursive(root, depth=0)
