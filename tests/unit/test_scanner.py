"""
Testes unitários para scanner.directory_scanner.

TDD: estes testes foram escritos ANTES da implementação e devem falhar inicialmente.
Executar ANTES de criar directory_scanner.py para confirmar falha por ImportError.
"""
from __future__ import annotations

from pathlib import Path

from scanner.directory_scanner import DirectoryScanner, validate_path_scope

ALLOWED_SCOPE = Path("/home/yves_marinho/Documentos/DevOps/")


class TestValidatePathScope:
    """Testes para a função standalone validate_path_scope."""

    def test_scope_root_itself_returns_true(self) -> None:
        """O próprio diretório raiz do escopo é permitido."""
        assert validate_path_scope(ALLOWED_SCOPE) is True

    def test_direct_subdir_returns_true(self) -> None:
        """Subdiretório direto do escopo é permitido."""
        assert validate_path_scope(ALLOWED_SCOPE / "meu-projeto") is True

    def test_nested_subdir_returns_true(self) -> None:
        """Subdiretório aninhado dentro do escopo é permitido."""
        assert validate_path_scope(ALLOWED_SCOPE / "Projetos" / "meu-app") is True

    def test_portfolio_generator_path_returns_true(self) -> None:
        """O próprio projeto está dentro do escopo (DevOps/Projetos/...)."""
        assert validate_path_scope(ALLOWED_SCOPE / "Projetos" / "portfolio-generator") is True

    def test_parent_of_scope_returns_false(self) -> None:
        """Diretório pai do escopo não é permitido."""
        assert validate_path_scope(Path("/home/yves_marinho/Documentos/")) is False

    def test_home_dir_returns_false(self) -> None:
        """Diretório home não é permitido."""
        assert validate_path_scope(Path("/home/yves_marinho/")) is False

    def test_system_path_returns_false(self) -> None:
        """Paths fora do home são rejeitados."""
        assert validate_path_scope(Path("/etc/passwd")) is False

    def test_root_path_returns_false(self) -> None:
        """O path raiz / não é permitido."""
        assert validate_path_scope(Path("/")) is False

    def test_empty_path_returns_false(self) -> None:
        """Path vazio retorna False (sem resolver para cwd)."""
        assert validate_path_scope(Path("")) is False

    def test_path_traversal_stays_in_scope_returns_true(self) -> None:
        """Path traversal que permanece dentro do escopo é permitido após resolve()."""
        traversal_valid = ALLOWED_SCOPE / "projeto" / ".." / "outro-projeto"
        assert validate_path_scope(traversal_valid) is True

    def test_path_traversal_leaves_scope_returns_false(self) -> None:
        """Path traversal que sai do escopo é rejeitado após resolve()."""
        traversal_out = ALLOWED_SCOPE / ".." / ".." / "etc"
        assert validate_path_scope(traversal_out) is False

    def test_similar_name_outside_scope_returns_false(self) -> None:
        """Diretório com nome similar (DevOpsExtra) não corresponde ao escopo."""
        assert validate_path_scope(Path("/home/yves_marinho/Documentos/DevOpsExtra/")) is False


class TestDirectoryScanner:
    """Testes para a classe DirectoryScanner."""

    def test_init_with_valid_config(self) -> None:
        """Construtor aceita configuração válida."""
        config: dict[str, object] = {
            "root_path": str(ALLOWED_SCOPE),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        assert scanner is not None

    def test_list_projects_returns_list(self, fixtures_dir: Path) -> None:
        """list_projects retorna uma lista."""
        config: dict[str, object] = {
            "root_path": str(fixtures_dir),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(fixtures_dir)
        assert isinstance(result, list)

    def test_list_projects_finds_python_project(self, fixtures_dir: Path) -> None:
        """list_projects detecta o python_project na fixtures_dir."""
        config: dict[str, object] = {
            "root_path": str(fixtures_dir),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(fixtures_dir)
        names = [p.name for p in result]
        assert "python_project" in names

    def test_list_projects_returns_path_objects(self, fixtures_dir: Path) -> None:
        """Todos os itens retornados são objetos Path."""
        config: dict[str, object] = {
            "root_path": str(fixtures_dir),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(fixtures_dir)
        for item in result:
            assert isinstance(item, Path)

    def test_list_projects_excludes_git(self, scan_target: Path) -> None:
        """list_projects exclui diretórios .git."""
        config: dict[str, object] = {
            "root_path": str(scan_target),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(scan_target)
        names = [p.name for p in result]
        assert ".git" not in names

    def test_list_projects_excludes_node_modules(self, scan_target: Path) -> None:
        """list_projects exclui node_modules."""
        config: dict[str, object] = {
            "root_path": str(scan_target),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(scan_target)
        names = [p.name for p in result]
        assert "node_modules" not in names

    def test_list_projects_excludes_pycache(self, scan_target: Path) -> None:
        """list_projects exclui __pycache__."""
        config: dict[str, object] = {
            "root_path": str(scan_target),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(scan_target)
        names = [p.name for p in result]
        assert "__pycache__" not in names

    def test_list_projects_excludes_venv(self, scan_target: Path) -> None:
        """list_projects exclui .venv."""
        config: dict[str, object] = {
            "root_path": str(scan_target),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(scan_target)
        names = [p.name for p in result]
        assert ".venv" not in names

    def test_list_projects_excludes_tmp(self, scan_target: Path) -> None:
        """list_projects exclui tmp."""
        config: dict[str, object] = {
            "root_path": str(scan_target),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(scan_target)
        names = [p.name for p in result]
        assert "tmp" not in names

    def test_list_projects_keeps_valid_dirs(self, scan_target: Path) -> None:
        """list_projects mantém diretórios válidos (valid-project-a, valid-project-b)."""
        config: dict[str, object] = {
            "root_path": str(scan_target),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(scan_target)
        names = [p.name for p in result]
        assert "valid-project-a" in names
        assert "valid-project-b" in names

    def test_list_projects_rejects_out_of_scope(self) -> None:
        """list_projects retorna [] quando path está fora do escopo permitido."""
        config: dict[str, object] = {
            "root_path": "/etc",
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(Path("/etc"))
        assert result == []

    def test_list_projects_returns_empty_for_nonexistent_dir(self, fixtures_dir: Path) -> None:
        """list_projects retorna [] para diretório inexistente."""
        config: dict[str, object] = {
            "root_path": str(fixtures_dir),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(fixtures_dir / "diretorio_inexistente_xyzabc")
        assert result == []

    def test_list_projects_result_is_sorted(self, scan_target: Path) -> None:
        """list_projects retorna projetos em ordem alfabética."""
        config: dict[str, object] = {
            "root_path": str(scan_target),
            "excluded_dirs": [],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(scan_target)
        names = [p.name for p in result]
        assert names == sorted(names)

    def test_list_projects_custom_excluded_dirs(self, fixtures_dir: Path) -> None:
        """list_projects respeita excluded_dirs customizados da config."""
        config: dict[str, object] = {
            "root_path": str(fixtures_dir),
            "excluded_dirs": ["corrupted_project"],
            "max_depth": 1,
        }
        scanner = DirectoryScanner(config)
        result = scanner.list_projects(fixtures_dir)
        names = [p.name for p in result]
        assert "corrupted_project" not in names
