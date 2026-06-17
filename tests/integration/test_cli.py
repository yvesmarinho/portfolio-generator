"""
Testes de integração para a CLI via click CliRunner.

T037 (Phase 5 / US3): `portfolio-gen scan --dry-run`
T040 (Phase 6 / US4): `portfolio-gen validate` (próxima phase)

Escritos ANTES da implementação de T039 (TDD) — os testes de tamanho JSON
e elegibilidade IA devem FALHAR inicialmente.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from cli.main import cli


def _fake_project_data(name: str = "test-project", word_count: int = 50) -> dict[str, object]:
    """Retorna dict de projeto falso compatível com o schema de portfolio."""
    return {
        "name": name,
        "path": f"/fake/{name}",
        "type": "script",
        "description": "Projeto de teste para testes de CLI.",
        "description_source": "readme",
        "language": {"primary": "Python", "secondary": [], "confidence": 0.9},
        "metrics": {"file_count": 5, "size_bytes": 2048, "line_count_estimated": 100},
        "git": {"initialized": False},
        "technologies": ["Python/uv"],
        "status": "active",
        "last_modified": "2026-01-01T00:00:00+00:00",
        "_readme_word_count": word_count,
    }


class TestScanDryRun:
    """T037 (US3): `scan --dry-run` — sumário no stdout, zero arquivos criados."""

    def _invoke(
        self,
        tmp_path: Path,
        extra_args: list[str] | None = None,
        side_effects: list[object] | None = None,
    ) -> object:
        """Invoca `scan --dry-run` com mocks padrão de scanner e executor."""
        runner = CliRunner()
        if side_effects is None:
            side_effects = [_fake_project_data()]
        project_paths = [Path(f"/fake/proj-{i}") for i in range(len(side_effects))]
        args = ["scan", f"--path={tmp_path}", "--dry-run", "--workers", "1"]
        if extra_args:
            args.extend(extra_args)
        with (
            patch("scanner.directory_scanner.validate_path_scope", return_value=True),
            patch(
                "scanner.directory_scanner.DirectoryScanner.list_projects",
                return_value=project_paths,
            ),
            patch(
                "extractor.metadata_extractor.scan_project",
                side_effect=list(side_effects),
            ),
            patch("cli.main.ProcessPoolExecutor", ThreadPoolExecutor),
        ):
            return runner.invoke(cli, args, catch_exceptions=False)

    # --- T037: comportamentos básicos de dry-run ---

    def test_exits_zero(self, tmp_path: Path) -> None:
        """`scan --dry-run` retorna exit code 0."""
        result = self._invoke(tmp_path)
        assert result.exit_code == 0

    def test_no_json_file_created(self, tmp_path: Path) -> None:
        """`scan --dry-run` não cria arquivo JSON de saída em disco."""
        out = tmp_path / "portfolio-test.json"
        self._invoke(tmp_path, extra_args=[f"--output={out}"])
        assert not out.exists()

    def test_summary_table_in_stdout(self, tmp_path: Path) -> None:
        """`scan --dry-run` exibe tabela 'Resultado do Scan' no stdout."""
        result = self._invoke(tmp_path)
        assert "Resultado do Scan" in result.output

    def test_dry_run_message_in_stdout(self, tmp_path: Path) -> None:
        """`scan --dry-run` menciona 'dry-run' no output."""
        result = self._invoke(tmp_path)
        assert "dry-run" in result.output.lower()

    def test_shows_project_count(self, tmp_path: Path) -> None:
        """`scan --dry-run` com 3 projetos exibe '3' no sumário."""
        result = self._invoke(
            tmp_path,
            side_effects=[_fake_project_data(f"proj-{i}") for i in range(3)],
        )
        assert "3" in result.output

    def test_skipped_project_shows_warning(self, tmp_path: Path) -> None:
        """`scan --dry-run` exibe 'pulado' quando um projeto retorna None."""
        result = self._invoke(
            tmp_path,
            side_effects=[None, _fake_project_data()],
        )
        assert "pulado" in result.output.lower()

    # --- T039: sumário enriquecido (tamanho JSON + elegibilidade IA) ---

    def test_shows_estimated_json_size(self, tmp_path: Path) -> None:
        """`scan --dry-run` exibe tamanho estimado do JSON em KB (T039)."""
        result = self._invoke(tmp_path)
        assert "KB" in result.output

    def test_shows_ai_eligible_count(self, tmp_path: Path) -> None:
        """`scan --dry-run` exibe contagem de projetos elegíveis para IA (T039)."""
        result = self._invoke(tmp_path)
        assert "IA" in result.output

    def test_ai_eligible_project_has_short_readme(self, tmp_path: Path) -> None:
        """Projeto com README < 30 palavras deve constar como elegível para IA."""
        # word_count=5 < ai_min_words padrão (30) → elegível para IA
        result = self._invoke(
            tmp_path,
            side_effects=[_fake_project_data("short-readme", word_count=5)],
        )
        assert "IA" in result.output
        # "1" deve aparecer no contexto de elegíveis para IA
        assert "1" in result.output

    def test_ai_not_eligible_with_long_readme(self, tmp_path: Path) -> None:
        """Projeto com README >= 30 palavras não é elegível para IA."""
        # word_count=100 >= ai_min_words(30) → não elegível
        result = self._invoke(
            tmp_path,
            side_effects=[_fake_project_data("long-readme", word_count=100)],
        )
        assert "IA" in result.output
        # elegíveis = 0
        assert "0" in result.output
