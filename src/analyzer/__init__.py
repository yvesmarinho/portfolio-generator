"""
Módulo analyzer — análise de README e geração de descrições de projetos.

Responsabilidade única: extrair descrições de arquivos README e acionar a
geração via IA quando o README é ausente, muito curto ou muito extenso.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from analyzer.project_analyzer import ProjectAnalyzer


def create_analyzer(config: dict[str, Any]) -> ProjectAnalyzer | bool:
    """
    Factory para instanciar o ProjectAnalyzer com configuração fornecida.

    :param config: Dicionário de configuração com chaves: ai_min_words, ai_max_tokens,
                   no_ai, secrets_path.
    :type config: dict[str, Any]
    :return: Instância configurada de ProjectAnalyzer, ou False em caso de erro.
    :rtype: ProjectAnalyzer | bool

    >>> config = {"ai_min_words": 30, "ai_max_tokens": 2000, "no_ai": True}
    >>> result = create_analyzer(config)
    >>> result is not None
    True
    >>> create_analyzer({})
    False
    >>> create_analyzer("")  # type: ignore[arg-type]
    False
    """
    if not config or not isinstance(config, dict):
        return False
    try:
        from analyzer.project_analyzer import ProjectAnalyzer

        return ProjectAnalyzer(config)
    except Exception as e:
        print(f"Erro ao criar analyzer: {e}")
        return False
