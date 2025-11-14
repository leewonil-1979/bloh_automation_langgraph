# nodes/hybrid_post_writer_node.py
"""
GPT + Claude 협업 블로그 글 작성 노드
- Stage 1 (GPT): 뼈대 생성 (목차, 키워드, 구조)
- Stage 2 (Claude): 살 붙이기 (자연스러운 글쓰기, 스토리텔링)
"""

import json
from typing import Dict, Any, Optional
from utils.logger import get_logger
from utils.llm_client import LLMClient, HybridLLMClient

logger = get_logger("HybridPostWriter")


class HybridPostWriterNode:
    """
    2-Stage 협업 블로그 글 작성
    - GPT: 구조화된 뼈대 (빠르고 저렴)
    - Claude: 고품질 살 붙이기 (자연스럽고 창의적)
    """

    def __init__(self):
        self.gpt_client = LLMClient()  # Stage 1: 뼈대
        self.hybrid_client = HybridLLMClient()  # Stage 2: 살 붙이기

    def write(self, plan_item: Dict[str, Any], serp_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        2단계 협업 글쓰기
        
        Args:
            plan_item: 30일 계획 중 하나 (day, title, category, keywords)
            serp_context: SERP 데이터 (선택)
        
        Returns:
            완성된 블로그 글 (제목, 본문, 메타데이터)
        """
        logger.info("=" * 80)
        logger.info(f"🚀 2-Stage 협업 글쓰기 시작: {plan_item.get('title')}")
        logger.info("=" * 80)
        
        # Stage 1: GPT로 뼈대 생성
        skeleton = self._stage1_create_skeleton(plan_item, serp_context)
        logger.info("✅ Stage 1 완료: 뼈대 생성 (GPT)")
        
        # Stage 2: Claude로 살 붙이기
        final_post = self._stage2_add_flesh(skeleton, plan_item)
        logger.info("✅ Stage 2 완료: 살 붙이기 (Claude)")
        
        # 최종 결과 조합
        result = {
            "title": plan_item.get("title"),
            "category": plan_item.get("category"),
            "keywords": plan_item.get("main_keywords", []),
            "skeleton": skeleton,  # 디버깅용
            "final_content": final_post,
            "word_count": len(final_post),
            "metadata": {
                "stage1_model": "GPT-4o-mini",
                "stage2_model": "Claude 3 Haiku",
                "collaboration": "2-stage hybrid"
            }
        }
        
        logger.info(f"🎉 글쓰기 완료! 총 {len(final_post)}자")
        return result

    def _stage1_create_skeleton(self, plan_item: Dict[str, Any], serp_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Stage 1: GPT로 글의 뼈대 생성
        - 목차 구조 (H2, H3)
        - 각 섹션별 핵심 포인트
        - SEO 키워드 배치
        - 사실 정보 정리
        """
        logger.info("📐 Stage 1 시작: GPT로 뼈대 생성 중...")
        
        title = plan_item.get("title")
        category = plan_item.get("category")
        keywords = plan_item.get("main_keywords", [])
        
        # SERP 요약 (있으면)
        serp_summary = ""
        if serp_context and serp_context.get("serp_results"):
            top_3 = serp_context["serp_results"][:3]
            serp_summary = "\n참고 블로그 분석:\n"
            for idx, blog in enumerate(top_3, 1):
                serp_summary += f"{idx}. {blog.get('title')}\n"
        
        prompt = f"""당신은 블로그 글 구조 설계 전문가입니다.

**제목:** {title}
**카테고리:** {category}
**핵심 키워드:** {', '.join(keywords)}

{serp_summary}

**미션:** 이 주제로 블로그 글을 쓰기 위한 **뼈대(outline)**를 만들어주세요.

**출력 형식 (JSON):**
```json
{{
  "outline": [
    {{
      "section": "도입부",
      "h2_title": "제목",
      "key_points": ["포인트1", "포인트2"],
      "target_keywords": ["키워드1"]
    }},
    {{
      "section": "본문1",
      "h2_title": "제목",
      "h3_subsections": [
        {{
          "h3_title": "소제목1",
          "key_points": ["내용 요점"]
        }}
      ],
      "target_keywords": ["키워드2", "키워드3"]
    }},
    ... (본문 3~5개 섹션)
  ],
  "seo_meta": {{
    "meta_description": "150자 이내 요약",
    "focus_keyword": "메인 키워드"
  }}
}}
```

**요구사항:**
1. 도입부, 본문 3~5개, 결론부 구조
2. 각 섹션마다 핵심 포인트 3~5개
3. H2, H3 제목은 키워드 포함
4. 총 2000~3000자 분량 예상되도록 설계
5. SEO 최적화 구조

JSON만 출력하세요:"""

        try:
            raw = self.gpt_client.chat(prompt, max_tokens=2000)
            skeleton = self._safe_parse_json(raw)
            return skeleton
        except Exception as e:
            logger.error(f"Stage 1 실패: {e}")
            # 기본 뼈대 반환
            return {
                "outline": [
                    {
                        "section": "도입부",
                        "h2_title": title,
                        "key_points": keywords,
                        "target_keywords": keywords
                    }
                ],
                "seo_meta": {
                    "meta_description": title,
                    "focus_keyword": keywords[0] if keywords else ""
                }
            }

    def _stage2_add_flesh(self, skeleton: Dict[str, Any], plan_item: Dict[str, Any]) -> str:
        """
        Stage 2: Claude로 살 붙이기
        - 뼈대를 기반으로 자연스러운 글 작성
        - 스토리텔링, 예시, 감성 추가
        - 독자 몰입도 높이기
        """
        logger.info("✍️ Stage 2 시작: Claude로 살 붙이기 중...")
        
        title = plan_item.get("title")
        category = plan_item.get("category")
        outline = skeleton.get("outline", [])
        
        # 뼈대를 텍스트로 변환
        outline_text = ""
        for idx, section in enumerate(outline, 1):
            outline_text += f"\n## {section.get('h2_title', f'섹션{idx}')}\n"
            outline_text += f"핵심 포인트: {', '.join(section.get('key_points', []))}\n"
            
            if "h3_subsections" in section:
                for subsec in section["h3_subsections"]:
                    outline_text += f"  ### {subsec.get('h3_title')}\n"
                    outline_text += f"  - {', '.join(subsec.get('key_points', []))}\n"
        
        prompt = f"""당신은 한국 블로그 글쓰기 전문 작가입니다.

**제목:** {title}
**카테고리:** {category}

**뼈대 (Skeleton):**
{outline_text}

**미션:** 위 뼈대를 바탕으로 **완성된 블로그 글**을 작성해주세요.

**글쓰기 원칙:**
1. 자연스럽고 친근한 말투 (경어 사용, "~습니다" 스타일)
2. 실제 경험담처럼 생생하게
3. 각 섹션마다 예시, 비유 추가
4. 독자에게 공감과 도움이 되는 톤
5. 뼈대의 H2, H3 구조 유지하되, 살을 풍성하게
6. 총 2000~3000자 분량
7. 도입부는 흥미롭게, 결론부는 행동 유도

**출력:** 완성된 블로그 글 본문 (마크다운 형식, HTML 태그 없이)
"""

        try:
            final_content = self.hybrid_client.chat(
                prompt, 
                max_tokens=4000,
                task_type="creative"  # Claude 우선 사용
            )
            return final_content
        except Exception as e:
            logger.error(f"Stage 2 실패: {e}")
            # 뼈대라도 반환
            return outline_text

    def _safe_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """JSON 파싱 (코드 블록 제거)"""
        try:
            # ```json ... ``` 제거
            if "```json" in raw_text:
                start = raw_text.find("```json") + 7
                end = raw_text.rfind("```")
                raw_text = raw_text[start:end].strip()
            elif "```" in raw_text:
                start = raw_text.find("```") + 3
                end = raw_text.rfind("```")
                raw_text = raw_text[start:end].strip()
            
            return json.loads(raw_text)
        except Exception as e:
            logger.error(f"JSON 파싱 실패: {e}")
            return {}
