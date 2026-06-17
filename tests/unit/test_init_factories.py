"""
Testes unitários para as funções factory dos __init__.py de cada módulo.

Cobertura T048 (Phase 8): factory functions cobrindo os ramos válido,
inválido e exceção no construtor — para atingir ≥90% nesses módulos.
"""
from __future__ import annotations

from unittest.mock import patch


class TestCreateExtractor:
    """Factory extractor/__init__.py: create_extractor()."""

    def test_invalid_config_returns_false(self) -> None:
        """`create_extractor({})` retorna False (config vazia)."""
        from extractor import create_extractor

        assert create_extractor({}) is False

    def test_non_dict_config_returns_false(self) -> None:
        """`create_extractor("")` retorna False (config inválida)."""
        from extractor import create_extractor

        assert create_extractor("") is False  # type: ignore[arg-type]

    def test_valid_config_returns_instance(self) -> None:
        """`create_extractor(valid)` retorna instância de MetadataExtractor."""
        from extractor import create_extractor

        result = create_extractor({"no_ai": True, "ai_min_words": 30, "ai_max_tokens": 2000})
        assert result is not False
        assert hasattr(result, "extract")

    def test_constructor_error_returns_false(self) -> None:
        """`create_extractor` captura exceção do construtor e retorna False."""
        from extractor import create_extractor

        # Passar valor inválido causa ValueError em int() dentro do __init__
        result = create_extractor({"ai_min_words": "nao-e-inteiro"})
        assert result is False


class TestCreateGenerator:
    """Factory generator/__init__.py: create_generator()."""

    def test_invalid_config_returns_false(self) -> None:
        """`create_generator({})` retorna False (config vazia)."""
        from generator import create_generator

        assert create_generator({}) is False

    def test_non_dict_config_returns_false(self) -> None:
        """`create_generator(None)` retorna False."""
        from generator import create_generator

        assert create_generator(None) is False  # type: ignore[arg-type]

    def test_valid_config_returns_instance(self) -> None:
        """`create_generator(valid)` retorna instância de PortfolioGenerator."""
        from generator import create_generator

        result = create_generator({
            "schema_path": "schemas/portfolio-schema-v1.json",
            "generator_version": "1.0.0",
        })
        assert result is not False
        assert hasattr(result, "build_portfolio")

    def test_constructor_error_returns_false(self) -> None:
        """`create_generator` captura exceção mockada do construtor."""
        from generator import create_generator

        with patch(
            "generator.portfolio_generator.PortfolioGenerator",
            side_effect=RuntimeError("mock error"),
        ):
            result = create_generator({"key": "val"})
        assert result is False


class TestCreateScanner:
    """Factory scanner/__init__.py: create_scanner()."""

    def test_invalid_config_returns_false(self) -> None:
        """`create_scanner({})` retorna False (config vazia)."""
        from scanner import create_scanner

        assert create_scanner({}) is False

    def test_non_dict_config_returns_false(self) -> None:
        """`create_scanner(42)` retorna False."""
        from scanner import create_scanner

        assert create_scanner(42) is False  # type: ignore[arg-type]

    def test_valid_config_returns_instance(self) -> None:
        """`create_scanner(valid)` retorna instância de DirectoryScanner."""
        from scanner import create_scanner

        result = create_scanner({"root_path": "/tmp", "excluded_dirs": [], "max_depth": 1})
        assert result is not False
        assert hasattr(result, "list_projects")

    def test_constructor_error_returns_false(self) -> None:
        """`create_scanner` captura exceção no construtor quando max_depth inválido."""
        from scanner import create_scanner

        # Valor inválido causa ValueError em int() dentro do __init__
        result = create_scanner({"max_depth": "nao-e-inteiro"})
        assert result is False


class TestCreateAnalyzer:
    """Factory analyzer/__init__.py: create_analyzer()."""

    def test_invalid_config_returns_false(self) -> None:
        """`create_analyzer({})` retorna False (config vazia)."""
        from analyzer import create_analyzer

        assert create_analyzer({}) is False

    def test_non_dict_config_returns_false(self) -> None:
        """`create_analyzer("")` retorna False."""
        from analyzer import create_analyzer

        assert create_analyzer("") is False  # type: ignore[arg-type]

    def test_valid_config_returns_false_when_module_missing(self) -> None:
        """
        `create_analyzer(valid)` retorna False quando ProjectAnalyzer não existe (Phase 7).

        Cobre o bloco except da factory function.
        """
        from analyzer import create_analyzer

        result = create_analyzer({"ai_min_words": 30, "ai_max_tokens": 2000, "no_ai": True})
        # ProjectAnalyzer não implementado → ImportError → except → False
        assert result is False
