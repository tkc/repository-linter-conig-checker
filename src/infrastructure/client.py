import re
from base64 import b64decode
from typing import Optional, Tuple, List, Dict, Any

import requests
from infrastructure.env import TOKEN

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def github_url_to_api(
    repo_url: str, file_paths: List[str]
) -> Tuple[Optional[str], Optional[str]]:
    """
    GitHub のリポジトリ URL と対象ファイルパスのリストから、
    存在する最初のファイルの API エンドポイント URL とファイル名を返す。
    """
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        raise ValueError("無効な GitHub リポジトリ URL です。")
    owner, repo = match.groups()
    for file_path in file_paths:
        api_url: str = (
            f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        )
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            return api_url, file_path
    return None, None


def get_file_content(api_url: str) -> Optional[str]:
    """
    GitHub API から指定ファイルの内容を取得し、Base64 をデコードして返す。
    """
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        return None
    data: Dict[str, Any] = response.json()
    if "content" in data:
        return b64decode(data["content"]).decode("utf-8")
    return None
