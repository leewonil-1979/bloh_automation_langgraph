# nodes/content_planner_node.py
import json
from typing import Dict, Any, List
from utils.logger import get_logger
from utils.llm_client import HybridLLMClient

logger = get_logger("ContentPlannerNode")


class ContentPlannerNode:
    """
    Step2-2: 콘텐츠 플래너 노드
    - SERP 결과 분석하여 30일 글감 로테이션 생성
    - 무한 루프 가능한 구조
    - Claude 3.5 Sonnet 사용으로 고품질 기획
    """

    def __init__(self) -> None:
        self.llm = HybridLLMClient()

    def plan(self, serp_data: Dict[str, Any]) -> Dict[str, Any]:
        """30일 글감 로테이션 계획 생성"""
        logger.info("ContentPlannerNode: 30일 콘텐츠 계획 생성 시작")

        serp_results = serp_data.get("serp_results", [])
        topic = serp_data.get("topic", "")
        
        if not serp_results:
            raise ValueError("SERP 결과가 없습니다")

        prompt = self._build_prompt(topic, serp_results)

        try:
            # Claude를 사용한 창의적 콘텐츠 기획
            raw = self.llm.chat(
                prompt, 
                max_tokens=4000,  # Claude 3 Haiku 최대값 (4096)
                task_type="creative"  # Claude 우선 사용
            )
            parsed = self._safe_parse_json(raw)
            logger.info(f"ContentPlannerNode: 30일 계획 생성 완료")
            return parsed
            
        except Exception as e:
            logger.error(f"ContentPlannerNode 실패: {e}")
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
            with open("debug_content_planner.txt", "w", encoding="utf-8") as f:
                f.write(text)
            raise ValueError(f"JSON 파싱 실패: {e.msg}")

    def _build_prompt(self, topic: str, serp_results: List[Dict[str, Any]]) -> str:
        # 상위 30개 제목만 추출
        titles = [item.get("title", "") for item in serp_results[:30]]
        titles_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(titles)])
        
        return f"""
다음 주제로 **Evergreen 콘텐츠 중심** 30일 로테이션을 만드세요.

[주제]
{topic}

[SERP 참고용]
{titles_text}

**중요 원칙:**
1. SERP는 참고만! 패턴을 그대로 따라하지 마세요
2. 메인 주제(4인 가족 여행) 60% + 서브 주제(반려견) 40% 균형
3. 다음 달에도 재사용 가능한 Evergreen 콘텐츠 중심
4. 특정 지역/계절에 편중되지 않게 분산
5. 수익형 콘텐츠(리뷰, 비교, 템플릿) 필수 포함

**6개 카테고리별 5개씩 생성 (총 30개):**

**[카테고리 1: 여행 준비 - 5개]**
- 초보자 가이드, 체크리스트, HOW-TO 중심
- 예: "4인 가족 여행 준비 완벽 가이드", "계절별 준비물 리스트"

**[카테고리 2: 여행지 추천 - 5개]**  
- 국내/해외, 테마별, 계절별 다양화
- 예: "가족 여행지 TOP 10", "예산별 여행지 추천"

**[카테고리 3: 실제 사례 - 5개]**
- 여행 후기, 브이로그식 스토리, 경험담
- 예: "우리 가족 제주도 3박4일 후기", "첫 해외여행 도전기"

**[카테고리 4: 비교/리뷰 - 5개]**
- 숙소, 교통, 장비, 패키지 비교 (수익형)
- 예: "호텔 vs 리조트 vs 펜션 비교", "필수템 리뷰"

**[카테고리 5: 문제 해결 - 5개]**
- 위기 대처, 안전, 건강, 날씨, 실패 사례
- 예: "여행 중 흔한 문제 해결법", "비 오는 날 대안"

**[카테고리 6: 일정/예산/템플릿 - 5개]**
- 계획표, 예산 가이드, 템플릿, 체크리스트
- 예: "2박3일 여행 예산 짜기", "여행 계획표 템플릿"

[출력 형식]
{{
  "topic": "{topic}",
  "analysis": {{
    "primary_focus": "메인 주제 (60%)",
    "secondary_focus": "서브 주제 (40%)",
    "target_keywords": ["키워드1", "키워드2", "키워드3"]
  }},
  "30_days_plan": [
    {{
      "day": 1,
      "category": "여행준비",
      "title": "글감 제목 (40-60자)",
      "content_type": "체크리스트",
      "main_keywords": ["키워드1", "키워드2"]
    }}
  ]
}}

**필수 체크:**
- 각 카테고리 정확히 5개씩
- 특정 지역 편중 금지 (예: 제주도만 5개 X)
- Evergreen (언제든 재사용 가능)
- 유효한 JSON만 출력
"""
