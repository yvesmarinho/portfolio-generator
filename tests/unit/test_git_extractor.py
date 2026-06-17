"""
Testes unitários para extractor.git_extractor.

TDD: escritos ANTES da implementação.
"""
from __future__ import annotations

from pathlib import Path

from extractor.git_extractor import GitInfo, extract_git_info


class TestGitInfo:
    """Testes para o dataclass GitInfo."""

    def test_git_info_attributes(self) -> None:
        """GitInfo expõe todos os campos esperados."""
        info = GitInfo(
            branch="main",
            last_commit_hash="abc1234",
            last_commit_date="2026-06-17T00:00:00+00:00",
            last_commit_author="Test User",
            commit_count=5,
        )
        assert info.branch == "main"
        assert info.last_commit_hash == "abc1234"
        assert info.last_commit_date == "2026-06-17T00:00:00+00:00"
        assert info.last_commit_author == "Test User"
        assert info.commit_count == 5


class TestExtractGitInfo:
    """Testes para a função extract_git_info."""

    def test_git_project_returns_git_info(self, git_project: Path) -> None:
        """Projeto com git retorna instância de GitInfo."""
        result = extract_git_info(git_project)
        assert result is not None
        assert isinstance(result, GitInfo)

    def test_no_git_project_returns_none(self, no_git_project: Path) -> None:
        """Projeto sem git retorna None."""
        result = extract_git_info(no_git_project)
        assert result is None

    def test_nonexistent_path_returns_none(self) -> None:
        """Path inexistente retorna None sem exceção."""
        result = extract_git_info(Path("/nonexistent_xyzabc"))
        assert result is None

    def test_git_info_has_branch_string(self, git_project: Path) -> None:
        """GitInfo.branch é uma string não vazia."""
        result = extract_git_info(git_project)
        assert result is not None
        assert isinstance(result.branch, str)
        assert len(result.branch) > 0

    def test_git_info_has_commit_hash(self, git_project: Path) -> None:
        """GitInfo.last_commit_hash tem exatamente 7 caracteres."""
        result = extract_git_info(git_project)
        assert result is not None
        assert isinstance(result.last_commit_hash, str)
        assert len(result.last_commit_hash) == 7

    def test_git_info_commit_count_positive(self, git_project: Path) -> None:
        """GitInfo.commit_count é inteiro > 0 para repo com commits."""
        result = extract_git_info(git_project)
        assert result is not None
        assert isinstance(result.commit_count, int)
        assert result.commit_count >= 1

    def test_git_info_has_last_commit_date(self, git_project: Path) -> None:
        """GitInfo.last_commit_date é string ISO-8601."""
        result = extract_git_info(git_project)
        assert result is not None
        assert isinstance(result.last_commit_date, str)
        assert "T" in result.last_commit_date  # formato ISO-8601

    def test_git_info_has_author(self, git_project: Path) -> None:
        """GitInfo.last_commit_author é string não vazia."""
        result = extract_git_info(git_project)
        assert result is not None
        assert isinstance(result.last_commit_author, str)
        assert len(result.last_commit_author) > 0

    def test_empty_project_returns_none(self, empty_project: Path) -> None:
        """Diretório sem git retorna None."""
        result = extract_git_info(empty_project)
        assert result is None
