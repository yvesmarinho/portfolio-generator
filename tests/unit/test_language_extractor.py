"""
Testes unitários para extractor.language_extractor.

TDD: escritos ANTES da implementação.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from extractor.language_extractor import LanguageInfo, _iter_source_files, detect_language


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


class TestLanguageExtractorCoverage:
    """Cobertura T048: exception paths, pygments e _iter_source_files."""

    def test_detect_language_exception_returns_unknown(self, tmp_path: Path) -> None:
        """Exceção em _detect_by_extension → detect_language retorna Unknown (linhas 102-104)."""
        (tmp_path / "main.py").write_text("print('hello')")
        with patch("extractor.language_extractor._detect_by_extension", side_effect=RuntimeError("forced")):
            result = detect_language(tmp_path)
        assert result.primary == "Unknown"
        assert result.confidence == 0.0

    def test_iter_source_files_permission_error_returns_empty(self, tmp_path: Path) -> None:
        """PermissionError em rglob → _iter_source_files retorna [] (linhas 146-147)."""
        with patch("pathlib.Path.rglob", side_effect=PermissionError("sem permissão")):
            result = _iter_source_files(tmp_path)
        assert result == []

    def test_mixed_project_triggers_confirm_with_pygments(self, tmp_path: Path) -> None:
        """Projeto misto com confiança < 0.60 aciona _confirm_with_pygments (linhas 131, 158-187)."""
        for i in range(2):
            (tmp_path / f"script_{i}.py").write_text(f"print({i})")
        for i in range(2):
            (tmp_path / f"app_{i}.js").write_text(f"console.log({i})")
        for i in range(2):
            (tmp_path / f"main_{i}.go").write_text("package main")
        for i in range(2):
            (tmp_path / f"type_{i}.ts").write_text(f"const x: number = {i}")
        (tmp_path / "data.xyz").write_text("unknown extension")
        result = detect_language(tmp_path)
        assert isinstance(result, LanguageInfo)
        assert result.primary != ""
        assert 0.0 <= result.confidence <= 1.0

    def test_confirm_with_pygments_exception_returns_original(self, tmp_path: Path) -> None:
        """Exceção genérica no pygments → retorna info original (linhas 188-191)."""
        from extractor.language_extractor import _confirm_with_pygments

        (tmp_path / "main.py").write_text("print('hello')")
        with patch("pygments.lexers.guess_lexer_for_filename", side_effect=RuntimeError("pygments quebrado")):
            result = _confirm_with_pygments(tmp_path, "Python", ["Go"], 0.5)
        assert result.primary == "Python"
        assert result.confidence == 0.5
