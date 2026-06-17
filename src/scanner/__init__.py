"""
Módulo scanner — varredura recursiva de diretórios de projetos.

Responsabilidade única: encontrar e listar projetos válidos em um diretório raiz,
aplicando filtros de exclusão configuráveis.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scanner.directory_scanner import DirectoryScanner


def create_scanner(config: dict[str, Any]) -> DirectoryScanner | bool:
    """
    Factory para instanciar o DirectoryScanner com configuração fornecida.

    :param config: Dicionário de configuração com chaves: root_path, excluded_dirs, max_depth.
    :type config: dict[str, Any]
    :return: Instância configurada de DirectoryScanner, ou False em caso de erro.
    :rtype: DirectoryScanner | bool

    >>> config = {"root_path": "/tmp", "excluded_dirs": [".git"], "max_depth": 1}
    >>> result = create_scanner(config)
    >>> result is not None
    True
    >>> create_scanner({})
    False
    >>> create_scanner("")  # type: ignore[arg-type]
    False
    """
    if not config or not isinstance(config, dict):
        return False
    try:
        from scanner.directory_scanner import DirectoryScanner

        return DirectoryScanner(config)
    except Exception as e:
        print(f"Erro ao criar scanner: {e}")
        return False
