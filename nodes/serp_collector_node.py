# nodes/serp_collector_node.py
import json
from typing import Dict, Any, List

from utils.logger import get_logger
from utils.llm_client import LLMClient
from utils.naver_search import NaverSearchClient
from utils.html_parser import HTMLParser

logger = get_logger("SERPCollectorNode")


class SERPCollectorNode:
    """
    Step3: SERP 수집 노드
    - 네이버 검색 API → URL 수집
    - HTML 크롤링
    - 본문 텍스트·헤더 추출
    - LLM 요약
    """

    def __init__(self) -> None:
        self.search_api = NaverSearchClient()
        self.parser = HTMLParser()
        self.llm = LLMClient()

    def collect(self, keyword: str) -> Dict[str, Any]:
        logger.info(f"SERPCollector 시작: keyword={keyword}")

        # 1) 네이버 API 검색
        items = self.search_api.search(keyword)

        serp_results = []

        for idx, item in enumerate(items, start=1):
            url = item.get("link")
            title = item.get("title")

            html = self.parser.fetch(url)
            extracted = self.parser.extract(html)

            summary_data = self._summarize(title, extracted["text"])

            serp_results.append(
                {
                    "rank": idx,
                    "title": title,
                    "url": url,
                    "summary": summary_data.get("summary", ""),
                    "key_points": summary_data.get("key_points", []),
                    "headings": extracted["headings"],
                }
            )

        result = {
            "keyword": keyword,
            "serp_results": serp_results,
        }

        logger.info("SERPCollector 완료")
        return result

    def _summarize(self, title: str, text: str) -> Dict[str, Any]:
        prompt = f"""
아래 글을 요약하고 핵심 포인트를 추출해줘.

제목: {title}

본문:
{text[:3000]}

JSON으로 출력:
{{
  "summary": "",
  "key_points": []
}}
        """

        try:
            raw = self.llm.chat(prompt)
            start = raw.find("{")
            end = raw.rfind("}") + 1
            return json.loads(raw[start:end])
        except Exception:
            logger.error("요약 생성 실패")
            return {"summary": "", "key_points": []}
