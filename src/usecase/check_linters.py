import toml
from typing import Dict, Any, List

from src.domain.model import (
    CommonCheckResult,
)

from src.domain.constants import LINTERS, PYPROJECT_FILE, REQUIREMENTS_FILE


def check_linters_installed(file_content: str, file_type: str) -> CommonCheckResult:
    """
    pyproject.toml または requirements.txt 内に、対象の linter がインストールされているかをチェックする。
    また、pyproject.toml の場合は Poetry を使っているかも判定する。
    """
    try:
        linter_status: Dict[str, bool] = {linter: False for linter in LINTERS}
        is_poetry: bool = False
        if file_type == PYPROJECT_FILE:
            pyproject_data = toml.loads(file_content)
            dependencies: Dict[str, Any] = (
                pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            )
            dev_dependencies: Dict[str, Any] = (
                pyproject_data.get("tool", {})
                .get("poetry", {})
                .get("dev-dependencies", {})
            )
            is_poetry = "tool" in pyproject_data and "poetry" in pyproject_data["tool"]
            for linter in LINTERS:
                if linter in dependencies or linter in dev_dependencies:
                    linter_status[linter] = True
        elif file_type == REQUIREMENTS_FILE:
            lines: List[str] = file_content.splitlines()
            for linter in LINTERS:
                if any(line.strip().startswith(linter) for line in lines):
                    linter_status[linter] = True
        return CommonCheckResult(
            check_type="linters_installed",
            success=True,
            data={"poetry_used": is_poetry, **linter_status},
        )
    except Exception as e:
        return CommonCheckResult(
            check_type="linters_installed", success=False, error=str(e)
        )
