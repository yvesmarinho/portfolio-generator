"""
Configurações e fixtures compartilhadas do pytest.

Fixtures disponíveis para todos os testes do projeto.
"""
from __future__ import annotations

from pathlib import Path

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """
    Retorna o caminho para o diretório de fixtures de teste.

    :return: Path para tests/fixtures/
    :rtype: Path
    """
    return FIXTURES_DIR


@pytest.fixture
def python_project(fixtures_dir: Path) -> Path:
    """
    Retorna o caminho para a fixture de projeto Python com README e pyproject.toml.

    :param fixtures_dir: Diretório de fixtures (injetado pelo pytest).
    :type fixtures_dir: Path
    :return: Path para tests/fixtures/python_project/
    :rtype: Path
    """
    return fixtures_dir / "python_project"


@pytest.fixture
def empty_project(fixtures_dir: Path) -> Path:
    """
    Retorna o caminho para a fixture de diretório vazio (edge case).

    :param fixtures_dir: Diretório de fixtures (injetado pelo pytest).
    :type fixtures_dir: Path
    :return: Path para tests/fixtures/empty_project/
    :rtype: Path
    """
    path = fixtures_dir / "empty_project"
    path.mkdir(exist_ok=True)
    return path


@pytest.fixture
def no_readme_project(fixtures_dir: Path) -> Path:
    """
    Retorna o caminho para a fixture de projeto sem README.

    :param fixtures_dir: Diretório de fixtures (injetado pelo pytest).
    :type fixtures_dir: Path
    :return: Path para tests/fixtures/no_readme_project/
    :rtype: Path
    """
    path = fixtures_dir / "no_readme_project"
    path.mkdir(exist_ok=True)
    py_file = path / "script.py"
    if not py_file.exists():
        py_file.write_text('"""Script sem README."""\n\nprint("hello")\n')
    return path


@pytest.fixture
def corrupted_project(fixtures_dir: Path) -> Path:
    """
    Retorna o caminho para a fixture de projeto com arquivo corrompido.

    :param fixtures_dir: Diretório de fixtures (injetado pelo pytest).
    :type fixtures_dir: Path
    :return: Path para tests/fixtures/corrupted_project/
    :rtype: Path
    """
    return fixtures_dir / "corrupted_project"
