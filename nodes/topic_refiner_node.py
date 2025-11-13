# nodes/topic_refiner_node.py
import json
from typing import Dict, Any, List
from utils.llm_client import LLMClient
from utils.logger import get_logger

logger = get_logger("TopicRefinerNode")

class TopicRefinerNode:
    """
    블로그 자동화 Step1.
    입력된 토픽을 기반으로 검색 의도 분석, 서브키워드, SEO 구조 템플릿을 생성하고
    다음 노드가 사용할 표준 JSON 포맷으로 반환하는 모듈
    """

    def __init__(self) -> None:
        self.llm = LLMClient()

    def refine(self, topic: str) -> Dict[str, Any]:
        """
        주제를 입력받아 정제된 SEO 출력 JSON 생성
        """

        logger.info(f"TopicRefinerNode 시작: topic={topic}")

        prompt = self._build_prompt(topic)

        try:
            raw_output = self.llm.chat(prompt)
            parsed = self._safe_parse_json(raw_output)

            logger.info("TopicRefinerNode 완료")
            return parsed

        except Exception as e:
            logger.exception("TopicRefinerNode 오류")
            raise e

    def _safe_parse_json(self, text: str) -> Dict[str, Any]:
        """
        LLM의 응답이 JSON이 아닐 가능성을 대비한 파서
        """

        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            cleaned = text[start:end]
            return json.loads(cleaned)

        except Exception:
            logger.error("JSON 파싱 실패. 원본 텍스트 로그 출력.")
            logger.error(text)
            raise ValueError("LLM 응답 JSON 파싱 실패")

    def _build_prompt(self, topic: str) -> str:
        """
        LLM에 전달할 프롬프트 생성
        """

        return f"""
다음 주제에 대해 검색의도 분석 + 서브키워드 + 경쟁 SERP 요약 + SEO 콘텐츠 구조를
아래 JSON 스키마에 맞춰 출력해줘.

주제: "{topic}"

출력 JSON 스키마:
{{
  "topic": "",
  "search_intent": "",
  "main_keywords": [],
  "sub_keywords": [],
  "benchmark_serp": [
    {{
      "title": "",
      "summary": "",
      "url": ""
    }}
  ],
  "recommended_structure": [
    {{
      "header": "",
      "description": ""
    }}
  ]
}}

조건:
1. JSON 외 텍스트 금지
2. URL은 실제 상위 랭킹에 존재할 법한 형태로 작성
3. 서브키워드는 5~10개
4. 헤더는 H2 기반 5~7개
        """

