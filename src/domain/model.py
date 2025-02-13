from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


class LintCheckResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    repository: str
    file: Optional[str]
    poetry_used: bool
    mypy: bool
    ruff: bool
    pyright: bool
    bandit: bool
    mypy_ini_exists: bool
    static_mode_enabled: bool
    ruff_toml_exists: bool


class CommonCheckResult(BaseModel):
    check_type: str
    success: bool
    data: Dict[str, Any] = {}
    error: Optional[str] = None
