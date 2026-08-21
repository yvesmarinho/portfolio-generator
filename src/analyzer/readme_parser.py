"""
Parser de arquivos README para extração de descrições de projetos.

Suporta README.md, README.rst, README.txt (case-insensitive).
Funções utilitárias word_count e token_count também exportadas aqui.
"""
from __future__ import annotations

import re
from pathlib import Path

from loguru import logger

# Linha de badge/shield markdown (ex.: [![CI](url)](url) ou ![alt](url))
_BADGE_RE = re.compile(r"^(\[!\[|!\[)")
# Linha de metadados tipo "**Version**: 1.0.0" ou "> **Última atualização:** ..."
_METADATA_RE = re.compile(r"^>?\s*(\*\*[^*]{1,30}:\*\*|\*\*[^*:]{1,30}\*\*\s*:)")
# Cerca de bloco de código markdown (```)
_FENCE_RE = re.compile(r"^```")

README_NAMES: tuple[str, ...] = (
    "README.md",
    "README.rst",
    "README.txt",
    "README",
    "readme.md",
    "readme.rst",
    "readme.txt",
)


def parse_readme(project_path: Path) -> str | None:
    """
    Lê o arquivo README de um diretório de projeto.

    Tenta extensões em ordem: .md, .rst, .txt, sem extensão.
    Usa chardet para detecção de encoding quando UTF-8 falha.
    Retorna None se nenhum README for encontrado.

    :param project_path: Caminho do diretório do projeto.
    :type project_path: Path
    :return: Conteúdo do README como string, ou None.
    :rtype: str | None

    >>> from pathlib import Path
    >>> parse_readme(Path("/nonexistent_xyzabc")) is None
    True
    """
    if not isinstance(project_path, Path) or not project_path.exists():
        return None
    try:
        for name in README_NAMES:
            candidate = project_path / name
            if candidate.is_file():
                return _read_file(candidate)
    except Exception as exc:
        logger.warning(f"Erro ao buscar README em '{project_path}': {exc}")
    return None


def _read_file(path: Path) -> str | None:
    """Lê arquivo com fallback para detecção de encoding via chardet."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        pass
    try:
        import chardet

        raw = path.read_bytes()
        detected = chardet.detect(raw)
        encoding = str(detected.get("encoding") or "utf-8")
        return raw.decode(encoding, errors="replace")
    except Exception as exc:
        logger.debug(f"Falha ao ler '{path}': {exc}")
        return None


def word_count(text: str) -> int:
    """
    Conta palavras em um texto (separadas por whitespace).

    :param text: Texto a ser contado.
    :type text: str
    :return: Número de palavras.
    :rtype: int

    >>> word_count("hello world")
    2
    >>> word_count("")
    0
    >>> word_count("hello   world")
    2
    """
    if not text or not isinstance(text, str):
        return 0
    return len(text.split())


def token_count(text: str) -> int:
    """
    Estima o número de tokens em um texto (len(text) // 4).

    Aproximação grosseira baseada em modelos de linguagem:
    ~4 caracteres por token em média para texto em inglês.

    :param text: Texto a ser estimado.
    :type text: str
    :return: Estimativa de tokens.
    :rtype: int

    >>> token_count("abcd")
    1
    >>> token_count("")
    0
    >>> token_count("a" * 100)
    25
    """
    if not text or not isinstance(text, str):
        return 0
    return len(text) // 4


def extract_description(readme_text: str | None) -> str:
    """
    Extrai o primeiro parágrafo significativo de um texto README.

    Pula linhas de título (# ...), badges/shields markdown, blocos de
    código (```) e cabeçalhos de metadados (ex.: "**Version**: 1.0.0")
    até encontrar o primeiro parágrafo real. Limita a 1000 caracteres.

    :param readme_text: Conteúdo bruto do README.
    :type readme_text: str | None
    :return: Primeiro parágrafo ou string vazia.
    :rtype: str

    >>> extract_description("# Title\\n\\nFirst paragraph.\\n")
    'First paragraph.'
    >>> extract_description("[![CI](url)](url)\\n\\nReal description.\\n")
    'Real description.'
    >>> extract_description("")
    ''
    >>> extract_description(None)
    ''
    """
    if not readme_text or not isinstance(readme_text, str):
        return ""
    lines = readme_text.splitlines()
    collecting = False
    in_fence = False
    result_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if _FENCE_RE.match(stripped):
            if collecting:
                break
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("#"):
            if collecting:
                break
            continue
        if _BADGE_RE.match(stripped) or _METADATA_RE.match(stripped):
            if collecting:
                break
            continue
        if not stripped and not collecting:
            continue
        if not stripped and collecting:
            break
        result_lines.append(stripped)
        collecting = True
    return " ".join(result_lines)[:1000]
