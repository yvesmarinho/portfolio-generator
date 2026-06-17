"""
Testes unitários para cli._logging.configure_logging.

Cobertura T048 (Phase 8): exception path quando mkdir falha (linhas 58-59).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


class TestConfigureLogging:
    """Testes para configure_logging()."""

    def test_configure_logging_success(self, tmp_path: Path) -> None:
        """configure_logging cria arquivo de log e não lança exceção."""
        from cli._logging import configure_logging

        configure_logging(verbose=False, log_dir=tmp_path / "logs")

    def test_configure_logging_verbose_mode(self, tmp_path: Path) -> None:
        """configure_logging verbose=True configura handler DEBUG sem exceção."""
        from cli._logging import configure_logging

        configure_logging(verbose=True, log_dir=tmp_path / "logs_verbose")

    def test_mkdir_failure_prints_warning_to_stderr(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Quando mkdir falha, imprime aviso no stderr e não lança exceção (linhas 58-59)."""
        from cli._logging import configure_logging

        bad_log_dir = tmp_path / "log_dir"
        bad_log_dir.write_text("arquivo, não diretório")
        configure_logging(verbose=False, log_dir=bad_log_dir)
        captured = capsys.readouterr()
        assert "Aviso" in captured.err
