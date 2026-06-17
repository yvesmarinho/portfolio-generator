"""
Configuração centralizada de logging com loguru.

Chamado no startup da CLI para configurar os handlers de log.
Módulos internos usam apenas `from loguru import logger` — sem configuração própria.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module}:{line} — {message}"
)
_STDERR_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level:<8}</level> | "
    "{module} — {message}"
)


def configure_logging(verbose: bool = False, log_dir: Path | None = None) -> None:
    """
    Configura handlers do loguru para a aplicação portfolio-gen.

    Remove o handler padrão e adiciona:
    - Handler de arquivo (DEBUG+) em logs/scan-YYYY-MM-DD.log com rotação diária.
    - Handler de stderr (DEBUG se verbose, INFO caso contrário).

    :param verbose: Exibe mensagens DEBUG no stderr quando True.
    :type verbose: bool
    :param log_dir: Diretório para arquivos de log. Padrão: logs/.
    :type log_dir: Path | None
    :return: None
    :rtype: None

    >>> configure_logging(verbose=False)
    """
    logger.remove()

    resolved_log_dir = log_dir if log_dir is not None else Path("logs")

    try:
        resolved_log_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = resolved_log_dir / f"scan-{date_str}.log"
        logger.add(
            str(log_file),
            level="DEBUG",
            format=_FILE_FORMAT,
            encoding="utf-8",
            rotation="1 day",
            retention="7 days",
        )
    except Exception as exc:
        print(f"Aviso: não foi possível criar arquivo de log: {exc}", file=sys.stderr)

    stderr_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=stderr_level,
        format=_STDERR_FORMAT,
        colorize=True,
    )
