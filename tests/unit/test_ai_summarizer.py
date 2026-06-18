"""
Testes unitários para src/analyzer/ai_summarizer.py (Phase 7 — IA Integration).

Cobre:
- Geração de descrição quando README ausente
- Retorno None quando --no-ai ativo
- Retorno None quando API indisponível (exception mockada)
- Threshold duplo: word_count < 30 OU token_count > 2000 OU README ausente
- Leitura de credenciais de .secrets/api_config.json
- Falha de credenciais → None
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from analyzer.ai_summarizer import (
    _load_api_credentials,
    _should_use_ai,
    generate_summary,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def project_data_no_readme() -> dict:
    return {
        "name": "projeto-sem-readme",
        "type": "script",
        "description": "",
        "description_source": "empty",
        "_readme_word_count": 0,
        "_readme_token_count": 0,
        "_readme_text": None,
    }


@pytest.fixture()
def project_data_short_readme() -> dict:
    return {
        "name": "projeto-readme-curto",
        "type": "python",
        "description": "Hello",
        "description_source": "readme",
        "_readme_word_count": 5,
        "_readme_token_count": 2,
        "_readme_text": "Hello world short readme",
    }


@pytest.fixture()
def project_data_long_readme() -> dict:
    long_text = "word " * 2500
    return {
        "name": "projeto-readme-longo",
        "type": "python",
        "description": "início do README",
        "description_source": "readme",
        "_readme_word_count": 2500,
        "_readme_token_count": 2500,
        "_readme_text": long_text,
    }


@pytest.fixture()
def project_data_adequate_readme() -> dict:
    text = "word " * 100
    return {
        "name": "projeto-readme-ok",
        "type": "python",
        "description": "Projeto com README adequado.",
        "description_source": "readme",
        "_readme_word_count": 100,
        "_readme_token_count": 50,
        "_readme_text": text,
    }


@pytest.fixture()
def config_with_ai() -> dict:
    return {
        "no_ai": False,
        "ai_min_words": 30,
        "ai_max_tokens": 2000,
        "secrets_path": ".secrets/api_config.json",
    }


@pytest.fixture()
def config_no_ai() -> dict:
    return {
        "no_ai": True,
        "ai_min_words": 30,
        "ai_max_tokens": 2000,
        "secrets_path": ".secrets/api_config.json",
    }


# ---------------------------------------------------------------------------
# _should_use_ai
# ---------------------------------------------------------------------------

class TestShouldUseAI:
    def test_readme_ausente_retorna_true(self, config_with_ai):
        data = {"_readme_word_count": 0, "_readme_token_count": 0, "_readme_text": None}
        assert _should_use_ai(data, config_with_ai) is True

    def test_readme_curto_retorna_true(self, config_with_ai):
        data = {"_readme_word_count": 5, "_readme_token_count": 2, "_readme_text": "curto"}
        assert _should_use_ai(data, config_with_ai) is True

    def test_readme_muito_longo_retorna_true(self, config_with_ai):
        data = {"_readme_word_count": 2500, "_readme_token_count": 2500, "_readme_text": "x " * 2500}
        assert _should_use_ai(data, config_with_ai) is True

    def test_readme_adequado_retorna_false(self, config_with_ai):
        data = {"_readme_word_count": 100, "_readme_token_count": 50, "_readme_text": "word " * 100}
        assert _should_use_ai(data, config_with_ai) is False

    def test_no_ai_flag_retorna_false(self, config_no_ai):
        data = {"_readme_word_count": 0, "_readme_token_count": 0, "_readme_text": None}
        assert _should_use_ai(data, config_no_ai) is False

    def test_config_invalido_retorna_false(self):
        assert _should_use_ai({}, {}) is False
        assert _should_use_ai({}, "") is False  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# _load_api_credentials
# ---------------------------------------------------------------------------

class TestLoadApiCredentials:
    def test_carrega_credenciais_validas(self, tmp_path):
        creds = {"token": "sk-ant-test123", "model": "claude-sonnet-4-6"}
        creds_file = tmp_path / "api_config.json"
        creds_file.write_text(json.dumps(creds))
        result = _load_api_credentials(str(creds_file))
        assert result is not False
        assert isinstance(result, dict)
        assert result["token"] == "sk-ant-test123"

    def test_arquivo_inexistente_retorna_false(self, tmp_path):
        result = _load_api_credentials(str(tmp_path / "nao_existe.json"))
        assert result is False

    def test_json_invalido_retorna_false(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ invalido json }")
        result = _load_api_credentials(str(bad_file))
        assert result is False

    def test_token_ausente_retorna_false(self, tmp_path):
        creds = {"model": "claude-sonnet-4-6"}
        creds_file = tmp_path / "api_config.json"
        creds_file.write_text(json.dumps(creds))
        result = _load_api_credentials(str(creds_file))
        assert result is False

    def test_parametro_invalido_retorna_false(self):
        assert _load_api_credentials("") is False
        assert _load_api_credentials(None) is False  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# generate_summary — lógica principal
# ---------------------------------------------------------------------------

class TestGenerateSummary:
    def test_no_ai_flag_retorna_none(self, project_data_no_readme, config_no_ai):
        result = generate_summary(project_data_no_readme, config_no_ai)
        assert result is None

    def test_readme_adequado_retorna_none_sem_chamar_api(
        self, project_data_adequate_readme, config_with_ai
    ):
        with patch("analyzer.ai_summarizer.anthropic") as mock_anthropic:
            result = generate_summary(project_data_adequate_readme, config_with_ai)
            assert result is None
            mock_anthropic.Anthropic.assert_not_called()

    def test_gera_descricao_quando_readme_ausente(
        self, project_data_no_readme, config_with_ai, tmp_path
    ):
        creds_file = tmp_path / "api_config.json"
        creds_file.write_text(json.dumps({"token": "sk-ant-fake", "model": "claude-haiku-4-5-20251001"}))
        config = {**config_with_ai, "secrets_path": str(creds_file)}

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Descrição gerada pela IA.")]
        mock_client.messages.create.return_value = mock_message

        with patch("analyzer.ai_summarizer.anthropic") as mock_anthropic:
            mock_anthropic.Anthropic.return_value = mock_client
            result = generate_summary(project_data_no_readme, config)

        assert result == "Descrição gerada pela IA."
        mock_client.messages.create.assert_called_once()

    def test_gera_descricao_quando_readme_curto(
        self, project_data_short_readme, config_with_ai, tmp_path
    ):
        creds_file = tmp_path / "api_config.json"
        creds_file.write_text(json.dumps({"token": "sk-ant-fake", "model": "claude-haiku-4-5-20251001"}))
        config = {**config_with_ai, "secrets_path": str(creds_file)}

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Resumo curto.")]
        mock_client.messages.create.return_value = mock_message

        with patch("analyzer.ai_summarizer.anthropic") as mock_anthropic:
            mock_anthropic.Anthropic.return_value = mock_client
            result = generate_summary(project_data_short_readme, config)

        assert result == "Resumo curto."

    def test_api_exception_retorna_none(
        self, project_data_no_readme, config_with_ai, tmp_path
    ):
        creds_file = tmp_path / "api_config.json"
        creds_file.write_text(json.dumps({"token": "sk-ant-fake", "model": "claude-haiku-4-5-20251001"}))
        config = {**config_with_ai, "secrets_path": str(creds_file)}

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API indisponível")

        with patch("analyzer.ai_summarizer.anthropic") as mock_anthropic:
            mock_anthropic.Anthropic.return_value = mock_client
            result = generate_summary(project_data_no_readme, config)

        assert result is None

    def test_credenciais_invalidas_retorna_none(
        self, project_data_no_readme, config_with_ai
    ):
        config = {**config_with_ai, "secrets_path": "/nao/existe/api_config.json"}
        result = generate_summary(project_data_no_readme, config)
        assert result is None

    def test_project_data_invalido_retorna_none(self, config_with_ai):
        assert generate_summary({}, config_with_ai) is None
        assert generate_summary(None, config_with_ai) is None  # type: ignore[arg-type]

    def test_config_invalido_retorna_none(self, project_data_no_readme):
        assert generate_summary(project_data_no_readme, {}) is None
        assert generate_summary(project_data_no_readme, None) is None  # type: ignore[arg-type]

    def test_resposta_vazia_da_api_retorna_none(
        self, project_data_no_readme, config_with_ai, tmp_path
    ):
        creds_file = tmp_path / "api_config.json"
        creds_file.write_text(json.dumps({"token": "sk-ant-fake", "model": "claude-haiku-4-5-20251001"}))
        config = {**config_with_ai, "secrets_path": str(creds_file)}

        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = []
        mock_client.messages.create.return_value = mock_message

        with patch("analyzer.ai_summarizer.anthropic") as mock_anthropic:
            mock_anthropic.Anthropic.return_value = mock_client
            result = generate_summary(project_data_no_readme, config)

        assert result is None
