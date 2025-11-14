# test_claude_vs_gpt.py
"""
Claude vs GPT 성능 비교 테스트
- 같은 주제로 30일 콘텐츠 기획
- 품질 비교 (다양성, 창의성, 자연스러움)
"""

import json
from nodes.content_planner_node import ContentPlannerNode
from utils.llm_client import LLMClient, HybridLLMClient
from utils.logger import get_logger

logger = get_logger("AB_Test")


def load_serp_data():
    """기존 SERP 데이터 로드"""
    with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["serp_data"]


def test_gpt_only():
    """GPT-4o-mini만 사용한 기획"""
    print("=" * 80)
    print("🤖 TEST 1: GPT-4o-mini 단독 테스트")
    print("=" * 80)
    
    # GPT 전용 클라이언트로 임시 변경
    class GPTOnlyPlanner(ContentPlannerNode):
        def __init__(self):
            from utils.llm_client import LLMClient
            self.llm_gpt = LLMClient()  # GPT만 사용
        
        def plan(self, serp_data):
            """GPT로만 기획 생성"""
            logger.info("ContentPlannerNode: 30일 콘텐츠 계획 생성 시작 (GPT 전용)")
            
            serp_results = serp_data.get("serp_results", [])
            topic = serp_data.get("topic", "")
            
            prompt = self._build_prompt(topic, serp_results)
            
            try:
                raw = self.llm_gpt.chat(prompt, max_tokens=4500)
                parsed = self._safe_parse_json(raw)
                logger.info(f"ContentPlannerNode: 30일 계획 생성 완료 (GPT)")
                return parsed
            except Exception as e:
                logger.error(f"ContentPlannerNode 실패: {e}")
                raise
    
    serp_data = load_serp_data()
    planner = GPTOnlyPlanner()
    
    result = planner.plan(serp_data)
    
    # 결과 저장
    with open("outputs/ab_test_gpt.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("✅ GPT 테스트 완료 → outputs/ab_test_gpt.json")
    return result


def test_claude_preferred():
    """Claude 우선 사용한 기획"""
    print("=" * 80)
    print("🧠 TEST 2: Claude 3.5 Sonnet 우선 테스트")
    print("=" * 80)
    
    serp_data = load_serp_data()
    planner = ContentPlannerNode()  # HybridLLMClient 사용 (Claude 우선)
    
    result = planner.plan(serp_data)
    
    # 결과 저장
    with open("outputs/ab_test_claude.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("✅ Claude 테스트 완료 → outputs/ab_test_claude.json")
    return result


def compare_results(gpt_result, claude_result):
    """결과 비교 분석"""
    logger.info("=" * 80)
    logger.info("📊 결과 비교 분석")
    logger.info("=" * 80)
    
    gpt_plan = gpt_result.get("30_days_plan", [])
    claude_plan = claude_result.get("30_days_plan", [])
    
    print("\n📌 GPT-4o-mini 생성 결과 (첫 10개):")
    for i, item in enumerate(gpt_plan[:10], 1):
        print(f"  Day {item.get('day')}: [{item.get('category')}] {item.get('title')}")
    
    print("\n📌 Claude 3.5 Sonnet 생성 결과 (첫 10개):")
    for i, item in enumerate(claude_plan[:10], 1):
        print(f"  Day {item.get('day')}: [{item.get('category')}] {item.get('title')}")
    
    # 카테고리 분포 분석
    print("\n📊 카테고리 분포 비교:")
    
    def count_categories(plan):
        categories = {}
        for item in plan:
            cat = item.get('category', '기타')
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    gpt_cats = count_categories(gpt_plan)
    claude_cats = count_categories(claude_plan)
    
    print("\n  GPT 카테고리 분포:")
    for cat, count in gpt_cats.items():
        print(f"    {cat}: {count}개")
    
    print("\n  Claude 카테고리 분포:")
    for cat, count in claude_cats.items():
        print(f"    {cat}: {count}개")
    
    # 제목 키워드 반복성 분석
    print("\n📊 제목 다양성 분석:")
    
    def analyze_diversity(plan):
        titles = [item.get('title', '') for item in plan]
        # 가장 많이 반복되는 단어 찾기
        words = []
        for title in titles:
            words.extend(title.split())
        
        word_count = {}
        for word in words:
            if len(word) > 2:  # 2글자 이상만
                word_count[word] = word_count.get(word, 0) + 1
        
        # 상위 5개 반복 단어
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:5]
    
    gpt_top_words = analyze_diversity(gpt_plan)
    claude_top_words = analyze_diversity(claude_plan)
    
    print("\n  GPT 상위 반복 단어:")
    for word, count in gpt_top_words:
        print(f"    '{word}': {count}회")
    
    print("\n  Claude 상위 반복 단어:")
    for word, count in claude_top_words:
        print(f"    '{word}': {count}회")
    
    print("\n" + "=" * 80)
    print("🎯 평가 기준:")
    print("  1. 카테고리 균형: 6개 카테고리 × 5개씩 = 30개 달성 여부")
    print("  2. 제목 다양성: 같은 단어 반복 빈도 낮을수록 좋음")
    print("  3. 창의성: 실제 글 제목의 참신함 (수동 평가 필요)")
    print("=" * 80)


def main():
    """메인 테스트 실행"""
    print("=" * 80)
    print("🔬 Claude vs GPT A/B 테스트 시작")
    print("=" * 80)
    print()
    
    # 1. GPT 테스트
    gpt_result = test_gpt_only()
    print()
    
    # 2. Claude 테스트
    claude_result = test_claude_preferred()
    print()
    
    # 3. 결과 비교
    compare_results(gpt_result, claude_result)
    print()
    
    print("✅ 테스트 완료!")
    print()
    print("다음 단계:")
    print("  1. outputs/ab_test_gpt.json 확인")
    print("  2. outputs/ab_test_claude.json 확인")
    print("  3. 두 결과 비교 후 최종 선택")
    print()


if __name__ == "__main__":
    main()
