import structlog
import pandas as pd
from src.infrastructure.env import TOKEN  # トークンを環境変数から取得するモジュール
from src.infrastructure.client import get_dependabot_alerts
from typing import Dict, Any, List
import yaml

logger = structlog.get_logger()

def process_repository(repos:str) -> None:
    alerts_list = []  # すべてのアラート情報をまとめるリスト

    for repo in repos:
        parts = repo.split("/")
        owner=parts[0]
        repo=parts[1]

        logger.info("Fetching Dependabot alerts", owner=owner, repo=repo)
        alerts = get_dependabot_alerts(owner, repo, TOKEN)

        # 各アラートにリポジトリ情報や severity、ライブラリ名を追加
        for alert in alerts:
            alert["owner"] = owner
            alert["repo"] = repo
            # security_vulnerability が存在すれば severity とライブラリ名を取得、なければ "unknown" とする
            security_info = alert.get("security_vulnerability", {})
            alert["severity"] = security_info.get("severity", "unknown")
            alert["library_name"] = security_info.get("package", {}).get("name", "unknown")
            alerts_list.append(alert)

    # リストを DataFrame に変換
    df = pd.DataFrame(alerts_list)
    # 出力するカラムを指定（利用可能なカラムのみ選択）
    columns_to_show = ["owner", "repo", "state", "severity", "library_name", "number", "created_at"]
    available_columns = [col for col in columns_to_show if col in df.columns]
    df = df[available_columns]

    # CSV ファイルに出力
    output_csv = "dependabot_alerts.csv"
    df.to_csv(output_csv, index=False, encoding="utf-8")
    logger.info("CSV file created", filename=output_csv)
    logger.info(f"Repository alerts have been saved to '{output_csv}'.")


def main(yaml_file: str) -> pd.DataFrame:
    """
    YAML ファイルからリポジトリ URL の配列を読み込み、各リポジトリのチェック結果をまとめた DataFrame を返す。
    """
    with open(yaml_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    repo_urls: List[str] = data.get("repositories", [])

    logger.info("Processing repository", repo_url=repo_urls)
    process_repository(repo_urls)


if __name__ == "__main__":
    yaml_file = "repos.yaml"  # リポジトリ URL リストを含む YAML ファイル
    main(yaml_file)

