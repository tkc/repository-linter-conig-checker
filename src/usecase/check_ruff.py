import toml
from typing import Dict, List

from src.domain.model import CommonCheckResult
from src.domain.constants import RUFF_RULES


def check_ruff_rules(file_content: str) -> CommonCheckResult:
    """
    ruff.toml または pyproject.toml 内の ruff 設定から、select に指定されたルールを取得し、
    RUFF_RULES に含まれる各ルールが設定されているかをチェックする。

    対応ケース:
      - pyproject.toml の場合は、[tool.ruff] セクション内の select を優先して使用する。
      - ruff.toml の場合は、[lint] セクション内の select またはトップレベルの select を使用する。
    """
    try:
        config_data = toml.loads(file_content)
        selected_rules: List[str] = []
        if "tool" in config_data and "ruff" in config_data["tool"]:
            if "select" in config_data["tool"]["ruff"]:
                selected_rules = config_data["tool"]["ruff"]["select"]
        if (
            not selected_rules
            and "lint" in config_data
            and isinstance(config_data["lint"], dict)
        ):
            if "select" in config_data["lint"]:
                selected_rules = config_data["lint"]["select"]
        if not selected_rules and "select" in config_data:
            selected_rules = config_data["select"]
        rule_status: Dict[str, bool] = {
            f"ruff_{rule}": (rule in selected_rules) for rule in RUFF_RULES
        }
        return CommonCheckResult(
            check_type="ruff_rules", success=True, data=rule_status
        )
    except Exception as e:
        return CommonCheckResult(check_type="ruff_rules", success=False, error=str(e))
