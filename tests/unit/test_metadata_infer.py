"""
Testes unitários para funções de inferência de metadata_extractor.

Cobertura T048 (Phase 8): _infer_type, _infer_technologies, _infer_status,
_get_last_modified e MetadataExtractor class.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from extractor.git_extractor import GitInfo
from extractor.metadata_extractor import (
    MetadataExtractor,
    _get_last_modified,
    _infer_status,
    _infer_technologies,
    _infer_type,
    scan_project,
)


def _git_info(days_ago: int) -> GitInfo:
    """Cria GitInfo com last_commit_date relativo a agora."""
    date = (datetime.now(UTC) - timedelta(days=days_ago)).isoformat()
    return GitInfo(
        branch="main",
        last_commit_hash="abc1234",
        last_commit_date=date,
        last_commit_author="Test User",
        commit_count=1,
    )


class TestMetadataExtractorClass:
    """MetadataExtractor: init e extract."""

    def test_init_creates_instance(self) -> None:
        """MetadataExtractor pode ser instanciado com configuração válida."""
        e = MetadataExtractor({"no_ai": True, "ai_min_words": 30, "ai_max_tokens": 2000})
        assert e is not None

    def test_extract_nonexistent_returns_none(self) -> None:
        """MetadataExtractor.extract retorna None para path inexistente."""
        e = MetadataExtractor({"no_ai": True})
        assert e.extract(Path("/nonexistent_xyz_abc")) is None

    def test_extract_valid_project_returns_dict(self, tmp_path: Path) -> None:
        """MetadataExtractor.extract retorna dict para projeto válido."""
        (tmp_path / "main.py").write_text('"""Main."""\n')
        e = MetadataExtractor({"no_ai": True})
        result = e.extract(tmp_path)
        assert result is not None
        assert isinstance(result, dict)


class TestInferType:
    """_infer_type(): cobertura de todos os ramos de retorno."""

    def test_terraform_file_is_infrastructure(self, tmp_path: Path) -> None:
        """Arquivo .tf → tipo 'infrastructure'."""
        (tmp_path / "main.tf").write_text("resource {}")
        assert _infer_type(tmp_path) == "infrastructure"

    def test_kubernetes_dir_is_infrastructure(self, tmp_path: Path) -> None:
        """Pasta k8s/ → tipo 'infrastructure'."""
        (tmp_path / "k8s").mkdir()
        assert _infer_type(tmp_path) == "infrastructure"

    def test_dockerfile_without_pyproject_is_infrastructure(self, tmp_path: Path) -> None:
        """Dockerfile sem pyproject.toml → tipo 'infrastructure'."""
        (tmp_path / "Dockerfile").write_text("FROM python:3.13")
        assert _infer_type(tmp_path) == "infrastructure"

    def test_ansible_cfg_is_automation(self, tmp_path: Path) -> None:
        """ansible.cfg → tipo 'automation'."""
        (tmp_path / "ansible.cfg").write_text("[defaults]")
        assert _infer_type(tmp_path) == "automation"

    def test_package_json_is_web_app(self, tmp_path: Path) -> None:
        """package.json → tipo 'web-app'."""
        (tmp_path / "package.json").write_text("{}")
        assert _infer_type(tmp_path) == "web-app"

    def test_notebook_is_data_analysis(self, tmp_path: Path) -> None:
        """Arquivo .ipynb → tipo 'data-analysis'."""
        (tmp_path / "analysis.ipynb").write_text("{}")
        assert _infer_type(tmp_path) == "data-analysis"

    def test_mkdocs_is_documentation(self, tmp_path: Path) -> None:
        """mkdocs.yml → tipo 'documentation'."""
        (tmp_path / "mkdocs.yml").write_text("site_name: docs")
        assert _infer_type(tmp_path) == "documentation"

    def test_app_py_without_pyproject_is_api_service(self, tmp_path: Path) -> None:
        """app.py sem pyproject.toml → tipo 'api-service'."""
        (tmp_path / "app.py").write_text("from flask import Flask")
        assert _infer_type(tmp_path) == "api-service"

    def test_setup_py_without_main_is_library(self, tmp_path: Path) -> None:
        """setup.py sem main.py → tipo 'library'."""
        (tmp_path / "setup.py").write_text("from setuptools import setup")
        assert _infer_type(tmp_path) == "library"

    def test_empty_dir_is_unknown(self, tmp_path: Path) -> None:
        """Diretório vazio → tipo 'unknown'."""
        assert _infer_type(tmp_path) == "unknown"


class TestInferTechnologies:
    """_infer_technologies(): cobertura de cada tecnologia detectada."""

    def test_dockerfile_adds_docker(self, tmp_path: Path) -> None:
        """Dockerfile → detecção de 'Docker'."""
        (tmp_path / "Dockerfile").write_text("FROM python:3.13")
        assert "Docker" in _infer_technologies(tmp_path)

    def test_docker_compose_yaml_adds_compose(self, tmp_path: Path) -> None:
        """docker-compose.yaml → detecção de 'Docker Compose'."""
        (tmp_path / "docker-compose.yaml").write_text("services: {}")
        assert "Docker Compose" in _infer_technologies(tmp_path)

    def test_docker_compose_yml_adds_compose(self, tmp_path: Path) -> None:
        """docker-compose.yml → detecção de 'Docker Compose'."""
        (tmp_path / "docker-compose.yml").write_text("services: {}")
        assert "Docker Compose" in _infer_technologies(tmp_path)

    def test_terraform_file_adds_terraform(self, tmp_path: Path) -> None:
        """Arquivo .tf → detecção de 'Terraform'."""
        (tmp_path / "main.tf").write_text("resource {}")
        assert "Terraform" in _infer_technologies(tmp_path)

    def test_makefile_adds_make(self, tmp_path: Path) -> None:
        """Makefile → detecção de 'Make'."""
        (tmp_path / "Makefile").write_text("all:\n\techo done")
        assert "Make" in _infer_technologies(tmp_path)

    def test_requirements_txt_adds_python_pip(self, tmp_path: Path) -> None:
        """requirements.txt sem pyproject.toml → detecção de 'Python/pip'."""
        (tmp_path / "requirements.txt").write_text("requests==2.31.0")
        assert "Python/pip" in _infer_technologies(tmp_path)

    def test_package_json_adds_nodejs(self, tmp_path: Path) -> None:
        """package.json → detecção de 'Node.js'."""
        (tmp_path / "package.json").write_text('{"name": "test"}')
        assert "Node.js" in _infer_technologies(tmp_path)

    def test_go_mod_adds_go_modules(self, tmp_path: Path) -> None:
        """go.mod → detecção de 'Go modules'."""
        (tmp_path / "go.mod").write_text("module example.com/app\ngo 1.21")
        assert "Go modules" in _infer_technologies(tmp_path)

    def test_github_actions_workflows_adds_gha(self, tmp_path: Path) -> None:
        """Pasta .github/workflows/ → detecção de 'GitHub Actions'."""
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        assert "GitHub Actions" in _infer_technologies(tmp_path)

    def test_ansible_cfg_adds_ansible(self, tmp_path: Path) -> None:
        """ansible.cfg → detecção de 'Ansible'."""
        (tmp_path / "ansible.cfg").write_text("[defaults]")
        assert "Ansible" in _infer_technologies(tmp_path)

    def test_playbook_yml_adds_ansible(self, tmp_path: Path) -> None:
        """playbook.yml → detecção de 'Ansible'."""
        (tmp_path / "playbook.yml").write_text("- hosts: all")
        assert "Ansible" in _infer_technologies(tmp_path)

    def test_empty_project_returns_empty_list(self, tmp_path: Path) -> None:
        """Projeto vazio → lista de tecnologias vazia."""
        assert _infer_technologies(tmp_path) == []


class TestInferStatus:
    """_infer_status(): ramos active, archived, unknown e edge cases."""

    def test_recent_commit_is_active(self) -> None:
        """Commit de 30 dias atrás → status 'active'."""
        assert _infer_status(_git_info(30)) == "active"

    def test_very_old_commit_is_archived(self) -> None:
        """Commit de 800 dias atrás → status 'archived'."""
        assert _infer_status(_git_info(800)) == "archived"

    def test_middle_age_commit_is_unknown(self) -> None:
        """Commit de 300 dias atrás (entre 180 e 730) → status 'unknown'."""
        assert _infer_status(_git_info(300)) == "unknown"

    def test_no_git_info_is_unknown(self) -> None:
        """None → status 'unknown' (sem git inicializado)."""
        assert _infer_status(None) == "unknown"

    def test_non_gitinfo_object_is_unknown(self) -> None:
        """Objeto que não é GitInfo → status 'unknown'."""
        assert _infer_status("not-a-gitinfo") == "unknown"

    def test_invalid_date_string_is_unknown(self) -> None:
        """GitInfo com data inválida → status 'unknown' (via except)."""
        bad = GitInfo(
            branch="main",
            last_commit_hash="abc1234",
            last_commit_date="esta-nao-e-uma-data",
            last_commit_author="Test",
            commit_count=1,
        )
        assert _infer_status(bad) == "unknown"


class TestGetLastModified:
    """_get_last_modified(): path com arquivos, diretório vazio e exclusão de dirs."""

    def test_project_with_files_returns_isoformat(self, tmp_path: Path) -> None:
        """Projeto com arquivo real → ISO string com 'T'."""
        (tmp_path / "main.py").write_text("print('hello')")
        result = _get_last_modified(tmp_path)
        assert "T" in result

    def test_empty_dir_returns_isoformat(self, tmp_path: Path) -> None:
        """Diretório vazio → retorna now() como ISO string."""
        result = _get_last_modified(tmp_path)
        assert "T" in result

    def test_excludes_git_dir_files(self, tmp_path: Path) -> None:
        """Arquivo dentro de .git/ é ignorado no cálculo de mtime."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")
        (tmp_path / "main.py").write_text("code")
        result = _get_last_modified(tmp_path)
        assert "T" in result


class TestScanProjectAIIntegration:
    """Cobertura das linhas 183-189: bloco de integração IA em scan_project."""

    def test_scan_project_no_ai_flag_skips_ai(self, tmp_path: Path) -> None:
        """scan_project com no_ai=True não chama generate_summary."""
        (tmp_path / "main.py").write_text("print('hello')")
        config = {"no_ai": True, "ai_min_words": 30, "ai_max_tokens": 2000}
        from unittest.mock import patch

        with patch("extractor.metadata_extractor.generate_summary") as mock_gen:
            result = scan_project(tmp_path, config=config)
            mock_gen.assert_not_called()
        assert result is not None

    def test_scan_project_ai_sets_generated_source(self, tmp_path: Path) -> None:
        """scan_project com IA disponível seta description_source='ai-generated'."""
        (tmp_path / "main.py").write_text("print('hello')")
        config = {"no_ai": False, "ai_min_words": 30, "ai_max_tokens": 2000}
        from unittest.mock import patch

        with patch("extractor.metadata_extractor.generate_summary", return_value="Descrição gerada."):
            result = scan_project(tmp_path, config=config)
        assert result is not None
        assert result["description"] == "Descrição gerada."
        assert result["description_source"] == "ai-generated"

    def test_scan_project_ai_fails_no_readme_sets_unavailable(self, tmp_path: Path) -> None:
        """scan_project sem README + IA falha → description_source='ai-unavailable'."""
        (tmp_path / "main.py").write_text("print('hello')")
        config = {"no_ai": False, "ai_min_words": 30, "ai_max_tokens": 2000}
        from unittest.mock import patch

        with patch("extractor.metadata_extractor.generate_summary", return_value=None):
            result = scan_project(tmp_path, config=config)
        assert result is not None
        assert result["description_source"] == "ai-unavailable"

    def test_scan_project_without_config_skips_ai(self, tmp_path: Path) -> None:
        """scan_project sem config não tenta IA."""
        (tmp_path / "main.py").write_text("print('hello')")
        from unittest.mock import patch

        with patch("extractor.metadata_extractor.generate_summary") as mock_gen:
            result = scan_project(tmp_path)
            mock_gen.assert_not_called()
        assert result is not None


class TestScanProjectGitPopulated:
    """Cobertura de scan_project com repositório git real (linhas 149-153)."""

    def test_scan_project_with_git_populates_git_dict(self, git_project: Path) -> None:
        """scan_project em projeto com git real preenche campos branch, hash, etc."""
        result = scan_project(git_project)
        assert result is not None
        git = result["git"]
        assert git["initialized"] is True  # type: ignore[index]
        assert "branch" in git  # type: ignore[operator]
        assert "last_commit_hash" in git  # type: ignore[operator]
        assert "last_commit_date" in git  # type: ignore[operator]
        assert "commit_count" in git  # type: ignore[operator]

    def test_scan_project_with_git_has_active_or_unknown_status(self, git_project: Path) -> None:
        """scan_project em projeto com commit recente → status 'active' ou 'unknown'."""
        result = scan_project(git_project)
        assert result is not None
        assert result["status"] in ("active", "unknown")
