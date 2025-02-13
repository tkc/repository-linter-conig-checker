import pytest
from src.usecase.check_ruff import check_ruff_rules
from src.domain.model import CommonCheckResult
from src.domain.constants import RUFF_RULES


def test_check_ruff_rules_tool_ruff_section():
    # [tool.ruff] セクションの場合のサンプル
    sample_pyproject = """
[tool.ruff]
select = ["F", "E", "W", "C90", "I"]
"""
    result: CommonCheckResult = check_ruff_rules(sample_pyproject)
    assert result.success is True
    # [tool.ruff] に記載されているルールのみ True になるはず
    for rule in RUFF_RULES:
        key = f"ruff_{rule}"
        if rule in ["F", "E", "W", "C90", "I"]:
            assert result.data.get(key) is True, f"{key} should be True"
        else:
            assert result.data.get(key) is False, f"{key} should be False"


def test_check_ruff_rules_lint_section():
    # ruff.toml 内の [lint] セクションの場合のサンプル
    sample_ruff_toml = """
[lint]
select = ["F", "E", "W", "C90", "I", "N", "D"]
"""
    result: CommonCheckResult = check_ruff_rules(sample_ruff_toml)
    assert result.success is True
    for rule in RUFF_RULES:
        key = f"ruff_{rule}"
        if rule in ["F", "E", "W", "C90", "I", "N", "D"]:
            assert result.data.get(key) is True, f"{key} should be True"
        else:
            assert result.data.get(key) is False, f"{key} should be False"


def test_check_ruff_rules_top_level_select():
    # トップレベルに select キーがある場合のサンプル
    sample_top_level = """
select = ["F", "W", "D"]
"""
    result: CommonCheckResult = check_ruff_rules(sample_top_level)
    assert result.success is True
    for rule in RUFF_RULES:
        key = f"ruff_{rule}"
        if rule in ["F", "W", "D"]:
            assert result.data.get(key) is True, f"{key} should be True"
        else:
            assert result.data.get(key) is False, f"{key} should be False"


def test_check_ruff_rules_invalid_content():
    # 無効な内容の場合のテスト
    sample_invalid = "this is not a valid toml content"
    result: CommonCheckResult = check_ruff_rules(sample_invalid)
    assert result.success is False
    assert result.error is not None
