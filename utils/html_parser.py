# utils/html_parser.py
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger("HTMLParser")


class HTMLParser:
    """블로그 페이지 HTML 크롤러"""

    def fetch(self, url: str) -> str:
        try:
            res = requests.get(url, timeout=7)
            res.raise_for_status()
            return res.text
        except Exception as e:
            logger.error(f"URL 요청 실패: {url}")
            return ""

    def extract(self, html: str) -> Dict[str, Any]:
        if not html:
            return {"text": "", "headings": []}

        try:
            soup = BeautifulSoup(html, "html.parser")

            # 본문 텍스트
            texts = " ".join([p.get_text(strip=True) for p in soup.find_all("p")])

            # 헤더(H2/H3) 추출
            h_tags = {
                "H2": [h.get_text(strip=True) for h in soup.find_all("h2")],
                "H3": [h.get_text(strip=True) for h in soup.find_all("h3")],
            }

            return {"text": texts, "headings": h_tags}
        except Exception:
            logger.error("HTML 파싱 실패")
            return {"text": "", "headings": []}
