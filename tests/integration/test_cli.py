"""
Testes de integração para a CLI via click CliRunner.

T037 (Phase 5 / US3): `portfolio-gen scan --dry-run`
T040 (Phase 6 / US4): `portfolio-gen validate`
"""
from __future__ import annotations

import json
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


def _valid_portfolio(tmp_path: Path, n_projects: int = 1) -> Path:
    """Cria arquivo portfolio JSON válido conforme schema v1."""
    projects = [
        {
            "name": f"project-{i}",
            "path": f"project-{i}",
            "type": "script",
            "description": "Projeto de teste.",
            "description_source": "readme",
            "language": {"primary": "Python", "secondary": [], "confidence": 0.9},
            "metrics": {"file_count": 3, "size_bytes": 1024, "line_count_estimated": 50},
            "git": {"initialized": False},
            "technologies": [],
            "status": "active",
            "last_modified": "2026-06-17T10:00:00+00:00",
        }
        for i in range(n_projects)
    ]
    portfolio = {
        "generated_at": "2026-06-17T10:00:00+00:00",
        "generator_version": "1.0.0",
        "scan_path": "/fake/devops",
        "total_projects": n_projects,
        "skipped_projects": 0,
        "scan_duration_seconds": 1.5,
        "projects": projects,
    }
    out = tmp_path / "portfolio.json"
    out.write_text(json.dumps(portfolio), encoding="utf-8")
    return out


class TestValidateCommand:
    """T040 (US4): `validate` via CliRunner."""

    def test_valid_json_exits_zero(self, tmp_path: Path) -> None:
        """`validate` em portfolio JSON válido → exit 0."""
        runner = CliRunner()
        portfolio_file = _valid_portfolio(tmp_path)
        result = runner.invoke(cli, ["validate", str(portfolio_file)], catch_exceptions=False)
        assert result.exit_code == 0

    def test_valid_json_shows_success_message(self, tmp_path: Path) -> None:
        """`validate` em portfolio válido exibe mensagem de sucesso."""
        runner = CliRunner()
        portfolio_file = _valid_portfolio(tmp_path)
        result = runner.invoke(cli, ["validate", str(portfolio_file)], catch_exceptions=False)
        assert "válido" in result.output.lower() or "✓" in result.output

    def test_missing_required_field_exits_one(self, tmp_path: Path) -> None:
        """`validate` em JSON sem campo obrigatório → exit 1."""
        runner = CliRunner()
        invalid = tmp_path / "invalid.json"
        invalid.write_text(json.dumps({"total_projects": 0}), encoding="utf-8")
        result = runner.invoke(cli, ["validate", str(invalid)], catch_exceptions=False)
        assert result.exit_code == 1

    def test_invalid_json_shows_missing_field_name(self, tmp_path: Path) -> None:
        """`validate` em JSON inválido exibe nome do campo violado (T042)."""
        runner = CliRunner()
        invalid = tmp_path / "invalid.json"
        invalid.write_text(json.dumps({"total_projects": 0}), encoding="utf-8")
        result = runner.invoke(cli, ["validate", str(invalid)], catch_exceptions=False)
        assert any(
            field in result.output
            for field in ["generated_at", "generator_version", "scan_path", "violação", "missing"]
        )

    def test_invalid_json_shows_json_path(self, tmp_path: Path) -> None:
        """`validate` em JSON inválido exibe path no JSON (T042)."""
        runner = CliRunner()
        invalid = tmp_path / "invalid.json"
        invalid.write_text(json.dumps({"total_projects": 0}), encoding="utf-8")
        result = runner.invoke(cli, ["validate", str(invalid)], catch_exceptions=False)
        assert "$" in result.output

    def test_nonexistent_file_exits_nonzero(self, tmp_path: Path) -> None:
        """`validate` em arquivo inexistente → exit não-zero."""
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(tmp_path / "nonexistent.json")])
        assert result.exit_code != 0

    def test_invalid_json_syntax_exits_one(self, tmp_path: Path) -> None:
        """`validate` em arquivo com JSON inválido (sintaxe) → exit 1."""
        runner = CliRunner()
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{ not valid json }", encoding="utf-8")
        result = runner.invoke(cli, ["validate", str(bad_json)], catch_exceptions=False)
        assert result.exit_code == 1

    def test_valid_empty_projects_list_exits_zero(self, tmp_path: Path) -> None:
        """`validate` em portfolio válido com zero projetos → exit 0."""
        runner = CliRunner()
        portfolio_file = _valid_portfolio(tmp_path, n_projects=0)
        result = runner.invoke(cli, ["validate", str(portfolio_file)], catch_exceptions=False)
        assert result.exit_code == 0

    def test_wrong_type_field_exits_one(self, tmp_path: Path) -> None:
        """`validate` em portfolio com tipo errado em campo → exit 1."""
        runner = CliRunner()
        portfolio_file = _valid_portfolio(tmp_path)
        data = json.loads(portfolio_file.read_text())
        data["total_projects"] = "não-é-inteiro"  # viola type: integer
        portfolio_file.write_text(json.dumps(data), encoding="utf-8")
        result = runner.invoke(cli, ["validate", str(portfolio_file)], catch_exceptions=False)
        assert result.exit_code == 1
