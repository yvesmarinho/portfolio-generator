"""
Módulo generator — geração e validação do portfólio JSON.

Responsabilidade única: serializar a lista de entradas de projetos em um
dicionário de portfólio, validar contra o schema e escrever o arquivo de saída.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from generator.portfolio_generator import PortfolioGenerator


def create_generator(config: dict[str, Any]) -> PortfolioGenerator | bool:
    """
    Factory para instanciar o PortfolioGenerator com configuração fornecida.

    :param config: Dicionário de configuração com chaves: schema_path, output_path,
                   generator_version.
    :type config: dict[str, Any]
    :return: Instância configurada de PortfolioGenerator, ou False em caso de erro.
    :rtype: PortfolioGenerator | bool

    >>> config = {"schema_path": "schemas/portfolio-schema-v1.json", "generator_version": "1.0.0"}
    >>> result = create_generator(config)
    >>> result is not None
    True
    >>> create_generator({})
    False
    >>> create_generator("")  # type: ignore[arg-type]
    False
    """
    if not config or not isinstance(config, dict):
        return False
    try:
        from generator.portfolio_generator import PortfolioGenerator

        return PortfolioGenerator(config)
    except Exception as e:
        print(f"Erro ao criar generator: {e}")
        return False
