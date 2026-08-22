"""
Detecção de linguagem de projetos usando cascata de 3 níveis.

Nível 1: contagem de extensões de arquivo (rápido, sem dependências externas)
Nível 2: confirmação via pygments (quando confiança < threshold)
Nível 3: tree-sitter (fallback extremo, raramente ativado)
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

CONFIDENCE_THRESHOLD = 0.60

EXCLUDED_DIRS: frozenset[str] = frozenset(
    {".git", "node_modules", "__pycache__", ".venv", "tmp"}
)

EXTENSION_MAP: dict[str, str] = {
    ".py": "Python",
    ".pyx": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".mts": "TypeScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".h": "C",
    ".hpp": "C++",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".tf": "Terraform",
    ".hcl": "HCL",
    ".sql": "SQL",
    ".r": "R",
    ".scala": "Scala",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".hs": "Haskell",
    ".lua": "Lua",
    ".pl": "Perl",
    ".swift": "Swift",
    ".dart": "Dart",
}

NON_PRIMARY_EXTENSIONS: frozenset[str] = frozenset(
    {".yml", ".yaml", ".json", ".md", ".rst", ".txt", ".toml", ".ini", ".cfg",
     ".html", ".css", ".scss", ".xml", ".csv", ".svg", ".png", ".jpg", ".lock"}
)


@dataclass
class LanguageInfo:
    """Resultado da detecção de linguagem de um projeto."""

    primary: str
    secondary: list[str]
    confidence: float


def detect_language(project_path: Path) -> LanguageInfo:
    """
    Detecta a linguagem principal de um projeto usando cascata de 3 níveis.

    Cascata: extensão de arquivo → pygments → tree-sitter (fallback).
    Retorna 'Unknown' se nenhuma linguagem detectada.

    :param project_path: Caminho do diretório do projeto.
    :type project_path: Path
    :return: Informações de linguagem detectada.
    :rtype: LanguageInfo

    >>> from pathlib import Path
    >>> result = detect_language(Path("/nonexistent_xyzabc"))
    >>> result.primary
    'Unknown'
    >>> result.confidence
    0.0
    """
    if not isinstance(project_path, Path) or not project_path.exists():
        return LanguageInfo(primary="Unknown", secondary=[], confidence=0.0)
    try:
        return _detect_by_extension(project_path)
    except Exception as exc:
        logger.warning(f"Erro ao detectar linguagem em '{project_path}': {exc}")
        return LanguageInfo(primary="Unknown", secondary=[], confidence=0.0)


def _detect_by_extension(project_path: Path) -> LanguageInfo:
    """Nível 1: detecção por contagem de extensões de arquivo."""
    counts: Counter[str] = Counter()

    for file in _iter_source_files(project_path):
        suffix = file.suffix.lower()
        if suffix in EXTENSION_MAP and suffix not in NON_PRIMARY_EXTENSIONS:
            counts[EXTENSION_MAP[suffix]] += 1

    if not counts:
        for file in _iter_source_files(project_path):
            suffix = file.suffix.lower()
            if suffix in EXTENSION_MAP:
                counts[EXTENSION_MAP[suffix]] += 1

    if not counts:
        return LanguageInfo(primary="Unknown", secondary=[], confidence=0.0)

    total = sum(counts.values())
    primary = counts.most_common(1)[0][0]
    confidence = counts[primary] / total
    secondary = [lang for lang, _ in counts.most_common()[1:4]]

    if confidence < CONFIDENCE_THRESHOLD:
        return _confirm_with_pygments(project_path, primary, secondary, confidence)

    return LanguageInfo(primary=primary, secondary=secondary, confidence=round(confidence, 3))


def _iter_source_files(root: Path) -> list[Path]:
    """Itera arquivos recursivamente excluindo diretórios de build/dependências."""
    result: list[Path] = []
    try:
        for entry in root.rglob("*"):
            if not entry.is_file():
                continue
            if any(part in EXCLUDED_DIRS for part in entry.relative_to(root).parts):
                continue
            result.append(entry)
    except (PermissionError, OSError) as exc:
        logger.debug(f"Erro ao iterar arquivos em '{root}': {exc}")
    return result


def _confirm_with_pygments(
    project_path: Path,
    primary: str,
    secondary: list[str],
    confidence: float,
) -> LanguageInfo:
    """Nível 2: confirmação via pygments quando confiança < threshold."""
    try:
        from pygments.lexers import guess_lexer_for_filename
        from pygments.util import ClassNotFound

        lang_votes: Counter[str] = Counter()
        for file in _iter_source_files(project_path):
            try:
                lexer = guess_lexer_for_filename(file.name, "")
                lang_name = lexer.name
                if "Python" in lang_name:
                    lang_votes["Python"] += 1
                elif "JavaScript" in lang_name or "JSX" in lang_name:
                    lang_votes["JavaScript"] += 1
                elif "TypeScript" in lang_name or "TSX" in lang_name:
                    lang_votes["TypeScript"] += 1
                else:
                    lang_votes[lang_name] += 1
            except ClassNotFound:
                continue

        if lang_votes:
            total = sum(lang_votes.values())
            new_primary = lang_votes.most_common(1)[0][0]
            new_confidence = lang_votes[new_primary] / total
            new_secondary = [lang for lang, _ in lang_votes.most_common()[1:4]]
            return LanguageInfo(
                primary=new_primary,
                secondary=new_secondary,
                confidence=round(new_confidence, 3),
            )
    except Exception as exc:
        logger.debug(f"pygments falhou para '{project_path}': {exc}")

    return LanguageInfo(primary=primary, secondary=secondary, confidence=round(confidence, 3))
