import pytest
from src.usecase.check_mypy import check_mypy_ini
from src.domain.model import CommonCheckResult


def test_mypy_ini_strict_true():
    file_content = """
[mypy]
strict = true
"""
    result: CommonCheckResult = check_mypy_ini(file_content)
    assert result.success is True
    assert result.data.get("static_mode_enabled") is True


def test_mypy_ini_disallow_untyped_defs_true():
    file_content = """
[mypy]
disallow_untyped_defs = true
"""
    result: CommonCheckResult = check_mypy_ini(file_content)
    assert result.success is True
    assert result.data.get("static_mode_enabled") is True


def test_mypy_ini_both_false():
    file_content = """
[mypy]
strict = false
disallow_untyped_defs = false
"""
    result: CommonCheckResult = check_mypy_ini(file_content)
    assert result.success is True
    assert result.data.get("static_mode_enabled") is False


def test_mypy_ini_no_section():
    file_content = """
[other_section]
some_option = true
"""
    result: CommonCheckResult = check_mypy_ini(file_content)
    assert result.success is True
    # [mypy] セクションがないので static_mode_enabled は False であるべき
    assert result.data.get("static_mode_enabled") is False


def test_mypy_ini_invalid_format():
    # セクションヘッダーが存在しない場合、configparser はエラーを発生させる
    file_content = "this is not a valid INI content"
    result: CommonCheckResult = check_mypy_ini(file_content)
    assert result.success is False
    # エラーメッセージに "File contains no section headers" などが含まれていることを期待
    assert "section header" in result.error.lower()
