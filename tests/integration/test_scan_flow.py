"""
Testes de integração para o fluxo completo de scan.

T020: scan end-to-end em tests/fixtures/ — projetos detectados, JSON válido contra schema.
T031 (US2): cenários com projeto corrompido — skipped_projects contabilizado.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from extractor.metadata_extractor import scan_project
from generator.portfolio_generator import PortfolioGenerator
from scanner.directory_scanner import DirectoryScanner

SCHEMA_PATH = Path("schemas/portfolio-schema-v1.json")


class TestScanProject:
    """Testes para a função standalone scan_project()."""

    def test_scan_project_returns_dict(self, python_project: Path) -> None:
        """scan_project retorna um dicionário para projeto válido."""
        result = scan_project(python_project)
        assert result is not None
        assert isinstance(result, dict)

    def test_scan_project_has_required_fields(self, python_project: Path) -> None:
        """Dicionário retornado contém todos os campos obrigatórios do schema."""
        result = scan_project(python_project)
        assert result is not None
        for field in ("name", "path", "type", "description", "description_source",
                      "language", "metrics", "git", "technologies", "status", "last_modified"):
            assert field in result, f"Campo '{field}' ausente no resultado"

    def test_scan_project_language_structure(self, python_project: Path) -> None:
        """Subestrutura language tem primary, secondary, confidence."""
        result = scan_project(python_project)
        assert result is not None
        lang = result["language"]
        assert "primary" in lang  # type: ignore[operator]
        assert "secondary" in lang  # type: ignore[operator]
        assert "confidence" in lang  # type: ignore[operator]

    def test_scan_project_metrics_structure(self, python_project: Path) -> None:
        """Subestrutura metrics tem file_count e size_bytes."""
        result = scan_project(python_project)
        assert result is not None
        metrics = result["metrics"]
        assert "file_count" in metrics  # type: ignore[operator]
        assert "size_bytes" in metrics  # type: ignore[operator]

    def test_scan_project_git_structure(self, python_project: Path) -> None:
        """Subestrutura git tem initialized."""
        result = scan_project(python_project)
        assert result is not None
        git = result["git"]
        assert "initialized" in git  # type: ignore[operator]

    def test_scan_project_no_git_returns_initialized_false(self, no_git_project: Path) -> None:
        """Projeto sem git tem git.initialized=False."""
        result = scan_project(no_git_project)
        assert result is not None
        assert result["git"]["initialized"] is False  # type: ignore[index]

    def test_scan_project_with_readme_has_description(self, python_project: Path) -> None:
        """Projeto com README tem description_source='readme'."""
        result = scan_project(python_project)
        assert result is not None
        assert result["description_source"] == "readme"

    def test_scan_project_without_readme_has_empty_source(self, no_readme_project: Path) -> None:
        """Projeto sem README tem description_source='empty'."""
        result = scan_project(no_readme_project)
        assert result is not None
        assert result["description_source"] in ("empty", "filename")

    def test_scan_project_nonexistent_returns_none(self) -> None:
        """Path inexistente retorna None sem exceção."""
        result = scan_project(Path("/nonexistent_xyzabc"))
        assert result is None

    def test_scan_project_corrupted_handled_gracefully(self, corrupted_project: Path) -> None:
        """Projeto com arquivo corrompido retorna dict ou None (nunca exceção)."""
        result = scan_project(corrupted_project)
        assert result is None or isinstance(result, dict)


class TestScanAndBuildFlow:
    """Testes do fluxo scan → build → validate."""

    def test_build_portfolio_from_scan_result(self, python_project: Path) -> None:
        """scan_project + build_portfolio produz portfolio válido."""
        result = scan_project(python_project)
        assert result is not None

        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        meta = {
            "scan_path": str(python_project.parent),
            "scan_duration_seconds": 0.1,
            "skipped_projects": 0,
        }
        portfolio = gen.build_portfolio([result], meta)
        assert portfolio["total_projects"] == 1

    def test_schema_validation_passes_for_scan_result(self, python_project: Path) -> None:
        """Portfolio gerado por scan_project valida contra o schema JSON."""
        result = scan_project(python_project)
        assert result is not None

        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        meta = {
            "scan_path": str(python_project.parent),
            "scan_duration_seconds": 0.1,
            "skipped_projects": 0,
        }
        portfolio = gen.build_portfolio([result], meta)
        assert gen.validate_schema(portfolio, SCHEMA_PATH) is True

    def test_write_output_creates_valid_file(self, python_project: Path, tmp_path: Path) -> None:
        """Fluxo completo grava JSON válido em disco."""
        result = scan_project(python_project)
        assert result is not None

        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        meta = {
            "scan_path": str(python_project.parent),
            "scan_duration_seconds": 0.1,
            "skipped_projects": 0,
        }
        portfolio = gen.build_portfolio([result], meta)
        output_path = tmp_path / "portfolio-test.json"
        assert gen.write_output(portfolio, output_path) is True
        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert "projects" in data
        assert len(data["projects"]) == 1

    def test_scan_fixtures_finds_projects(
        self,
        fixtures_dir: Path,
        python_project: Path,
        empty_project: Path,
        no_readme_project: Path,
        no_git_project: Path,
    ) -> None:
        """Scanner detecta pelo menos 4 projetos nas fixtures."""
        config: dict[str, object] = {
            "root_path": str(fixtures_dir),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        projects = scanner.list_projects(fixtures_dir)
        names = [p.name for p in projects]
        assert "python_project" in names
        assert len(projects) >= 4


class TestScanFlowWithErrors:
    """T031 (US2): fluxo com projeto que falha — N-1 resultados, bug-report gerado."""

    def test_scan_error_isolated_no_exception_propagated(self, python_project: Path, tmp_path: Path) -> None:
        """Falha interna em scan_project() retorna None sem propagar exceção."""
        with patch("extractor.metadata_extractor.detect_language", side_effect=RuntimeError("iso")):
            result = scan_project(python_project, bug_report_dir=tmp_path / "bugs")
        assert result is None

    def test_portfolio_skipped_projects_reflects_failures(self, python_project: Path) -> None:
        """Portfolio com skipped_projects=1 registra a contagem corretamente."""
        valid = scan_project(python_project)
        assert valid is not None
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        meta = {"scan_path": str(python_project.parent), "scan_duration_seconds": 0.1, "skipped_projects": 1}
        portfolio = gen.build_portfolio([valid], meta)
        assert portfolio["skipped_projects"] == 1
        assert portfolio["total_projects"] == 1

    def test_portfolio_schema_valid_with_skipped_projects(self, python_project: Path) -> None:
        """Portfolio com skipped_projects ainda passa na validação do schema."""
        valid = scan_project(python_project)
        assert valid is not None
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        meta = {"scan_path": str(python_project.parent), "scan_duration_seconds": 0.1, "skipped_projects": 1}
        portfolio = gen.build_portfolio([valid], meta)
        assert gen.validate_schema(portfolio, SCHEMA_PATH) is True

    def test_bug_report_created_for_failed_project(self, python_project: Path, tmp_path: Path) -> None:
        """Bug report é gravado quando scan_project() falha num projeto real."""
        bug_dir = tmp_path / "bugs"
        with patch("extractor.metadata_extractor.detect_language", side_effect=RuntimeError("fail")):
            scan_project(python_project, bug_report_dir=bug_dir)
        reports = list(bug_dir.glob("bug-report-*.md"))
        assert len(reports) == 1
        assert str(python_project) in reports[0].read_text()
