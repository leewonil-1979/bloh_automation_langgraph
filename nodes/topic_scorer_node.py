# nodes/topic_scorer_node.py
import json
from typing import Dict, Any, List
from utils.logger import get_logger
from utils.llm_client import LLMClient

logger = get_logger("TopicScorerNode")


class TopicScorerNode:
    """
    Step0-2: 주제 스코어링 노드
    - 확장된 주제들을 수익성, 확장성, 지속가능성 기준으로 점수화
    - 최종 주제 1개 자동 선정
    """

    def __init__(self) -> None:
        self.llm = LLMClient()

    def score_and_select(self, topics_data: Dict[str, Any]) -> Dict[str, Any]:
        """주제들을 스코어링하고 최적의 주제 선정"""
        logger.info("TopicScorerNode: 주제 스코어링 시작")

        topics = topics_data.get("topics", [])
        if not topics:
            raise ValueError("스코어링할 주제가 없습니다")

        prompt = self._build_prompt(topics)

        try:
            raw = self.llm.chat(prompt, max_tokens=2000)
            parsed = self._safe_parse_json(raw)
            
            # 최고 점수 주제 자동 선정
            scored_topics = parsed.get("scored_topics", [])
            if scored_topics:
                best_topic = max(scored_topics, key=lambda x: x.get("total_score", 0))
                parsed["selected_topic"] = best_topic
                logger.info(f"TopicScorerNode: 최종 선정 - {best_topic.get('title')}")
            
            return parsed
            
        except Exception as e:
            logger.error(f"TopicScorerNode 실패: {e}")
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
            with open("debug_topic_scorer.txt", "w", encoding="utf-8") as f:
                f.write(text)
            raise ValueError(f"JSON 파싱 실패: {e.msg}")

    def _build_prompt(self, topics: List[Dict[str, Any]]) -> str:
        topics_json = json.dumps(topics, ensure_ascii=False, indent=2)
        
        return f"""
다음 블로그 주제 후보들을 분석하여 점수를 매기고 최적의 주제를 추천해주세요.

[주제 후보들]
{topics_json}

[평가 기준]
1. **수익성 (0-10점)**
   - 광고 수익 가능성
   - 제휴 마케팅 가능성
   - 트래픽 잠재력
   - 키워드 검색량

2. **확장성 (0-10점)**
   - 1source multi use 가능성 (유튜브, 인스타, 블로그 등 다중 채널)
   - 시리즈물 제작 가능성
   - 관련 주제 확장 가능성

3. **지속가능성 (0-10점)**
   - 시즌에 관계없이 지속적 검색 가능성
   - 콘텐츠 업데이트 용이성
   - 경쟁 강도 (낮을수록 높은 점수)

4. **생산 난이도 (0-10점, 낮을수록 좋음)**
   - 콘텐츠 제작 난이도
   - 전문성 요구 수준
   - 자료 수집 용이성

[출력 형식]
JSON만 출력하세요.

{{
  "scored_topics": [
    {{
      "id": 1,
      "title": "주제 제목",
      "profitability_score": 8,
      "scalability_score": 7,
      "sustainability_score": 9,
      "difficulty_score": 6,
      "total_score": 30,
      "reasoning": "점수 근거 설명 (100-150자)",
      "recommended_platforms": ["네이버", "티스토리"]
    }}
  ],
  "recommendation": "최고 점수를 받은 주제에 대한 추천 이유 (150-200자)"
}}

**중요: total_score = profitability + scalability + sustainability - difficulty**
**유효한 JSON만 출력하세요.**
"""
