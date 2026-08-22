"""
Testes unitários para _write_bug_report() em extractor.metadata_extractor.

TDD — T030 (Phase 4 / US2): escritos ANTES da implementação, devem falhar.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from extractor.metadata_extractor import _write_bug_report, scan_project


class TestWriteBugReport:
    """Testes diretos de _write_bug_report()."""

    def test_creates_report_file(self, tmp_path: Path) -> None:
        """_write_bug_report() cria exatamente um arquivo bug-report-*.md."""
        _write_bug_report(Path("/fake/project"), RuntimeError("err"), tmp_path)
        reports = list(tmp_path.glob("bug-report-*.md"))
        assert len(reports) == 1

    def test_report_contains_project_path(self, tmp_path: Path) -> None:
        """Relatório registra o path do projeto que falhou."""
        project = Path("/fake/my-broken-project")
        _write_bug_report(project, RuntimeError("err"), tmp_path)
        content = list(tmp_path.glob("bug-report-*.md"))[0].read_text()
        assert str(project) in content

    def test_report_contains_exception_type(self, tmp_path: Path) -> None:
        """Relatório registra o tipo da exceção."""
        _write_bug_report(Path("/fake/p"), ValueError("bad"), tmp_path)
        content = list(tmp_path.glob("bug-report-*.md"))[0].read_text()
        assert "ValueError" in content

    def test_report_contains_error_message(self, tmp_path: Path) -> None:
        """Relatório registra a mensagem de erro textual."""
        _write_bug_report(Path("/fake/p"), RuntimeError("specific_error_xyz"), tmp_path)
        content = list(tmp_path.glob("bug-report-*.md"))[0].read_text()
        assert "specific_error_xyz" in content

    def test_report_has_open_status(self, tmp_path: Path) -> None:
        """Relatório tem status OPEN (não resolvido)."""
        _write_bug_report(Path("/fake/p"), RuntimeError("err"), tmp_path)
        content = list(tmp_path.glob("bug-report-*.md"))[0].read_text()
        assert "OPEN" in content

    def test_creates_output_dir_if_missing(self, tmp_path: Path) -> None:
        """_write_bug_report() cria diretório de saída quando não existe."""
        nested = tmp_path / "nested" / "bugs"
        _write_bug_report(Path("/fake/p"), RuntimeError("err"), nested)
        assert nested.exists()
        assert len(list(nested.glob("bug-report-*.md"))) == 1

    def test_report_contains_stack_trace(self, tmp_path: Path) -> None:
        """Relatório inclui stack trace da exceção."""
        try:
            raise RuntimeError("traced error")
        except RuntimeError as exc:
            _write_bug_report(Path("/fake/p"), exc, tmp_path)
        content = list(tmp_path.glob("bug-report-*.md"))[0].read_text()
        assert "Traceback" in content or "traced error" in content


class TestScanProjectWithBugReport:
    """Testes de scan_project() com parâmetro bug_report_dir."""

    def test_returns_none_on_internal_error(self, tmp_path: Path) -> None:
        """scan_project() retorna None quando extrator interno lança exceção."""
        project = tmp_path / "failing-project"
        project.mkdir()
        with patch("extractor.metadata_extractor.detect_language", side_effect=RuntimeError("forced")):
            result = scan_project(project, bug_report_dir=tmp_path / "bugs")
        assert result is None

    def test_writes_bug_report_when_dir_provided(self, tmp_path: Path) -> None:
        """scan_project() grava bug report em bug_report_dir quando erro ocorre."""
        project = tmp_path / "failing-project"
        project.mkdir()
        bug_dir = tmp_path / "bugs"
        with patch("extractor.metadata_extractor.detect_language", side_effect=RuntimeError("forced")):
            scan_project(project, bug_report_dir=bug_dir)
        assert len(list(bug_dir.glob("bug-report-*.md"))) == 1

    def test_no_bug_report_without_dir(self, tmp_path: Path) -> None:
        """scan_project() sem bug_report_dir não cria arquivos bug-report."""
        project = tmp_path / "failing-project"
        project.mkdir()
        with patch("extractor.metadata_extractor.detect_language", side_effect=RuntimeError("forced")):
            scan_project(project, bug_report_dir=None)
        assert not any(tmp_path.rglob("bug-report-*.md"))

    def test_valid_project_still_returns_dict(self, tmp_path: Path) -> None:
        """scan_project() sem erros retorna dict mesmo com bug_report_dir definido."""
        project = tmp_path / "ok-project"
        project.mkdir()
        (project / "main.py").write_text('"""Main."""\n')
        result = scan_project(project, bug_report_dir=tmp_path / "bugs")
        assert result is not None
        assert isinstance(result, dict)
