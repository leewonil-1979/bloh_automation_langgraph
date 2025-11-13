# nodes/post_writer_node.py
import json
from typing import Dict, Any, List
from utils.logger import get_logger
from utils.llm_client import LLMClient

logger = get_logger("PostWriterNode")


class PostWriterNode:
    """
    Step4: SEO 본문 생성 노드
    - Step1~3 데이터 기반으로 최종 글 구성
    - H1, H2, H3 자동 구성
    - 표, 리스트, FAQ 포함
    - 이미지 placeholder 포함
    - CTA placeholder 포함
    """

    def __init__(self) -> None:
        self.llm = LLMClient()

    def write(self, topic_json: Dict[str, Any],
              kws_json: Dict[str, Any],
              serp_json: Dict[str, Any]) -> Dict[str, Any]:

        logger.info("PostWriterNode: SEO 본문 생성 시작")

        topic = topic_json.get("topic", "")
        main_keywords = topic_json.get("main_keywords", [])
        clusters = kws_json.get("clusters", {})
        serp_items = serp_json.get("serp_results", [])

        prompt = self._build_prompt(topic, main_keywords, clusters, serp_items)

        try:
            raw = self.llm.chat(prompt)
            parsed = self._safe_parse_json(raw)
            logger.info("PostWriterNode: 완료")
            return parsed
        except Exception:
            logger.error("PostWriterNode JSON 파싱 실패")
            raise

    def _safe_parse_json(self, text: str) -> Dict[str, Any]:
        try:
            # JSON 추출
            s = text.find("{")
            e = text.rfind("}")
            
            if s == -1 or e == -1:
                raise ValueError("JSON 형식을 찾을 수 없습니다")
            
            json_text = text[s:e+1]
            
            # 파싱 시도 - LLM이 이미 올바른 JSON을 생성했다고 가정
            return json.loads(json_text)
            
        except json.JSONDecodeError as e:
            logger.error("=" * 60)
            logger.error("JSON 파싱 실패 - 상세 정보:")
            logger.error(f"에러 위치: line {e.lineno}, column {e.colno}")
            logger.error(f"에러 메시지: {e.msg}")
            logger.error("=" * 60)
            logger.error("원본 텍스트:")
            logger.error(text)
            logger.error("=" * 60)
            
            # JSON 텍스트를 파일로 저장 (디버깅용)
            with open("debug_json_error.txt", "w", encoding="utf-8") as f:
                f.write(text)
            logger.error("원본 텍스트를 debug_json_error.txt 파일에 저장했습니다.")
            
            raise ValueError(f"포스트 작성 JSON 파싱 실패: {e.msg}")
            
        except Exception as e:
            logger.error("LLM JSON 파싱 실패 (알 수 없는 오류)")
            logger.error(text)
            raise ValueError(f"포스트 작성 JSON 파싱 실패: {str(e)}")

    def _build_prompt(
        self,
        topic: str,
        main_keywords: List[str],
        clusters: Dict[str, List[str]],
        serp_items: List[Dict[str, Any]],
    ) -> str:

        return f"""
다음 정보를 기반으로 SEO 최적화 블로그 글을 작성해줘.

[주제]
{topic}

[메인 키워드]
{main_keywords}

[키워드 클러스터]
{json.dumps(clusters, ensure_ascii=False, indent=2)}

[경쟁 SERP 요약]
{json.dumps(serp_items[:5], ensure_ascii=False, indent=2)}

[중요: 출력 형식]
- 반드시 유효한 JSON만 출력해주세요
- JSON 외 다른 텍스트는 절대 포함하지 마세요
- 모든 문자열 값에서 줄바꿈은 공백으로 대체해주세요
- 쌍따옴표(")는 반드시 이스케이프(\\")해주세요

[JSON 스키마]
{{
  "title": "48-58자 제목",
  "h1": "H1 헤딩",
  "sections": [
    {{
      "h2": "섹션 제목",
      "h3_blocks": [
        {{
          "h3": "하위 제목",
          "content": "80-140자 본문 (줄바꿈 없이)"
        }}
      ]
    }}
  ],
  "table": {{
    "title": "표 제목",
    "headers": ["헤더1", "헤더2", "헤더3"],
    "rows": [
      ["데이터1", "데이터2", "데이터3"]
    ]
  }},
  "list_block": {{
    "title": "리스트 제목",
    "items": ["항목1", "항목2", "항목3", "항목4", "항목5"]
  }},
  "faqs": [
    {{
      "q": "질문1",
      "a": "답변1"
    }},
    {{
      "q": "질문2",
      "a": "답변2"
    }},
    {{
      "q": "질문3",
      "a": "답변3"
    }}
  ],
  "images": [
    {{
      "id": "IMG1",
      "alt": "이미지1 설명",
      "caption": "이미지1 캡션"
    }},
    {{
      "id": "IMG2",
      "alt": "이미지2 설명",
      "caption": "이미지2 캡션"
    }},
    {{
      "id": "IMG3",
      "alt": "이미지3 설명",
      "caption": "이미지3 캡션"
    }}
  ],
  "cta": {{
    "top": "[CTA_TOP]",
    "mid": "[CTA_MID]",
    "bottom": "[CTA_BOTTOM]"
  }}
}}

[필수 조건]
1. 제목(title)은 48~58자
2. 모든 content는 80~140자 (줄바꿈 없이 공백으로만)
3. H2 섹션 최소 4개
4. 각 H2마다 H3 블록 최소 2개
5. 표의 headers는 최소 3개
6. 표의 rows는 최소 3개
7. 리스트 items는 최소 5개
8. FAQ는 정확히 3개
9. 이미지는 정확히 3개 (IMG1, IMG2, IMG3)
10. 모든 문자열 값에 줄바꿈 금지 (공백으로 대체)

**JSON만 출력하세요. 다른 텍스트나 설명은 절대 포함하지 마세요.**
        """

