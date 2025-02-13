import pytest
from src.usecase.check_linters import check_linters_installed
from src.domain.model import (
    CommonCheckResult,
)

from src.domain.constants import LINTERS, PYPROJECT_FILE, REQUIREMENTS_FILE


def test_check_linters_installed_pyproject():
    sample_pyproject = """
[tool.poetry]
name = "test_project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.9"
mypy = "0.971"
ruff = "0.0.241"

[tool.poetry.dev-dependencies]
pytest = "^7.2.0"
"""
    result: CommonCheckResult = check_linters_installed(
        sample_pyproject, PYPROJECT_FILE
    )
    assert result.success is True
    # pyproject.toml の場合は Poetry を使っているので True となる
    assert result.data.get("poetry_used") is True

    # "mypy" と "ruff" は True になるはずで、他は False
    for linter in LINTERS:
        if linter in ["mypy", "ruff"]:
            assert result.data.get(linter) is True, f"{linter} should be True"
        else:
            assert result.data.get(linter) is False, f"{linter} should be False"


def test_check_linters_installed_requirements():
    sample_requirements = """
mypy==0.971
ruff==0.0.241
"""
    result: CommonCheckResult = check_linters_installed(
        sample_requirements, REQUIREMENTS_FILE
    )
    assert result.success is True
    # requirements.txt では Poetry を使わないので False になる
    assert result.data.get("poetry_used") is False

    # "mypy" と "ruff" は True になるはずで、他は False
    for linter in LINTERS:
        if linter in ["mypy", "ruff"]:
            assert result.data.get(linter) is True, f"{linter} should be True"
        else:
            assert result.data.get(linter) is False, f"{linter} should be False"


def test_check_linters_installed_no_linters():
    sample_pyproject = """
[tool.poetry]
name = "test_project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.9"

[tool.poetry.dev-dependencies]
pytest = "^7.2.0"
"""
    result: CommonCheckResult = check_linters_installed(
        sample_pyproject, PYPROJECT_FILE
    )
    assert result.success is True
    # Poetry は使われている
    assert result.data.get("poetry_used") is True

    # 依存関係に linters が含まれていないので全て False であることを確認
    for linter in LINTERS:
        assert result.data.get(linter) is False, f"{linter} should be False"
