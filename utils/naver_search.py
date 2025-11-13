# utils/naver_search.py
import os
import requests
from typing import Dict, List, Any
from utils.logger import get_logger

logger = get_logger("NaverSearch")


class NaverSearchClient:
    """네이버 검색 API 클라이언트"""

    def __init__(self) -> None:
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError("NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 .env에 없습니다.")

        self.url = "https://openapi.naver.com/v1/search/blog.json"

    def search(self, query: str, num: int = 10) -> List[Dict[str, Any]]:
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }

        params = {
            "query": query,
            "display": num,
            "start": 1,
            "sort": "sim",
        }

        try:
            res = requests.get(self.url, headers=headers, params=params, timeout=5)
            res.raise_for_status()
            data = res.json()
            return data.get("items", [])
        except Exception as e:
            logger.error(f"네이버 검색 API 요청 실패: {e}")
            raise e
