"""
Testes unitários para extractor.language_extractor.

TDD: escritos ANTES da implementação.
"""
from __future__ import annotations

from pathlib import Path

from extractor.language_extractor import LanguageInfo, detect_language


class TestLanguageInfo:
    """Testes para o dataclass LanguageInfo."""

    def test_language_info_attributes(self) -> None:
        """LanguageInfo expõe primary, secondary e confidence."""
        info = LanguageInfo(primary="Python", secondary=["YAML"], confidence=0.9)
        assert info.primary == "Python"
        assert info.secondary == ["YAML"]
        assert info.confidence == 0.9

    def test_language_info_empty_secondary(self) -> None:
        """secondary pode ser lista vazia."""
        info = LanguageInfo(primary="Go", secondary=[], confidence=1.0)
        assert info.secondary == []


class TestDetectLanguage:
    """Testes para a função detect_language (cascata 3 níveis)."""

    def test_python_project_detects_python(self, python_project: Path) -> None:
        """Projeto com .py detecta Python como primária."""
        result = detect_language(python_project)
        assert result.primary == "Python"

    def test_confidence_between_0_and_1(self, python_project: Path) -> None:
        """Confiança fica entre 0.0 e 1.0."""
        result = detect_language(python_project)
        assert 0.0 <= result.confidence <= 1.0

    def test_secondary_is_list(self, python_project: Path) -> None:
        """Campo secondary é sempre uma lista."""
        result = detect_language(python_project)
        assert isinstance(result.secondary, list)

    def test_empty_project_returns_unknown(self, empty_project: Path) -> None:
        """Projeto sem arquivos retorna 'Unknown'."""
        result = detect_language(empty_project)
        assert result.primary == "Unknown"
        assert result.confidence == 0.0

    def test_nonexistent_path_returns_unknown(self) -> None:
        """Path inexistente retorna 'Unknown' sem lançar exceção."""
        result = detect_language(Path("/nonexistent_dir_xyzabc"))
        assert result.primary == "Unknown"

    def test_no_readme_project_detects_python(self, no_readme_project: Path) -> None:
        """Projeto sem README mas com .py detecta Python."""
        result = detect_language(no_readme_project)
        assert result.primary == "Python"

    def test_returns_language_info_type(self, python_project: Path) -> None:
        """Retorno é instância de LanguageInfo."""
        result = detect_language(python_project)
        assert isinstance(result, LanguageInfo)

    def test_unknown_has_zero_confidence(self) -> None:
        """primary='Unknown' implica confidence=0.0."""
        result = detect_language(Path("/nonexistent_xyzabc"))
        assert result.confidence == 0.0
