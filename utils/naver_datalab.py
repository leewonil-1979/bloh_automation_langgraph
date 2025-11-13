# utils/naver_datalab.py
import os
import json
import logging
import requests
from typing import Dict, List, Any

from utils.logger import get_logger

logger = get_logger("NaverDataLab")


class NaverDataLabClient:
    """네이버 데이터랩 검색량 조회 클라이언트"""

    def __init__(self) -> None:
        self.client_id = os.getenv("NAVER_CLIENT_ID")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            logger.warning("NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET 미설정. LLM fallback을 사용합니다.")

        self.url = "https://openapi.naver.com/v1/datalab/search"

    def get_volume(self, keywords: List[str]) -> Dict[str, Any]:
        """
        키워드 검색량 조회
        """

        if not self.client_id or not self.client_secret:
            return {"fallback": True}

        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json",
        }

        body = {
            "startDate": "2024-01-01",
            "endDate": "2024-12-31",
            "timeUnit": "month",
            "keywordGroups": [{"groupName": kw, "keywords": [kw]} for kw in keywords],
        }

        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(body))
            response.raise_for_status()
            result = response.json()
            return {"fallback": False, "result": result}
        except Exception as e:
            logger.error("데이터랩 API 호출 실패. Fallback 사용 예정.")
            return {"fallback": True}
