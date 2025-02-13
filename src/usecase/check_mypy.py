import configparser
from src.domain.model import CommonCheckResult


def check_mypy_ini(file_content: str) -> CommonCheckResult:
    """
    mypy.ini の設定が Static Mode かをチェックする。
    条件として、[mypy] セクション内で strict=True または disallow_untyped_defs=True が設定されているかを確認する。
    """
    try:
        config = configparser.ConfigParser()
        config.read_string(file_content)
        static_mode = False
        if config.has_section("mypy"):
            if config.has_option("mypy", "strict") and config.getboolean(
                "mypy", "strict"
            ):
                static_mode = True
            elif config.has_option(
                "mypy", "disallow_untyped_defs"
            ) and config.getboolean("mypy", "disallow_untyped_defs"):
                static_mode = True
        return CommonCheckResult(
            check_type="mypy_ini",
            success=True,
            data={"static_mode_enabled": static_mode},
        )
    except Exception as e:
        return CommonCheckResult(check_type="mypy_ini", success=False, error=str(e))
