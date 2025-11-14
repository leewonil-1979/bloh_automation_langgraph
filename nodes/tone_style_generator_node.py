"""
Step 3: 문체·톤·스타일 확정 노드

SERP 상위 글을 분석하여 사용자 블로그의 일관된 문체와 톤을 확정합니다.

입력:
- SERP 크롤링 결과 (상위 5~10개 블로그 글)
- 사용자 선호도 (선택)

출력:
- tone_style_guide.json: 문체/톤/구조 가이드라인
"""

import json
import logging
from typing import Dict, Any, List, Optional
from utils.llm_client import HybridLLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToneStyleGeneratorNode:
    """문체·톤·스타일 확정 노드"""
    
    def __init__(self):
        self.llm = HybridLLMClient()
    
    def generate(
        self, 
        serp_result: Dict[str, Any],
        user_preferences: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        SERP 상위 글을 분석하여 문체·톤·스타일 가이드 생성
        
        Args:
            serp_result: SERP 크롤링 결과
            user_preferences: 사용자 선호도 (tone, length 등)
        
        Returns:
            문체·톤·스타일 가이드
        """
        logger.info("📝 Step 3: 문체·톤·스타일 확정 시작")
        
        # 1. SERP 상위 글 추출
        top_posts = self._extract_top_posts(serp_result)
        logger.info(f"   📊 상위 {len(top_posts)}개 글 분석 대상")
        
        # 2. 문체 패턴 분석 (Claude Analytical)
        style_analysis = self._analyze_writing_style(top_posts)
        logger.info("   ✅ 문체 패턴 분석 완료")
        
        # 3. 사용자 선호도 반영
        if user_preferences:
            style_analysis = self._merge_preferences(style_analysis, user_preferences)
            logger.info("   ✅ 사용자 선호도 반영 완료")
        
        # 4. 최종 가이드 생성
        tone_style_guide = self._generate_final_guide(style_analysis)
        logger.info("   ✅ 최종 문체·톤 가이드 생성 완료")
        
        return tone_style_guide
    
    def _extract_top_posts(self, serp_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """SERP 결과에서 상위 5~10개 글 추출"""
        blogs = serp_result.get("blogs", [])
        top_posts = []
        
        for blog in blogs[:10]:  # 최대 10개
            recent = blog.get("recent_posts", [])
            popular = blog.get("popular_posts", [])
            
            # 최근글 + 인기글 중 내용이 있는 것만
            for post in recent + popular:
                if post.get("content") and len(post["content"]) > 100:
                    top_posts.append({
                        "title": post.get("title", ""),
                        "content": post["content"][:2000],  # 처음 2000자만
                        "type": "recent" if post in recent else "popular"
                    })
                    if len(top_posts) >= 10:
                        break
            
            if len(top_posts) >= 10:
                break
        
        return top_posts[:10]
    
    def _analyze_writing_style(self, top_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Claude를 사용하여 상위 글의 문체 패턴 분석
        """
        # 분석용 텍스트 준비
        analysis_text = "\n\n---\n\n".join([
            f"[글 {i+1}]\n제목: {post['title']}\n내용:\n{post['content']}"
            for i, post in enumerate(top_posts)
        ])
        
        prompt = f"""당신은 블로그 문체 분석 전문가입니다.
네이버 블로그 상위 노출 글들을 분석하여 성공적인 문체 패턴을 추출하세요.

# 분석 대상 글 ({len(top_posts)}개)
{analysis_text}

# 분석 항목
1. **전반적인 톤 (Tone)**
   - 친근한가, 전문적인가?
   - 격식체인가, 구어체인가?
   - 1인칭/2인칭/3인칭 주로 사용?

2. **문장 스타일**
   - 평균 문장 길이 (짧음/보통/긺)
   - 단락 구성 (몇 문장으로 구성?)
   - 이모티콘/이모지 사용 빈도

3. **구조적 패턴**
   - 오프닝: 어떻게 시작? (경험/질문/요약)
   - 본론: 어떤 구조? (리스트/스토리/단계별)
   - 마무리: 어떻게 끝? (요약/CTA/질문)

4. **SEO 최적화 패턴**
   - 키워드 배치 위치
   - 소제목(H2/H3) 개수와 패턴
   - 표/리스트 사용 빈도

5. **가독성 요소**
   - 강조 표현 방법 (굵게, 밑줄, 색상)
   - 공백/여백 사용
   - 시각적 요소 (아이콘, 구분선)

# 출력 형식 (JSON)
{{
  "tone": {{
    "personality": "친근하고 공감하는 / 전문적이고 신뢰감 있는",
    "formality": "구어체 / 격식체",
    "voice": "1인칭 / 2인칭 / 3인칭"
  }},
  "sentence_style": {{
    "length": "짧음(~20자) / 보통(20~40자) / 긺(40자~)",
    "paragraph_sentences": 2-4,
    "emoji_usage": "많음 / 보통 / 적음 / 없음"
  }},
  "structure": {{
    "opening_pattern": "개인 경험 공감 / 문제 제기 질문 / 정보 요약",
    "body_pattern": "리스트형 / 단계별 가이드 / 스토리텔링 / 비교 분석",
    "closing_pattern": "행동 유도(CTA) / 요약 정리 / 질문 던지기"
  }},
  "seo_elements": {{
    "h2_count": 5-7,
    "h3_count": 10-15,
    "keyword_density": "2-3%",
    "table_usage": true/false,
    "list_usage": true/false
  }},
  "readability": {{
    "emphasis_method": "굵게 / 색상 / 아이콘",
    "spacing": "많음 / 보통 / 적음",
    "visual_separators": "이모지 / 구분선 / 없음"
  }},
  "recommended_length": "1000~1500자 / 1500~2000자 / 2000~3000자",
  "key_success_factors": ["요인1", "요인2", "요인3"]
}}

위 JSON 형식으로만 출력하세요. 추가 설명 없이 JSON만 출력하세요."""

        response = self.llm.chat(
            prompt=prompt,
            task_type="analytical",
            max_tokens=2000
        )
        
        # JSON 파싱
        try:
            # JSON 블록 추출
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(json_str)
            return analysis
        except Exception as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            logger.error(f"응답: {response[:500]}")
            # 기본값 반환
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """분석 실패 시 기본값"""
        return {
            "tone": {
                "personality": "친근하고 공감하는",
                "formality": "구어체",
                "voice": "1인칭"
            },
            "sentence_style": {
                "length": "보통(20~40자)",
                "paragraph_sentences": 3,
                "emoji_usage": "보통"
            },
            "structure": {
                "opening_pattern": "개인 경험 공감",
                "body_pattern": "리스트형",
                "closing_pattern": "행동 유도(CTA)"
            },
            "seo_elements": {
                "h2_count": 6,
                "h3_count": 12,
                "keyword_density": "2-3%",
                "table_usage": True,
                "list_usage": True
            },
            "readability": {
                "emphasis_method": "굵게",
                "spacing": "보통",
                "visual_separators": "이모지"
            },
            "recommended_length": "1500~2000자",
            "key_success_factors": [
                "개인 경험 기반 공감",
                "실용적 정보 제공",
                "시각적 가독성"
            ]
        }
    
    def _merge_preferences(
        self, 
        analysis: Dict[str, Any], 
        preferences: Dict[str, str]
    ) -> Dict[str, Any]:
        """사용자 선호도 반영"""
        # 사용자가 지정한 항목 우선 적용
        if "tone" in preferences:
            analysis["tone"]["personality"] = preferences["tone"]
        if "length" in preferences:
            analysis["recommended_length"] = preferences["length"]
        if "formality" in preferences:
            analysis["tone"]["formality"] = preferences["formality"]
        
        return analysis
    
    def _generate_final_guide(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        분석 결과를 기반으로 실전 적용 가능한 가이드 생성
        """
        prompt = f"""당신은 블로그 글쓰기 가이드 전문가입니다.
SERP 상위 글 분석 결과를 바탕으로, 실제 글쓰기에 사용할 구체적인 가이드를 생성하세요.

# 분석 결과
{json.dumps(analysis, ensure_ascii=False, indent=2)}

# 생성할 가이드 (JSON 형식)
{{
  "tone_guide": {{
    "personality": "친근하고 공감하는",
    "voice": "1인칭 ('저', '제가') 사용, 독자와 함께하는 느낌",
    "formality": "구어체 중심, 딱딱하지 않게",
    "examples": [
      "❌ 나쁜 예: ...",
      "✅ 좋은 예: ..."
    ]
  }},
  "structure_template": {{
    "opening": {{
      "pattern": "개인 경험 1~2문장 → 공감 → 문제 제기",
      "length": "80~120자",
      "example": "예시 오프닝 문장"
    }},
    "body": {{
      "pattern": "3단 구성 (배경 → 핵심 정보 → 활용법)",
      "section_count": 5-7,
      "h2_pattern": "질문형 / 명사형 / 숫자형",
      "h3_pattern": "구체적 소주제",
      "paragraph_rule": "80~140자 단락, 3~4문장"
    }},
    "closing": {{
      "pattern": "요약 1문장 → 행동 유도 → 다음 글 예고",
      "length": "60~100자",
      "cta_examples": ["예시 CTA 문장1", "예시 CTA 문장2"]
    }}
  }},
  "writing_rules": {{
    "sentence_length": "20~40자 권장",
    "paragraph_spacing": "2~3줄마다 공백",
    "emoji_usage": "섹션별 1개 (오프닝, H2마다)",
    "emphasis": "핵심 키워드만 굵게",
    "list_format": "• 또는 1. 2. 3. 형식"
  }},
  "seo_rules": {{
    "title_format": "48~58자, 키워드 앞배치, 숫자 포함",
    "h2_count": 5-7,
    "h3_per_h2": 2-3,
    "keyword_placement": "첫 단락, 각 H2 시작, 마지막 단락",
    "internal_links": "본문 3~5개",
    "table_usage": "비교/요약 시 1개",
    "faq_count": 3
  }},
  "content_length": {{
    "min": 1500,
    "max": 2000,
    "optimal": 1800
  }},
  "visual_elements": {{
    "thumbnail": "밝고 따뜻한 색감, 가족 이미지",
    "section_images": "3~5개, 각 H2마다 1개",
    "alt_text_pattern": "키워드 + 구체적 설명"
  }},
  "monetization_hints": {{
    "affiliate_section": "본문 중간(3번째 H2) 또는 마지막",
    "cta_placement": "오프닝 하단, 본문 중간, 마무리",
    "product_mention": "자연스럽게 경험담 형식"
  }}
}}

위 JSON 형식으로만 출력하세요. 추가 설명 없이 JSON만 출력하세요."""

        response = self.llm.chat(
            prompt=prompt,
            task_type="creative",
            max_tokens=2500
        )
        
        # JSON 파싱
        try:
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            guide = json.loads(json_str)
            
            # 메타 정보 추가
            guide["_meta"] = {
                "generated_at": "2025-11-14",
                "based_on_serp": True,
                "analysis_version": "1.0"
            }
            
            return guide
        except Exception as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            logger.error(f"응답: {response[:500]}")
            return self._get_default_guide()
    
    def _get_default_guide(self) -> Dict[str, Any]:
        """가이드 생성 실패 시 기본값"""
        return {
            "tone_guide": {
                "personality": "친근하고 공감하는",
                "voice": "1인칭 ('저', '제가') 사용",
                "formality": "구어체 중심",
                "examples": [
                    "❌ 나쁜 예: 여행 계획을 수립하십시오.",
                    "✅ 좋은 예: 저도 처음엔 막막했는데요, 이렇게 해보니 훨씬 쉬웠어요!"
                ]
            },
            "structure_template": {
                "opening": {
                    "pattern": "개인 경험 → 공감 → 문제 제기",
                    "length": "80~120자",
                    "example": "작년 여름, 아이들과 제주도를 갔다가 준비 부족으로 고생한 적 있으신가요?"
                },
                "body": {
                    "pattern": "리스트형 + 경험담",
                    "section_count": 6,
                    "h2_pattern": "질문형/숫자형",
                    "h3_pattern": "구체적 소주제",
                    "paragraph_rule": "80~140자, 3~4문장"
                },
                "closing": {
                    "pattern": "요약 → CTA",
                    "length": "60~100자",
                    "cta_examples": [
                        "오늘 소개한 방법으로 여행 준비하시면 분명 즐거운 추억 만드실 거예요!",
                        "다음 글에서는 실제 후기를 공유할게요. 궁금하시죠?"
                    ]
                }
            },
            "writing_rules": {
                "sentence_length": "20~40자",
                "paragraph_spacing": "2~3줄마다 공백",
                "emoji_usage": "섹션별 1개",
                "emphasis": "핵심 키워드만 굵게",
                "list_format": "• 형식"
            },
            "seo_rules": {
                "title_format": "48~58자, 키워드 앞배치",
                "h2_count": 6,
                "h3_per_h2": 2,
                "keyword_placement": "첫 단락, 각 H2, 마지막 단락",
                "internal_links": "3~5개",
                "table_usage": "비교/요약 시 1개",
                "faq_count": 3
            },
            "content_length": {
                "min": 1500,
                "max": 2000,
                "optimal": 1800
            },
            "visual_elements": {
                "thumbnail": "밝고 따뜻한 색감",
                "section_images": "3~5개",
                "alt_text_pattern": "키워드 + 구체적 설명"
            },
            "monetization_hints": {
                "affiliate_section": "본문 중간",
                "cta_placement": "오프닝 하단, 마무리",
                "product_mention": "자연스럽게 경험담"
            },
            "_meta": {
                "generated_at": "2025-11-14",
                "based_on_serp": True,
                "analysis_version": "1.0"
            }
        }


if __name__ == "__main__":
    # 테스트 실행
    import sys
    
    # SERP 결과 로드
    try:
        with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
            pipeline_result = json.load(f)
            serp_result = pipeline_result.get("serp_result", {})
    except FileNotFoundError:
        logger.error("❌ outputs/initial_pipeline_result.json 파일이 없습니다.")
        logger.error("   먼저 run_full_pipeline.py를 실행하세요.")
        sys.exit(1)
    
    # 문체·톤 생성
    generator = ToneStyleGeneratorNode()
    
    # 사용자 선호도 (선택)
    preferences = {
        "tone": "친근하고 전문적인",
        "length": "1500~2000자",
        "formality": "구어체"
    }
    
    tone_style_guide = generator.generate(serp_result, preferences)
    
    # 저장
    import os
    os.makedirs("outputs", exist_ok=True)
    
    output_path = "outputs/tone_style_guide.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tone_style_guide, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n✅ 문체·톤 가이드 생성 완료!")
    logger.info(f"📁 저장 위치: {output_path}")
    logger.info(f"\n📊 생성된 가이드 요약:")
    logger.info(f"   - 톤: {tone_style_guide['tone_guide']['personality']}")
    logger.info(f"   - 음성: {tone_style_guide['tone_guide']['voice']}")
    logger.info(f"   - 글자 수: {tone_style_guide['content_length']['optimal']}자")
    logger.info(f"   - H2 개수: {tone_style_guide['seo_rules']['h2_count']}개")
    logger.info(f"\n다음 단계: python nodes/seo_content_writer_node.py")
