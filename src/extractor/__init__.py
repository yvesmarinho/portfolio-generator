"""
Módulo extractor — extração de metadados de projetos individuais.

Responsabilidade única: coordenar a extração de linguagem, git info e métricas
de um projeto, retornando um dicionário de metadados estruturado.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from extractor.metadata_extractor import MetadataExtractor


def create_extractor(config: dict[str, Any]) -> MetadataExtractor | bool:
    """
    Factory para instanciar o MetadataExtractor com configuração fornecida.

    :param config: Dicionário de configuração com chaves: ai_min_words, ai_max_tokens, no_ai.
    :type config: dict[str, Any]
    :return: Instância configurada de MetadataExtractor, ou False em caso de erro.
    :rtype: MetadataExtractor | bool

    >>> config = {"ai_min_words": 30, "ai_max_tokens": 2000, "no_ai": True}
    >>> result = create_extractor(config)
    >>> result is not None
    True
    >>> create_extractor({})
    False
    >>> create_extractor("")  # type: ignore[arg-type]
    False
    """
    if not config or not isinstance(config, dict):
        return False
    try:
        from extractor.metadata_extractor import MetadataExtractor

        return MetadataExtractor(config)
    except Exception as e:
        print(f"Erro ao criar extractor: {e}")
        return False
