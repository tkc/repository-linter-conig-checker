import pandas as pd
import yaml
from typing import Dict, Any, List

from src.domain.constants import (
    RUFF_RULES,
    PYPROJECT_FILE,
    REQUIREMENTS_FILE,
    MYPY_INI_FILE,
    RUFF_TOML_FILE,
)
from src.infrastructure.client import github_url_to_api, get_file_content
from src.usecase.check_linters import check_linters_installed
from src.usecase.check_ruff import check_ruff_rules
from src.usecase.check_mypy import check_mypy_ini


def process_repository(repo: str) -> pd.DataFrame:
    """
    1 つのリポジトリについて、各種チェックを行い結果を DataFrame として返す。
    """
    repo_url = f"https://github.com/{repo}"
    result_data: Dict[str, Any] = {
        "repository": repo_url,
        "file": None,
    }

    # ① pyproject.toml または requirements.txt のチェック
    api_endpoint, file_name = github_url_to_api(
        repo_url, [PYPROJECT_FILE, REQUIREMENTS_FILE]
    )
    if api_endpoint:
        file_content = get_file_content(api_endpoint)
        if file_content:
            linters_result = check_linters_installed(file_content, file_name)
            result_data.update(linters_result.data)
            result_data["file"] = file_name

    # ② mypy.ini のチェック
    api_endpoint, _ = github_url_to_api(repo_url, [MYPY_INI_FILE])
    if api_endpoint:
        file_content = get_file_content(api_endpoint)
        if file_content:
            mypy_result = check_mypy_ini(file_content)
            result_data.update(mypy_result.data)

    # ③ ruff.toml または pyproject.toml 内の ruff 設定のチェック
    api_endpoint, file_name = github_url_to_api(
        repo_url, [RUFF_TOML_FILE, PYPROJECT_FILE]
    )
    if api_endpoint:
        file_content = get_file_content(api_endpoint)
        if file_content:
            if file_name == RUFF_TOML_FILE:
                result_data["ruff_toml_exists"] = True
            ruff_result = check_ruff_rules(file_content)
            result_data.update(ruff_result.data)
        else:
            result_data.update({f"ruff_{rule}": False for rule in RUFF_RULES})
    else:
        result_data.update({f"ruff_{rule}": False for rule in RUFF_RULES})

    df = pd.DataFrame([result_data])
    return df


def main(yaml_file: str) -> pd.DataFrame:
    """
    YAML ファイルからリポジトリ URL の配列を読み込み、各リポジトリのチェック結果をまとめた DataFrame を返す。
    """
    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    repo_urls: List[str] = data.get("repositories", [])

    all_dfs: List[pd.DataFrame] = []
    for repo_url in repo_urls:
        df_repo = process_repository(repo_url)
        all_dfs.append(df_repo)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame()
    return final_df


if __name__ == "__main__":
    yaml_file = "repos.yaml"  # リポジトリ URL リストを含む YAML ファイル
    final_df = main(yaml_file)
    print(final_df)
    final_df.to_csv("linter_check_report.csv", index=False)
