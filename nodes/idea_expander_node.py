# nodes/idea_expander_node.py
import json
from typing import Dict, Any, List
from utils.logger import get_logger
from utils.llm_client import LLMClient

logger = get_logger("IdeaExpanderNode")


class IdeaExpanderNode:
    """
    Step0-1: 아이디어 확장 노드
    - 사용자 입력 아이디어를 6~12개의 확장된 주제로 변환
    - 각 주제에 대한 기본 정보 제공
    """

    def __init__(self) -> None:
        self.llm = LLMClient()

    def expand(self, idea: str) -> Dict[str, Any]:
        """아이디어를 확장된 주제 리스트로 변환"""
        logger.info(f"IdeaExpanderNode: 아이디어 확장 시작 - {idea}")

        prompt = self._build_prompt(idea)

        try:
            raw = self.llm.chat(prompt, max_tokens=2000)
            parsed = self._safe_parse_json(raw)
            logger.info(f"IdeaExpanderNode: {len(parsed.get('topics', []))}개 주제 생성 완료")
            return parsed
        except Exception as e:
            logger.error(f"IdeaExpanderNode 실패: {e}")
            raise

    def _safe_parse_json(self, text: str) -> Dict[str, Any]:
        try:
            s = text.find("{")
            e = text.rfind("}")
            
            if s == -1 or e == -1:
                raise ValueError("JSON 형식을 찾을 수 없습니다")
            
            json_text = text[s:e+1]
            return json.loads(json_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            with open("debug_idea_expander.txt", "w", encoding="utf-8") as f:
                f.write(text)
            raise ValueError(f"JSON 파싱 실패: {e.msg}")

    def _build_prompt(self, idea: str) -> str:
        return f"""
다음 아이디어를 분석하여 블로그 주제로 확장해주세요.

[입력 아이디어]
{idea}

[요구사항]
1. 입력 아이디어를 6~12개의 구체적인 블로그 주제로 확장
2. 각 주제는 검색 가능하고 콘텐츠 생산이 가능해야 함
3. 다양한 각도에서 접근 (HOW-TO, 비교, 리뷰, 가이드, 팁 등)

[출력 형식]
JSON만 출력하세요. 다른 텍스트는 포함하지 마세요.

{{
  "original_idea": "입력된 원본 아이디어",
  "topics": [
    {{
      "id": 1,
      "title": "주제 제목 (40-60자)",
      "description": "주제 설명 (80-120자)",
      "category": "카테고리 (예: HOW-TO, 비교분석, 초보자가이드, 전문가팁 등)",
      "target_audience": "타겟 독자층",
      "estimated_difficulty": "난이도 (쉬움/보통/어려움)"
    }}
  ]
}}

**중요: 유효한 JSON만 출력하세요.**
"""
