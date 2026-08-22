"""
Geração, validação e escrita do portfólio JSON.

PortfolioGenerator serializa a lista de projetos em um dicionário de portfólio,
valida contra o schema JSON e escreve o arquivo de saída.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger


class PortfolioGenerator:
    """
    Gera, valida e escreve o arquivo de portfólio JSON.

    Responsabilidades:
    - Construir a estrutura top-level do portfólio.
    - Converter paths absolutos de projetos para relativos ao scan_path.
    - Validar o portfolio dict contra o schema JSON.
    - Escrever o arquivo JSON de saída com indentação.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Inicializa o gerador com configuração fornecida.

        :param config: Dicionário com chaves: schema_path (str), generator_version (str).
        :type config: dict[str, Any]

        >>> gen = PortfolioGenerator({"schema_path": "schemas/portfolio-schema-v1.json", "generator_version": "1.0.0"})
        >>> gen is not None
        True
        """
        self._schema_path = Path(str(config.get("schema_path", "schemas/portfolio-schema-v1.json")))
        self._generator_version = str(config.get("generator_version", "1.0.0"))

    def build_portfolio(
        self,
        projects: list[dict[str, Any]],
        meta: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Constrói o dicionário de portfólio a partir da lista de projetos.

        Converte paths absolutos para relativos ao scan_path.
        Remove campos internos (prefixo _) antes de incluir no portfólio.

        :param projects: Lista de dicionários de projetos (de scan_project).
        :type projects: list[dict[str, Any]]
        :param meta: Metadados do scan: scan_path, scan_duration_seconds, skipped_projects.
        :type meta: dict[str, Any]
        :return: Dicionário de portfólio pronto para serialização.
        :rtype: dict[str, Any]

        >>> gen = PortfolioGenerator({"generator_version": "1.0.0"})
        >>> result = gen.build_portfolio([], {"scan_path": "/tmp", "scan_duration_seconds": 0.0})
        >>> result["total_projects"]
        0
        """
        scan_path = Path(str(meta.get("scan_path", "")))
        processed: list[dict[str, Any]] = []
        for project in projects:
            p = {k: v for k, v in project.items() if not k.startswith("_")}
            abs_path = Path(str(p.get("path", "")))
            try:
                p["path"] = str(abs_path.relative_to(scan_path))
            except ValueError:
                p["path"] = abs_path.name
            processed.append(p)

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "generator_version": self._generator_version,
            "scan_path": str(scan_path),
            "total_projects": len(processed),
            "skipped_projects": int(meta.get("skipped_projects") or 0),
            "scan_duration_seconds": float(meta.get("scan_duration_seconds") or 0.0),
            "projects": processed,
        }

    def validate_schema(
        self,
        portfolio: dict[str, Any],
        schema_path: Path | None = None,
    ) -> bool:
        """
        Valida o dicionário de portfólio contra o schema JSON.

        :param portfolio: Dicionário de portfólio a validar.
        :type portfolio: dict[str, Any]
        :param schema_path: Path para o arquivo de schema. Usa o configurado se None.
        :type schema_path: Path | None
        :return: True se válido, False se inválido ou erro.
        :rtype: bool

        >>> gen = PortfolioGenerator({"generator_version": "1.0.0"})
        >>> gen.validate_schema({"foo": "bar"}, None)
        False
        """
        resolved_path = schema_path if schema_path is not None else self._schema_path
        if not isinstance(portfolio, dict):
            return False
        try:
            import jsonschema

            if not resolved_path.exists():
                logger.warning(f"Schema não encontrado: {resolved_path}")
                return False
            schema = json.loads(resolved_path.read_text(encoding="utf-8"))
            jsonschema.validate(instance=portfolio, schema=schema)
            return True
        except Exception as exc:
            logger.debug(f"Validação falhou: {exc}")
            return False

    def write_output(self, portfolio: dict[str, Any], output_path: Path) -> bool:
        """
        Escreve o portfólio em um arquivo JSON com indentação de 2 espaços.

        Cria diretórios pai se necessário.
        Retorna False em caso de qualquer erro de I/O.

        :param portfolio: Dicionário de portfólio a escrever.
        :type portfolio: dict[str, Any]
        :return: True se escrito com sucesso, False caso contrário.
        :rtype: bool

        >>> from pathlib import Path
        >>> gen = PortfolioGenerator({"generator_version": "1.0.0"})
        >>> gen.write_output({}, Path("/root/no-permission/out.json"))
        False
        """
        if not isinstance(portfolio, dict) or not isinstance(output_path, Path):
            return False
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(portfolio, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info(f"Portfolio escrito em '{output_path}'")
            return True
        except Exception as exc:
            logger.error(f"Erro ao escrever portfolio em '{output_path}': {exc}")
            return False
