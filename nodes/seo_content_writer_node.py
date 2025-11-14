"""
Step 4: SEO 콘텐츠 자동 생성 노드

30일 계획을 받아 각 Day별로 완성된 SEO 최적화 블로그 글을 생성합니다.

입력:
- 30일 콘텐츠 계획
- tone_style_guide.json (문체·톤 가이드)
- SERP 컨텍스트

출력:
- content/dayXX_content.json (Day 1~30)
"""

import json
import logging
from typing import Dict, Any, List, Optional
from utils.llm_client import HybridLLMClient, LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SEOContentWriterNode:
    """SEO 콘텐츠 자동 생성 노드"""
    
    def __init__(self):
        self.gpt = LLMClient()  # 구조 생성용
        self.claude = HybridLLMClient()  # 본문 작성용
    
    def generate_all(
        self,
        content_plan: List[Dict[str, Any]],
        tone_guide: Dict[str, Any],
        serp_context: Optional[Dict[str, Any]] = None,
        start_day: int = 1,
        end_day: int = 30
    ) -> List[Dict[str, Any]]:
        """
        30일 계획을 받아 전체 콘텐츠 생성
        
        Args:
            content_plan: 30일 콘텐츠 계획
            tone_guide: 문체·톤 가이드
            serp_context: SERP 분석 결과 (선택)
            start_day: 시작 일자
            end_day: 종료 일자
        
        Returns:
            생성된 콘텐츠 리스트
        """
        logger.info(f"📝 Step 4: SEO 콘텐츠 생성 시작 (Day {start_day}~{end_day})")
        
        results = []
        
        for day_num in range(start_day, end_day + 1):
            if day_num > len(content_plan):
                logger.warning(f"⚠️  Day {day_num}는 계획에 없습니다. 건너뜁니다.")
                continue
            
            day_plan = content_plan[day_num - 1]
            logger.info(f"\n📌 Day {day_num}: {day_plan.get('title', 'N/A')}")
            
            # 단일 글 생성
            content = self.generate_single(day_num, day_plan, tone_guide, serp_context)
            results.append(content)
            
            logger.info(f"   ✅ Day {day_num} 완료 ({len(content.get('content', ''))}자)")
        
        logger.info(f"\n🎉 총 {len(results)}개 콘텐츠 생성 완료!")
        return results
    
    def generate_single(
        self,
        day_num: int,
        day_plan: Dict[str, Any],
        tone_guide: Dict[str, Any],
        serp_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        단일 Day 콘텐츠 생성
        
        Args:
            day_num: Day 번호
            day_plan: 해당 Day 계획
            tone_guide: 문체·톤 가이드
            serp_context: SERP 컨텍스트
        
        Returns:
            완성된 콘텐츠
        """
        # 1단계: GPT로 구조 생성 (H2/H3, 표, 리스트, FAQ)
        structure = self._generate_structure(day_num, day_plan, tone_guide, serp_context)
        
        # 2단계: Claude로 본문 작성 (오프닝, 각 섹션 본문, CTA)
        full_content = self._write_content(day_num, day_plan, structure, tone_guide, serp_context)
        
        return full_content
    
    def _generate_structure(
        self,
        day_num: int,
        day_plan: Dict[str, Any],
        tone_guide: Dict[str, Any],
        serp_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        GPT를 사용하여 글 구조 생성 (빠르고 저렴)
        """
        title = day_plan.get("title", "제목 없음")
        category = day_plan.get("category", "일반")
        keywords = day_plan.get("keywords", [])
        
        # SERP 키워드 추가
        if serp_context:
            serp_keywords = serp_context.get("top_keywords", [])
            keywords.extend(serp_keywords[:5])
        
        h2_count = tone_guide.get("seo_rules", {}).get("h2_count", 6)
        h3_per_h2 = tone_guide.get("seo_rules", {}).get("h3_per_h2", 2)
        
        prompt = f"""당신은 SEO 최적화 블로그 글 구조 설계 전문가입니다.
주어진 주제에 대해 검색 엔진 최적화된 글 구조를 생성하세요.

# 글 정보
- Day: {day_num}
- 제목: {title}
- 카테고리: {category}
- 키워드: {', '.join(keywords[:10])}

# 구조 생성 규칙
- H2 개수: {h2_count}개
- H2당 H3: {h3_per_h2}개
- 표(Table) 1개: 비교/요약용
- 리스트 1개: 체크리스트/단계별
- FAQ 3개: 실제 검색 의도 기반

# 출력 형식 (JSON)
{{
  "seo_title": "48~58자, 키워드 앞배치, 숫자 포함",
  "meta_description": "110~150자, 행동 유도 포함",
  "h1": "메인 제목",
  "sections": [
    {{
      "h2": "H2 제목 (질문형/숫자형)",
      "h3_list": ["H3-1", "H3-2"],
      "content_outline": "이 섹션에서 다룰 내용 개요 1~2문장"
    }}
  ],
  "table": {{
    "title": "표 제목",
    "headers": ["열1", "열2", "열3"],
    "rows": [
      ["데이터1-1", "데이터1-2", "데이터1-3"],
      ["데이터2-1", "데이터2-2", "데이터2-3"]
    ],
    "insert_after_section": 2
  }},
  "checklist": {{
    "title": "체크리스트/리스트 제목",
    "items": ["항목1", "항목2", "항목3", "항목4", "항목5"],
    "insert_after_section": 3
  }},
  "faq": [
    {{
      "question": "실제 검색될 만한 질문",
      "answer_outline": "답변 개요 1문장"
    }},
    {{
      "question": "질문2",
      "answer_outline": "답변 개요"
    }},
    {{
      "question": "질문3",
      "answer_outline": "답변 개요"
    }}
  ],
  "internal_links": [
    {{
      "anchor_text": "관련 글 링크 텍스트",
      "target_day": 5,
      "insert_after_section": 1
    }}
  ],
  "image_prompts": [
    {{
      "position": "thumbnail",
      "prompt": "DSLR 스타일 이미지 프롬프트",
      "alt_text": "SEO 최적화 ALT 텍스트"
    }},
    {{
      "position": "section_2",
      "prompt": "이미지 프롬프트",
      "alt_text": "ALT 텍스트"
    }}
  ]
}}

위 JSON 형식으로만 출력하세요. 추가 설명 없이 JSON만 출력하세요."""

        response = self.gpt.chat(prompt, max_tokens=2000)
        
        # JSON 파싱
        try:
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            structure = json.loads(json_str)
            logger.info(f"   ✅ 구조 생성 완료 (H2 {len(structure.get('sections', []))}개)")
            return structure
        except Exception as e:
            logger.error(f"❌ 구조 JSON 파싱 실패: {e}")
            return self._get_default_structure(title, h2_count)
    
    def _get_default_structure(self, title: str, h2_count: int = 6) -> Dict[str, Any]:
        """구조 생성 실패 시 기본값"""
        return {
            "seo_title": title[:55],
            "meta_description": f"{title}에 대한 완벽한 가이드입니다. 지금 바로 확인하세요!",
            "h1": title,
            "sections": [
                {
                    "h2": f"섹션 {i+1}",
                    "h3_list": [f"소주제 {i+1}-1", f"소주제 {i+1}-2"],
                    "content_outline": "내용 개요"
                }
                for i in range(h2_count)
            ],
            "table": {
                "title": "비교표",
                "headers": ["항목", "내용"],
                "rows": [["예시1", "설명1"], ["예시2", "설명2"]],
                "insert_after_section": 2
            },
            "checklist": {
                "title": "체크리스트",
                "items": ["항목1", "항목2", "항목3"],
                "insert_after_section": 3
            },
            "faq": [
                {"question": "질문1", "answer_outline": "답변"},
                {"question": "질문2", "answer_outline": "답변"},
                {"question": "질문3", "answer_outline": "답변"}
            ],
            "internal_links": [],
            "image_prompts": [
                {
                    "position": "thumbnail",
                    "prompt": "밝고 따뜻한 가족 이미지",
                    "alt_text": title
                }
            ]
        }
    
    def _write_content(
        self,
        day_num: int,
        day_plan: Dict[str, Any],
        structure: Dict[str, Any],
        tone_guide: Dict[str, Any],
        serp_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Claude를 사용하여 실제 본문 작성 (고품질)
        """
        title = day_plan.get("title", "")
        category = day_plan.get("category", "")
        
        # 톤 가이드 추출
        personality = tone_guide.get("tone_guide", {}).get("personality", "친근하고 공감하는")
        voice = tone_guide.get("tone_guide", {}).get("voice", "1인칭")
        opening_pattern = tone_guide.get("structure_template", {}).get("opening", {}).get("pattern", "")
        closing_pattern = tone_guide.get("structure_template", {}).get("closing", {}).get("pattern", "")
        paragraph_rule = tone_guide.get("writing_rules", {}).get("paragraph_spacing", "2~3줄마다 공백")
        optimal_length = tone_guide.get("content_length", {}).get("optimal", 1800)
        
        # SERP 인사이트
        serp_insight = ""
        if serp_context:
            top_keywords = serp_context.get("top_keywords", [])[:5]
            if top_keywords:
                serp_insight = f"\n\n# SERP 인기 키워드\n{', '.join(top_keywords)}"
        
        prompt = f"""당신은 네이버 블로그 SEO 최적화 전문 작가입니다.
주어진 구조에 맞춰 독자가 끝까지 읽고 싶어하는 고품질 블로그 글을 작성하세요.

# 글 정보
- Day: {day_num}
- 제목: {title}
- 카테고리: {category}
- 목표 글자 수: {optimal_length}자{serp_insight}

# 문체·톤 가이드
- 성격: {personality}
- 음성: {voice}
- 오프닝: {opening_pattern}
- 마무리: {closing_pattern}
- 단락 규칙: {paragraph_rule}

# 글 구조 (반드시 따를 것)
{json.dumps(structure, ensure_ascii=False, indent=2)}

# 작성 규칙
1. **오프닝** (80~120자)
   - 개인 경험으로 공감 유도
   - 자연스럽게 문제 제기
   - 독자의 호기심 자극

2. **본문** (각 섹션)
   - H2마다 이모지 1개 사용
   - 80~140자 단락, 3~4문장
   - 핵심 키워드 자연스럽게 배치
   - 구체적 예시/수치 포함
   - 표는 insert_after_section 위치에 삽입
   - 리스트도 지정 위치에 삽입

3. **FAQ** (본문 마지막)
   - 3개 질문과 간결한 답변
   - 검색 의도 충족

4. **마무리** (60~100자)
   - 핵심 요약 1문장
   - 행동 유도 (CTA)
   - 다음 글 예고 (선택)

5. **내부 링크**
   - 관련 Day 글 자연스럽게 연결
   - "이전에 소개한 [링크] 글도 참고하세요"

# 출력 형식 (JSON)
{{
  "day": {day_num},
  "title": "{title}",
  "seo_title": "구조의 seo_title 그대로",
  "meta_description": "구조의 meta_description 그대로",
  "h1": "구조의 h1 그대로",
  "opening": "오프닝 전체 텍스트 (80~120자)",
  "sections": [
    {{
      "h2": "구조의 H2 그대로",
      "h2_emoji": "📌",
      "h3_contents": [
        {{
          "h3": "구조의 H3 그대로",
          "paragraphs": [
            "단락1 텍스트 (80~140자)",
            "단락2 텍스트",
            "단락3 텍스트"
          ]
        }}
      ]
    }}
  ],
  "table_html": "구조의 표를 HTML로 변환 (<table>...</table>)",
  "checklist_html": "구조의 리스트를 HTML로 변환 (<ul><li>...</li></ul>)",
  "faq": [
    {{
      "question": "구조의 질문",
      "answer": "완성된 답변 (2~3문장)"
    }}
  ],
  "closing": "마무리 전체 텍스트 (60~100자)",
  "internal_links": [
    {{
      "anchor_text": "링크 텍스트",
      "target_day": 5,
      "context": "링크 주변 문맥"
    }}
  ],
  "word_count": 1800,
  "keywords_used": ["키워드1", "키워드2", "키워드3"]
}}

위 JSON 형식으로만 출력하세요. 추가 설명 없이 JSON만 출력하세요.
반드시 {optimal_length}자 내외로 작성하세요."""

        response = self.claude.chat(
            prompt=prompt,
            task_type="creative",
            max_tokens=4000
        )
        
        # JSON 파싱
        try:
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            content = json.loads(json_str)
            
            # 전체 텍스트 조합 (검증용)
            full_text = content.get("opening", "")
            for section in content.get("sections", []):
                for h3_content in section.get("h3_contents", []):
                    full_text += " ".join(h3_content.get("paragraphs", []))
            full_text += content.get("closing", "")
            
            content["full_text"] = full_text
            content["full_text_length"] = len(full_text)
            
            logger.info(f"   ✅ 본문 작성 완료 ({len(full_text)}자)")
            return content
        except Exception as e:
            logger.error(f"❌ 본문 JSON 파싱 실패: {e}")
            logger.error(f"응답: {response[:300]}")
            return self._get_default_content(day_num, title, structure)
    
    def _get_default_content(
        self, 
        day_num: int, 
        title: str, 
        structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """본문 생성 실패 시 기본값"""
        return {
            "day": day_num,
            "title": title,
            "seo_title": structure.get("seo_title", title),
            "meta_description": structure.get("meta_description", ""),
            "h1": structure.get("h1", title),
            "opening": "이 글에서는 중요한 정보를 소개합니다.",
            "sections": [
                {
                    "h2": section.get("h2", ""),
                    "h2_emoji": "📌",
                    "h3_contents": [
                        {
                            "h3": h3,
                            "paragraphs": [
                                "내용을 작성 중입니다.",
                                "자세한 내용은 곧 업데이트됩니다."
                            ]
                        }
                        for h3 in section.get("h3_list", [])
                    ]
                }
                for section in structure.get("sections", [])
            ],
            "table_html": "<table><tr><td>내용</td></tr></table>",
            "checklist_html": "<ul><li>항목1</li></ul>",
            "faq": structure.get("faq", []),
            "closing": "도움이 되셨기를 바랍니다!",
            "internal_links": [],
            "word_count": 500,
            "keywords_used": [],
            "full_text": "기본 텍스트",
            "full_text_length": 500
        }


if __name__ == "__main__":
    import sys
    import os
    
    # 입력 파일 로드
    try:
        with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
            pipeline_result = json.load(f)
            content_plan = pipeline_result.get("content_plan", [])
            serp_result = pipeline_result.get("serp_result", {})
    except FileNotFoundError:
        logger.error("❌ outputs/initial_pipeline_result.json 파일이 없습니다.")
        sys.exit(1)
    
    try:
        with open("outputs/tone_style_guide.json", "r", encoding="utf-8") as f:
            tone_guide = json.load(f)
    except FileNotFoundError:
        logger.error("❌ outputs/tone_style_guide.json 파일이 없습니다.")
        logger.error("   먼저 python -m nodes.tone_style_generator_node를 실행하세요.")
        sys.exit(1)
    
    # 생성 옵션
    print("\n" + "="*80)
    print("📝 SEO 콘텐츠 자동 생성")
    print("="*80)
    print(f"\n총 {len(content_plan)}일 계획이 있습니다.")
    print("\n옵션을 선택하세요:")
    print("  1. 전체 생성 (Day 1~30)")
    print("  2. 범위 지정 (예: Day 1~5)")
    print("  3. 단일 Day (예: Day 1)")
    
    choice = input("\n선택 (1/2/3, 기본값=3): ").strip() or "3"
    
    start_day = 1
    end_day = 1
    
    if choice == "1":
        start_day = 1
        end_day = len(content_plan)
    elif choice == "2":
        start_input = input("시작 Day (기본값=1): ").strip() or "1"
        end_input = input(f"종료 Day (기본값={min(5, len(content_plan))}): ").strip() or str(min(5, len(content_plan)))
        start_day = int(start_input)
        end_day = int(end_input)
    else:  # choice == "3"
        day_input = input("생성할 Day (기본값=1): ").strip() or "1"
        start_day = end_day = int(day_input)
    
    # 비용/시간 예측
    count = end_day - start_day + 1
    estimated_cost = count * 35  # ₩35/글
    estimated_time = count * 30  # 30초/글
    
    print(f"\n📊 예상 정보:")
    print(f"   - 생성 개수: {count}개")
    print(f"   - 예상 비용: ₩{estimated_cost}")
    print(f"   - 예상 시간: {estimated_time}초 ({estimated_time//60}분 {estimated_time%60}초)")
    
    confirm = input(f"\n계속하시겠습니까? (y/n, 기본값=y): ").strip().lower() or "y"
    if confirm != "y":
        print("취소되었습니다.")
        sys.exit(0)
    
    # 생성 실행
    writer = SEOContentWriterNode()
    results = writer.generate_all(
        content_plan=content_plan,
        tone_guide=tone_guide,
        serp_context=serp_result,
        start_day=start_day,
        end_day=end_day
    )
    
    # 저장
    output_dir = "outputs/content"
    os.makedirs(output_dir, exist_ok=True)
    
    for content in results:
        day_num = content.get("day", 0)
        output_path = os.path.join(output_dir, f"day{day_num:02d}_content.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Day {day_num} 저장: {output_path}")
    
    # 요약 저장
    summary = {
        "generated_at": "2025-11-14",
        "total_count": len(results),
        "start_day": start_day,
        "end_day": end_day,
        "total_cost_krw": estimated_cost,
        "files": [f"day{c.get('day', 0):02d}_content.json" for c in results]
    }
    
    summary_path = os.path.join(output_dir, "generation_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*80)
    print("✅ SEO 콘텐츠 생성 완료!")
    print("="*80)
    print(f"\n📁 저장 위치: {output_dir}/")
    print(f"📊 총 {len(results)}개 파일 생성")
    print(f"\n다음 단계: python -m nodes.image_planner_node")
