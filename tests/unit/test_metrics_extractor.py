"""
Testes unitários para extractor.metrics_extractor.

TDD: escritos ANTES da implementação.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from extractor.metrics_extractor import ProjectMetrics, extract_metrics


class TestProjectMetrics:
    """Testes para o dataclass ProjectMetrics."""

    def test_project_metrics_attributes(self) -> None:
        """ProjectMetrics expõe file_count, size_bytes e line_count_estimated."""
        m = ProjectMetrics(file_count=10, size_bytes=4096, line_count_estimated=200)
        assert m.file_count == 10
        assert m.size_bytes == 4096
        assert m.line_count_estimated == 200


class TestExtractMetrics:
    """Testes para a função extract_metrics."""

    def test_python_project_has_files(self, python_project: Path) -> None:
        """python_project tem pelo menos 3 arquivos (README, main.py, pyproject.toml)."""
        result = extract_metrics(python_project)
        assert result.file_count >= 3

    def test_python_project_size_positive(self, python_project: Path) -> None:
        """size_bytes é positivo para projeto com arquivos."""
        result = extract_metrics(python_project)
        assert result.size_bytes > 0

    def test_python_project_line_count_non_negative(self, python_project: Path) -> None:
        """line_count_estimated é não-negativo."""
        result = extract_metrics(python_project)
        assert result.line_count_estimated >= 0

    def test_empty_project_file_count_zero(self, empty_project: Path) -> None:
        """Projeto vazio tem file_count=0 e size_bytes=0."""
        result = extract_metrics(empty_project)
        assert result.file_count == 0
        assert result.size_bytes == 0

    def test_nonexistent_path_returns_zeros(self) -> None:
        """Path inexistente retorna métricas zeradas sem exceção."""
        result = extract_metrics(Path("/nonexistent_xyzabc"))
        assert result.file_count == 0
        assert result.size_bytes == 0
        assert result.line_count_estimated == 0

    def test_returns_project_metrics_type(self, python_project: Path) -> None:
        """Retorno é instância de ProjectMetrics."""
        result = extract_metrics(python_project)
        assert isinstance(result, ProjectMetrics)

    def test_corrupted_project_handled_gracefully(self, corrupted_project: Path) -> None:
        """Projeto com arquivo corrompido não lança exceção."""
        result = extract_metrics(corrupted_project)
        assert isinstance(result, ProjectMetrics)
        assert result.file_count >= 0

    def test_no_readme_project_counts_files(self, no_readme_project: Path) -> None:
        """no_readme_project tem pelo menos 1 arquivo (script.py)."""
        result = extract_metrics(no_readme_project)
        assert result.file_count >= 1


class TestMetricsExtractorCoverage:
    """Cobertura T048: exception paths em extract_metrics e _compute_metrics (linhas 49-51, 84-85)."""

    def test_exception_in_compute_returns_zeros(self, tmp_path: Path) -> None:
        """_compute_metrics lançando exceção → extract_metrics retorna zeros (linhas 49-51)."""
        (tmp_path / "main.py").write_text("print('hello')")
        with patch("extractor.metrics_extractor._compute_metrics", side_effect=RuntimeError("forced")):
            result = extract_metrics(tmp_path)
        assert result.file_count == 0
        assert result.size_bytes == 0
        assert result.line_count_estimated == 0

    def test_rglob_permission_error_returns_partial_metrics(self, tmp_path: Path) -> None:
        """PermissionError em rglob dentro de _compute_metrics é tratado (linhas 84-85)."""
        (tmp_path / "main.py").write_text("print('hello')")
        with patch("pathlib.Path.rglob", side_effect=PermissionError("sem permissão")):
            result = extract_metrics(tmp_path)
        assert isinstance(result, ProjectMetrics)
        assert result.file_count == 0
