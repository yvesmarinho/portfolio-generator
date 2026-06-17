"""
Testes unitários para generator.portfolio_generator.

TDD: escritos ANTES da implementação.
"""
from __future__ import annotations

from pathlib import Path

from generator.portfolio_generator import PortfolioGenerator

VALID_PROJECT: dict[str, object] = {
    "name": "test-project",
    "path": "/home/yves_marinho/Documentos/DevOps/test-project",
    "type": "unknown",
    "description": "Projeto de teste para validação do schema.",
    "description_source": "readme",
    "language": {"primary": "Python", "secondary": [], "confidence": 0.9},
    "metrics": {"file_count": 5, "size_bytes": 1024, "line_count_estimated": 100},
    "git": {"initialized": False},
    "technologies": ["Python"],
    "status": "unknown",
    "last_modified": "2026-06-17T00:00:00+00:00",
}

META: dict[str, object] = {
    "scan_path": "/home/yves_marinho/Documentos/DevOps/",
    "scan_duration_seconds": 1.0,
    "skipped_projects": 0,
}

SCHEMA_PATH = Path("schemas/portfolio-schema-v1.json")


class TestPortfolioGeneratorInit:
    """Testes para inicialização do PortfolioGenerator."""

    def test_init_with_valid_config(self) -> None:
        """Construtor aceita configuração com schema_path e generator_version."""
        config: dict[str, object] = {
            "schema_path": str(SCHEMA_PATH),
            "generator_version": "1.0.0",
        }
        gen = PortfolioGenerator(config)
        assert gen is not None


class TestBuildPortfolio:
    """Testes para PortfolioGenerator.build_portfolio()."""

    def test_returns_dict(self) -> None:
        """build_portfolio retorna um dicionário."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        result = gen.build_portfolio([dict(VALID_PROJECT)], META)
        assert isinstance(result, dict)

    def test_has_required_top_level_keys(self) -> None:
        """Portfolio contém todos os campos obrigatórios do schema."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        result = gen.build_portfolio([dict(VALID_PROJECT)], META)
        assert "generated_at" in result
        assert "generator_version" in result
        assert "scan_path" in result
        assert "total_projects" in result
        assert "skipped_projects" in result
        assert "scan_duration_seconds" in result
        assert "projects" in result

    def test_total_projects_matches_list_length(self) -> None:
        """total_projects == len(projects)."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        result = gen.build_portfolio([dict(VALID_PROJECT), dict(VALID_PROJECT)], META)
        assert result["total_projects"] == 2
        assert len(result["projects"]) == 2  # type: ignore[arg-type]

    def test_project_path_is_relative(self) -> None:
        """path do projeto é relativo ao scan_path (sem / inicial)."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        result = gen.build_portfolio([dict(VALID_PROJECT)], META)
        project_path = result["projects"][0]["path"]  # type: ignore[index]
        assert not str(project_path).startswith("/")

    def test_generator_version_set(self) -> None:
        """generator_version usa a versão configurada."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        result = gen.build_portfolio([dict(VALID_PROJECT)], META)
        assert result["generator_version"] == "1.0.0"

    def test_empty_projects_list(self) -> None:
        """build_portfolio aceita lista vazia de projetos."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        result = gen.build_portfolio([], META)
        assert result["total_projects"] == 0
        assert result["projects"] == []


class TestValidateSchema:
    """Testes para PortfolioGenerator.validate_schema()."""

    def test_valid_portfolio_returns_true(self) -> None:
        """Portfolio bem formado passa na validação."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        portfolio = gen.build_portfolio([dict(VALID_PROJECT)], META)
        assert gen.validate_schema(portfolio, SCHEMA_PATH) is True

    def test_invalid_portfolio_returns_false(self) -> None:
        """Portfolio com campos faltando não passa na validação."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        invalid: dict[str, object] = {"foo": "bar"}
        assert gen.validate_schema(invalid, SCHEMA_PATH) is False

    def test_missing_required_field_returns_false(self) -> None:
        """Portfolio sem 'total_projects' falha na validação."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        portfolio = gen.build_portfolio([dict(VALID_PROJECT)], META)
        portfolio.pop("total_projects")  # type: ignore[union-attr]
        assert gen.validate_schema(portfolio, SCHEMA_PATH) is False

    def test_schema_not_found_returns_false(self) -> None:
        """Schema inexistente retorna False sem exceção."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        portfolio = gen.build_portfolio([dict(VALID_PROJECT)], META)
        assert gen.validate_schema(portfolio, Path("/nonexistent/schema.json")) is False


class TestWriteOutput:
    """Testes para PortfolioGenerator.write_output()."""

    def test_creates_json_file(self, tmp_path: Path) -> None:
        """write_output cria arquivo JSON no path especificado."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        portfolio = gen.build_portfolio([dict(VALID_PROJECT)], META)
        output = tmp_path / "portfolio.json"
        assert gen.write_output(portfolio, output) is True
        assert output.exists()

    def test_output_is_valid_json(self, tmp_path: Path) -> None:
        """Arquivo criado é JSON válido."""
        import json

        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        portfolio = gen.build_portfolio([dict(VALID_PROJECT)], META)
        output = tmp_path / "portfolio.json"
        gen.write_output(portfolio, output)
        content = json.loads(output.read_text())
        assert "projects" in content

    def test_invalid_path_returns_false(self) -> None:
        """Path inválido (dir sem permissão) retorna False sem exceção."""
        gen = PortfolioGenerator({"schema_path": str(SCHEMA_PATH), "generator_version": "1.0.0"})
        portfolio = gen.build_portfolio([dict(VALID_PROJECT)], META)
        assert gen.write_output(portfolio, Path("/root/no-permission/output.json")) is False
