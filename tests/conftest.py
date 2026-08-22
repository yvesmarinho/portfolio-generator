"""
Configurações e fixtures compartilhadas do pytest.

Fixtures disponíveis para todos os testes do projeto.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

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


@pytest.fixture
def no_git_project(fixtures_dir: Path) -> Path:
    """
    Retorna o caminho para fixture de projeto com README mas sem repositório git.

    :param fixtures_dir: Diretório de fixtures (injetado pelo pytest).
    :type fixtures_dir: Path
    :return: Path para tests/fixtures/no_git_project/
    :rtype: Path
    """
    path = fixtures_dir / "no_git_project"
    path.mkdir(exist_ok=True)
    readme = path / "README.md"
    if not readme.exists():
        readme.write_text(
            "# No Git Project\n\nProjeto de exemplo sem repositório git inicializado.\n"
            "\n## Descrição\n\nUsado para testar extração de metadados sem git.\n"
        )
    main_py = path / "main.py"
    if not main_py.exists():
        main_py.write_text('"""Módulo principal."""\n\n\ndef main() -> None:\n    """Entry point."""\n    print("hello")\n')
    return path


@pytest.fixture(scope="session")
def git_project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """
    Projeto com repositório git inicializado e commit inicial.

    Criado uma vez por sessão de teste em diretório temporário.
    Usa subprocess para criar um repo git real (necessário para testes do git_extractor).

    :param tmp_path_factory: Factory de paths temporários (injetado pelo pytest).
    :type tmp_path_factory: pytest.TempPathFactory
    :return: Path para o projeto com git inicializado.
    :rtype: Path
    """
    path = tmp_path_factory.mktemp("git_project")
    (path / "README.md").write_text(
        "# Git Test Project\n\nProjeto de teste com repositório git inicializado.\n"
        "\n## Descrição\n\nUsado para testes de extração de informações git.\n"
        "\nCom mais de trinta palavras para passar no threshold do analisador.\n"
    )
    (path / "main.py").write_text('"""Main module."""\n\nprint("hello")\n')
    env = {"GIT_CONFIG_NOSYSTEM": "1", "HOME": str(path), "PATH": "/usr/bin:/bin"}
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, env=env)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path, check=True, capture_output=True, env=env,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=path, check=True, capture_output=True, env=env,
    )
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True, env=env)
    subprocess.run(
        ["git", "commit", "-m", "initial commit"],
        cwd=path, check=True, capture_output=True, env=env,
    )
    return path


@pytest.fixture
def scan_target(fixtures_dir: Path) -> Generator[Path, None, None]:
    """
    Diretório temporário com mix de projetos válidos e diretórios excluídos.

    Usado para testar filtragem do DirectoryScanner.
    Criado e removido automaticamente após cada teste.

    :param fixtures_dir: Diretório de fixtures (injetado pelo pytest).
    :type fixtures_dir: Path
    :return: Gerador que fornece Path para o diretório de teste.
    :rtype: Generator[Path, None, None]
    """
    target = fixtures_dir / "_scan_target_tmp"
    target.mkdir(exist_ok=True)
    (target / "valid-project-a").mkdir(exist_ok=True)
    (target / "valid-project-a" / ".portfolio-project").write_text("{}\n")
    (target / "valid-project-b").mkdir(exist_ok=True)
    (target / "valid-project-b" / ".portfolio-project").write_text("{}\n")
    (target / ".git").mkdir(exist_ok=True)
    (target / "node_modules").mkdir(exist_ok=True)
    (target / "__pycache__").mkdir(exist_ok=True)
    (target / ".venv").mkdir(exist_ok=True)
    (target / "tmp").mkdir(exist_ok=True)
    yield target
    shutil.rmtree(target, ignore_errors=True)
