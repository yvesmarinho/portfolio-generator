"""
Gerador de descrições de projetos via Anthropic API.

Acionado quando README está ausente, muito curto (< ai_min_words palavras)
ou muito extenso (> ai_max_tokens tokens). Lê credenciais exclusivamente
de .secrets/api_config.json — nunca hardcoded.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import anthropic
from loguru import logger

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_SECRETS_PATH = ".secrets/api_config.json"
MAX_SUMMARY_TOKENS = 150

_SUMMARY_PROMPT = """\
Você é um assistente que escreve descrições técnicas concisas de projetos de software.

Projeto: {name}
Tipo: {project_type}
Tecnologias: {technologies}
Arquivos no projeto: {file_count}
Linguagem principal: {primary_language}

{readme_section}

Escreva uma descrição técnica em português de 1 a 3 frases que explique o propósito deste projeto.\
 Seja direto e objetivo. Não use frases introdutórias como "Este projeto" ou "Este é um projeto".\
 Responda APENAS com a descrição, sem explicações adicionais."""


def _load_api_credentials(secrets_path: str | None) -> dict[str, Any] | bool:
    """
    Carrega credenciais da API Anthropic do arquivo JSON em .secrets/.

    :param secrets_path: Caminho do arquivo JSON de credenciais.
    :type secrets_path: str | None
    :return: Dicionário com credenciais (obrigatório: 'token'), ou False em caso de erro.
    :rtype: dict[str, Any] | bool

    >>> _load_api_credentials("")
    False
    >>> _load_api_credentials(None)
    False
    >>> _load_api_credentials("/nao/existe/api_config.json")
    False
    """
    if not secrets_path or not isinstance(secrets_path, str):
        return False
    try:
        path = Path(secrets_path)
        if not path.exists():
            logger.debug(f"Arquivo de credenciais não encontrado: {secrets_path}")
            return False
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data.get("token"):
            logger.debug(f"Credenciais inválidas em {secrets_path}: 'token' ausente")
            return False
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.debug(f"Erro ao carregar credenciais de '{secrets_path}': {exc}")
        return False


def _should_use_ai(project_data: dict[str, Any], config: dict[str, Any]) -> bool:
    """
    Determina se a IA deve ser usada para gerar descrição deste projeto.

    Condições para usar IA (qualquer uma):
    - README ausente (word_count == 0)
    - README muito curto (word_count < ai_min_words)
    - README muito extenso (token_count > ai_max_tokens)

    Retorna False se --no-ai está ativo ou se parâmetros são inválidos.

    :param project_data: Dicionário de dados do projeto.
    :type project_data: dict[str, Any]
    :param config: Configuração com no_ai, ai_min_words, ai_max_tokens.
    :type config: dict[str, Any]
    :return: True se IA deve ser chamada.
    :rtype: bool

    >>> _should_use_ai({}, {})
    False
    >>> _should_use_ai({}, "")
    False
    """
    if not project_data or not isinstance(project_data, dict):
        return False
    if not config or not isinstance(config, dict):
        return False
    if config.get("no_ai"):
        return False
    try:
        word_count = int(project_data.get("_readme_word_count") or 0)
        token_count = int(project_data.get("_readme_token_count") or 0)
        ai_min_words = int(config.get("ai_min_words") or 30)
        ai_max_tokens = int(config.get("ai_max_tokens") or 2000)

        readme_absent = word_count == 0
        readme_too_short = word_count < ai_min_words
        readme_too_long = token_count > ai_max_tokens

        return readme_absent or readme_too_short or readme_too_long
    except (TypeError, ValueError):
        return False


def _build_prompt(project_data: dict[str, Any]) -> str:
    """Constrói o prompt para a API a partir dos dados do projeto."""
    name = str(project_data.get("name") or "desconhecido")
    project_type = str(project_data.get("type") or "unknown")
    technologies = ", ".join(project_data.get("technologies") or []) or "não detectadas"
    language_info = project_data.get("language") or {}
    primary_language = str(language_info.get("primary") or "desconhecida") if isinstance(language_info, dict) else "desconhecida"
    metrics = project_data.get("metrics") or {}
    file_count = str(metrics.get("file_count") or "?") if isinstance(metrics, dict) else "?"

    readme_text = project_data.get("_readme_text")
    if readme_text:
        readme_preview = str(readme_text)[:500]
        readme_section = f"Conteúdo parcial do README:\n{readme_preview}"
    else:
        readme_section = "README: ausente"

    return _SUMMARY_PROMPT.format(
        name=name,
        project_type=project_type,
        technologies=technologies,
        file_count=file_count,
        primary_language=primary_language,
        readme_section=readme_section,
    )


def generate_summary(project_data: dict[str, Any] | None, config: dict[str, Any] | None) -> str | None:
    """
    Gera uma descrição técnica de um projeto via Anthropic API.

    Retorna None (sem lançar exceção) em todos os casos de erro:
    - --no-ai ativo
    - README adequado (não precisa de IA)
    - Credenciais ausentes ou inválidas
    - Falha na API
    - Resposta vazia

    :param project_data: Dicionário de dados do projeto (campos _readme_*).
    :type project_data: dict[str, Any] | None
    :param config: Configuração com no_ai, ai_min_words, ai_max_tokens, secrets_path.
    :type config: dict[str, Any] | None
    :return: Descrição gerada pela IA, ou None.
    :rtype: str | None

    >>> generate_summary(None, None) is None
    True
    >>> generate_summary({}, {}) is None
    True
    >>> generate_summary({"_readme_word_count": 0}, {"no_ai": True}) is None
    True
    """
    if not project_data or not isinstance(project_data, dict):
        return None
    if not config or not isinstance(config, dict):
        return None
    if not _should_use_ai(project_data, config):
        return None
    try:
        secrets_path = str(config.get("secrets_path") or DEFAULT_SECRETS_PATH)
        creds = _load_api_credentials(secrets_path)
        if not creds or not isinstance(creds, dict):
            logger.warning(
                f"IA indisponível para '{project_data.get('name')}': credenciais ausentes em {secrets_path}"
            )
            return None

        api_key = str(creds["token"])
        model = str(creds.get("model") or DEFAULT_MODEL)
        prompt = _build_prompt(project_data)

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=MAX_SUMMARY_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

        content_blocks = response.content
        if not content_blocks:
            logger.debug(f"Resposta vazia da API para '{project_data.get('name')}'")
            return None

        first_block = content_blocks[0]
        if not hasattr(first_block, "text"):
            logger.debug(f"Bloco de resposta sem atributo 'text' para '{project_data.get('name')}'")
            return None

        summary = str(first_block.text).strip()
        if not summary:
            return None

        logger.info(f"Descrição gerada via IA para '{project_data.get('name')}'")
        return summary

    except Exception as exc:
        logger.warning(f"Falha na geração de descrição via IA para '{project_data.get('name')}': {exc}")
        return None
