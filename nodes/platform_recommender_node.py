# nodes/platform_recommender_node.py
import json
from typing import Dict, Any, List
from utils.logger import get_logger
from utils.llm_client import LLMClient

logger = get_logger("PlatformRecommenderNode")


class PlatformRecommenderNode:
    """
    Step1: 플랫폼 추천 노드
    - 선정된 주제에 가장 적합한 블로그 플랫폼 추천
    - 수익성, 1source multi use, 난이도 종합 분석
    """

    def __init__(self) -> None:
        self.llm = LLMClient()

    def recommend(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """주제에 최적화된 플랫폼 추천"""
        logger.info("PlatformRecommenderNode: 플랫폼 추천 시작")

        selected_topic = topic_data.get("selected_topic", {})
        if not selected_topic:
            raise ValueError("선정된 주제가 없습니다")

        prompt = self._build_prompt(selected_topic)

        try:
            raw = self.llm.chat(prompt, max_tokens=2000)
            parsed = self._safe_parse_json(raw)
            logger.info(f"PlatformRecommenderNode: 완료 - 추천 플랫폼: {parsed.get('primary_platform')}")
            return parsed
            
        except Exception as e:
            logger.error(f"PlatformRecommenderNode 실패: {e}")
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
            with open("debug_platform_recommender.txt", "w", encoding="utf-8") as f:
                f.write(text)
            raise ValueError(f"JSON 파싱 실패: {e.msg}")

    def _build_prompt(self, topic: Dict[str, Any]) -> str:
        topic_json = json.dumps(topic, ensure_ascii=False, indent=2)
        
        return f"""
다음 블로그 주제에 가장 적합한 블로그 플랫폼을 추천해주세요.

[선정된 주제]
{topic_json}

[플랫폼 옵션 및 특징]
1. **네이버 블로그**
   - 장점: 한국 검색 최적화, 높은 초기 트래픽, 쉬운 SEO
   - 단점: 해외 트래픽 없음, 애드센스 불가
   - 적합: 정보성 콘텐츠, 로컬 키워드, 초보자, 빠른 수익화
   
2. **티스토리**
   - 장점: 애드센스 가능, 커스터마이징, 네이버 검색 노출
   - 단점: 초기 트래픽 확보 어려움
   - 적합: 전문 블로거, 장기 수익화, 기술/IT 콘텐츠

3. **워드프레스 (WordPress.org)**
   - 장점: 완전한 소유권, 글로벌 SEO, 무제한 수익화
   - 단점: 초기 비용(호스팅), 기술적 난이도
   - 적합: 전문가 콘텐츠, 글로벌 타겟, 장기 자산화

4. **구글 블로거 (Blogger)**
   - 장점: 무료, 구글 생태계, 애드센스 통합
   - 단점: 제한적 커스터마이징, 낮은 한국 검색 노출
   - 적합: 영문 콘텐츠, 글로벌 타겟, 실험용

5. **미디엄 (Medium)**
   - 장점: 높은 독자층, 전문가 이미지, 파트너 프로그램
   - 단점: SEO 제한적, 수익화 어려움
   - 적합: 전문가 칼럼, 사상/인사이트

[평가 기준]
1. 수익성: 광고, 제휴, RPM
2. 트래픽 확보 용이성
3. 1source multi use 가능성
4. SEO 난이도
5. 초기 비용 및 운영 난이도

[출력 형식]
JSON만 출력하세요.

{{
  "primary_platform": "메인 추천 플랫폼명",
  "secondary_platforms": ["보조 추천 플랫폼1", "보조 추천 플랫폼2"],
  "platform_scores": [
    {{
      "platform": "네이버 블로그",
      "profitability": 8,
      "traffic_potential": 9,
      "multi_use": 6,
      "seo_difficulty": 3,
      "total_score": 26,
      "pros": ["장점1", "장점2"],
      "cons": ["단점1", "단점2"]
    }}
  ],
  "recommendation_reason": "메인 플랫폼 추천 이유 (200-250자)",
  "strategy": {{
    "content_format": "추천 콘텐츠 형식 (예: 긴글, 이미지중심, 리스트형 등)",
    "posting_frequency": "권장 포스팅 빈도",
    "monetization_method": "수익화 방법 (예: 애드센스, 제휴마케팅, 스폰서십 등)",
    "multi_platform_plan": "다중 플랫폼 활용 전략"
  }}
}}

**중요: 주제의 특성을 고려하여 실질적인 추천을 해주세요.**
**유효한 JSON만 출력하세요.**
"""
