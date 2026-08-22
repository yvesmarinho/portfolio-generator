.PHONY: help setup test test-unit test-integration lint format run dry-run security clean

## Mostra esta ajuda
help:
	@grep -E '^##' Makefile | sed 's/## //'

## Instala dependências e configura pre-commit
setup:
	uv sync --all-groups
	uv run pre-commit install
	@echo "✓ Ambiente configurado. Use 'make run' para executar."

## Executa suite de testes com cobertura
test:
	uv run pytest --cov=src --cov-report=term-missing --cov-report=html -v

## Executa apenas testes unitários (mais rápido)
test-unit:
	uv run pytest tests/unit/ -v

## Executa apenas testes de integração
test-integration:
	uv run pytest tests/integration/ -v

## Lint: ruff + mypy + bandit
lint:
	uv run ruff check src/ tests/
	uv run mypy src/ --strict
	uv run bandit -r src/ -q

## Formata código com black e ruff
format:
	uv run black src/ tests/
	uv run ruff check src/ tests/ --fix

## Executa portfolio-gen scan com configurações default
run:
	uv run portfolio-gen scan --verbose

## Executa scan em dry-run (sem criar arquivos)
dry-run:
	uv run portfolio-gen scan --dry-run --verbose

## Scan de segurança: bandit + safety
security:
	uv run bandit -r src/
	uv run safety check

## Remove arquivos gerados
clean:
	rm -rf output/*.json logs/*.log
	rm -rf dist/ build/ __pycache__/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ .coverage
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
