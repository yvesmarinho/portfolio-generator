"""
Testes unitários para analyzer.readme_parser.

TDD: escritos ANTES da implementação.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

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

    def test_skips_badge_line(self) -> None:
        """Linha de badges/shields markdown não é usada como descrição."""
        text = "[![CI](https://img.shields.io/badge/ci-passing-green)](url)\n\nReal description here.\n"
        result = extract_description(text)
        assert "shields.io" not in result
        assert "Real description here" in result

    def test_skips_multiple_badge_lines(self) -> None:
        """Várias linhas de badge seguidas são todas puladas."""
        text = (
            "[![Build](url)](url)\n"
            "![Coverage](url)\n"
            "[![License](url)](url)\n\n"
            "This project does something useful.\n"
        )
        result = extract_description(text)
        assert "This project does something useful" in result

    def test_skips_code_fence_block(self) -> None:
        """Bloco de código (```) antes do parágrafo real é ignorado."""
        text = "```\nssh-keygen -t rsa -b 4096\n```\n\nActual project description.\n"
        result = extract_description(text)
        assert "ssh-keygen" not in result
        assert "Actual project description" in result

    def test_skips_metadata_header_colon_after_bold(self) -> None:
        """Linha tipo '**Version**: 1.0.0' é tratada como metadado, não descrição."""
        text = "**Version**: 1.0.0 **Status**: In Development\n\nThe real project summary.\n"
        result = extract_description(text)
        assert "Version" not in result
        assert "The real project summary" in result

    def test_skips_metadata_header_colon_inside_bold(self) -> None:
        """Linha tipo '> **Última atualização:** 2026-05-15' é tratada como metadado."""
        text = "> **Última atualização:** 2026-05-15\n\nDescrição real do projeto.\n"
        result = extract_description(text)
        assert "atualização" not in result
        assert "Descrição real do projeto" in result

    def test_keeps_full_bold_sentence_as_description(self) -> None:
        """Parágrafo inteiramente em negrito, mas com frase longa, não é tratado como metadado."""
        text = "**Facilite a troca e gestão de projetos no VS Code por categorias.**\n"
        result = extract_description(text)
        assert "Facilite a troca e gestão de projetos" in result

    def test_fence_after_content_stops_collection(self) -> None:
        """Cerca de código aberta após o parágrafo já iniciado encerra a coleta."""
        text = "Primeiro parágrafo real aqui.\n```\ncode block\n```\n"
        result = extract_description(text)
        assert "Primeiro parágrafo real" in result
        assert "code block" not in result


class TestReadmeParserCoverage:
    """Cobertura T048: chardet fallback, exceções e break por heading (linhas 48-49, 57-68, 144)."""

    def test_chardet_fallback_reads_latin1_file(self, tmp_path: Path) -> None:
        """Arquivo com bytes Latin-1 inválidos em UTF-8 é lido via chardet (linhas 57-65)."""
        from analyzer.readme_parser import _read_file

        latin1_file = tmp_path / "README.md"
        latin1_file.write_bytes(b"# Projeto\n\nDescri\xe7\xe3o em portugu\xeas.\n")
        result = _read_file(latin1_file)
        assert result is not None
        assert isinstance(result, str)

    def test_chardet_exception_returns_none(self, tmp_path: Path) -> None:
        """Exceção no bloco chardet → _read_file retorna None (linhas 66-68)."""
        from analyzer.readme_parser import _read_file

        latin1_file = tmp_path / "README.md"
        latin1_file.write_bytes(b"Descri\xe7\xe3o.")
        with patch("chardet.detect", side_effect=RuntimeError("chardet quebrado")):
            result = _read_file(latin1_file)
        assert result is None

    def test_heading_after_content_stops_collection(self) -> None:
        """Heading # após conteúdo iniciado encerra a coleta (linha 144 — break)."""
        text = "Primeiro parágrafo completo aqui.\n# Nova Seção\nMais conteúdo."
        result = extract_description(text)
        assert "Primeiro parágrafo" in result
        assert "Nova Seção" not in result
        assert "Mais conteúdo" not in result

    def test_parse_readme_exception_returns_none(self, tmp_path: Path) -> None:
        """Exceção dentro do loop de leitura → parse_readme retorna None (linhas 48-49)."""
        (tmp_path / "README.md").write_text("# Test\n")
        with patch("analyzer.readme_parser._read_file", side_effect=RuntimeError("read failed")):
            result = parse_readme(tmp_path)
        assert result is None
