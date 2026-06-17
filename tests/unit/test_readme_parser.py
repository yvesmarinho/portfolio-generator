"""
Testes unitários para analyzer.readme_parser.

TDD: escritos ANTES da implementação.
"""
from __future__ import annotations

from pathlib import Path

from analyzer.readme_parser import extract_description, parse_readme, token_count, word_count


class TestParseReadme:
    """Testes para parse_readme(path) -> str | None."""

    def test_returns_string_for_project_with_readme(self, python_project: Path) -> None:
        """python_project tem README.md — deve retornar string não vazia."""
        result = parse_readme(python_project)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_none_for_project_without_readme(self, no_readme_project: Path) -> None:
        """no_readme_project não tem README — deve retornar None."""
        result = parse_readme(no_readme_project)
        assert result is None

    def test_returns_none_for_nonexistent_dir(self) -> None:
        """Path inexistente retorna None sem exceção."""
        result = parse_readme(Path("/nonexistent_xyzabc"))
        assert result is None

    def test_returns_none_for_empty_project(self, empty_project: Path) -> None:
        """Projeto sem arquivos retorna None."""
        result = parse_readme(empty_project)
        assert result is None

    def test_readme_content_contains_text(self, python_project: Path) -> None:
        """O conteúdo do README contém texto do arquivo."""
        result = parse_readme(python_project)
        assert result is not None
        assert "Python" in result or "python" in result.lower() or len(result) > 10

    def test_no_git_project_readme(self, no_git_project: Path) -> None:
        """no_git_project tem README — deve ser lido."""
        result = parse_readme(no_git_project)
        assert result is not None


class TestWordCount:
    """Testes para word_count(text: str) -> int."""

    def test_basic_count(self) -> None:
        """Conta palavras corretamente em frase simples."""
        assert word_count("hello world") == 2

    def test_empty_string(self) -> None:
        """String vazia retorna 0."""
        assert word_count("") == 0

    def test_multiple_spaces(self) -> None:
        """Múltiplos espaços não inflam a contagem."""
        assert word_count("hello   world") == 2

    def test_newlines_count_as_separators(self) -> None:
        """Newlines separam palavras."""
        assert word_count("hello\nworld") == 2

    def test_single_word(self) -> None:
        """Uma palavra retorna 1."""
        assert word_count("python") == 1

    def test_longer_text(self) -> None:
        """Texto com 10 palavras retorna 10."""
        text = "one two three four five six seven eight nine ten"
        assert word_count(text) == 10


class TestTokenCount:
    """Testes para token_count(text: str) -> int (estimativa chars/4)."""

    def test_token_count_approximation(self) -> None:
        """100 chars ÷ 4 = 25 tokens estimados."""
        text = "a" * 100
        assert token_count(text) == 25

    def test_token_count_empty(self) -> None:
        """String vazia retorna 0."""
        assert token_count("") == 0

    def test_token_count_four_chars(self) -> None:
        """4 chars = 1 token."""
        assert token_count("abcd") == 1

    def test_token_count_non_divisible(self) -> None:
        """5 chars ÷ 4 = 1 token (divisão inteira)."""
        assert token_count("abcde") == 1


class TestExtractDescription:
    """Testes para extract_description(text: str) -> str."""

    def test_returns_string(self) -> None:
        """Retorna sempre uma string."""
        result = extract_description("# Title\n\nFirst paragraph.\n")
        assert isinstance(result, str)

    def test_skips_title_line(self) -> None:
        """Não inclui a linha de título (# ...) na descrição."""
        result = extract_description("# My Project\n\nThis is the description.\n")
        assert "# My Project" not in result
        assert "This is the description" in result

    def test_empty_text_returns_empty(self) -> None:
        """Texto vazio retorna string vazia."""
        assert extract_description("") == ""

    def test_none_returns_empty(self) -> None:
        """None retorna string vazia."""
        assert extract_description(None) == ""  # type: ignore[arg-type]

    def test_truncated_to_1000_chars(self) -> None:
        """Descrição é truncada em 1000 caracteres."""
        long_text = "# Title\n\n" + "word " * 300
        result = extract_description(long_text)
        assert len(result) <= 1000
