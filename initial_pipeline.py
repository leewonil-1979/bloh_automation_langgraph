# initial_pipeline.py
"""
초기 단계 파이프라인
아이디어 → 주제 선정 → 플랫폼 추천 → 30일 글감 생성
"""

import json
from nodes.idea_refiner_node import IdeaRefinerNode
from nodes.idea_expander_node import IdeaExpanderNode
from nodes.topic_scorer_node import TopicScorerNode
from nodes.platform_recommender_node import PlatformRecommenderNode
from nodes.serp_crawler_node import SERPCrawlerNode
from nodes.content_planner_node import ContentPlannerNode
from utils.logger import get_logger

logger = get_logger("InitialPipeline")


def run_initial_pipeline(user_idea: str, skip_refinement: bool = False) -> dict:
    """
    초기 파이프라인 실행
    
    Args:
        user_idea: 사용자 아이디어 (예: "블로그 자동화", "부동산 투자")
        skip_refinement: True면 대화형 구체화 과정 건너뛰기 (빠른 테스트용)
    
    Returns:
        전체 파이프라인 결과
    """
    
    print("=" * 80)
    print("🚀 블로그 자동화 시스템 - 초기 단계 파이프라인")
    print("=" * 80)
    print()
    
    # Step 0-0: 아이디어 구체화 (대화형 티키타카)
    refined_result = None
    if not skip_refinement:
        print("📌 Step 0-0: 아이디어 구체화 (대화형 티키타카)...")
        print()
        refiner = IdeaRefinerNode()
        refined_result = refiner.refine_interactive(user_idea, auto_mode=False)
        
        # 구체화된 아이디어 사용
        user_idea = refined_result["refined_idea"]
        print()
        print(f"✅ 아이디어 구체화 완료 (총 {len(refined_result['conversation_history'])}번의 질문)")
        print()
    else:
        print("⚠️  아이디어 구체화 과정을 건너뜁니다.")
        print()
    
    # Step 0-1: 아이디어 확장
    print("📌 Step 0-1: 아이디어 확장 중...")
    step0_1 = IdeaExpanderNode()
    expanded_topics = step0_1.expand(user_idea)
    
    print(f"✅ {len(expanded_topics.get('topics', []))}개의 주제 후보 생성 완료")
    print()
    
    # 생성된 주제 미리보기
    print("📋 생성된 주제 후보:")
    for topic in expanded_topics.get('topics', [])[:5]:
        print(f"  - {topic.get('title')}")
    if len(expanded_topics.get('topics', [])) > 5:
        print(f"  ... 외 {len(expanded_topics.get('topics', [])) - 5}개")
    print()
    
    # Step 0-2: 주제 스코어링 및 선정
    print("📌 Step 0-2: 주제 스코어링 및 최적 주제 선정 중...")
    step0_2 = TopicScorerNode()
    scored_result = step0_2.score_and_select(expanded_topics)
    
    selected = scored_result.get("selected_topic", {})
    print(f"✅ 최종 선정 주제: {selected.get('title')}")
    print(f"   총점: {selected.get('total_score')}점")
    print(f"   - 수익성: {selected.get('profitability_score')}")
    print(f"   - 확장성: {selected.get('scalability_score')}")
    print(f"   - 지속성: {selected.get('sustainability_score')}")
    print(f"   - 난이도: {selected.get('difficulty_score')}")
    print()
    
    # Step 1: 플랫폼 추천
    print("📌 Step 1: 최적 플랫폼 추천 중...")
    step1 = PlatformRecommenderNode()
    platform_result = step1.recommend(scored_result)
    
    primary = platform_result.get("primary_platform")
    secondary = platform_result.get("secondary_platforms", [])
    print(f"✅ 추천 플랫폼:")
    print(f"   메인: {primary}")
    print(f"   보조: {', '.join(secondary)}")
    print()
    
    strategy = platform_result.get("strategy", {})
    print(f"📊 추천 전략:")
    print(f"   콘텐츠 형식: {strategy.get('content_format')}")
    print(f"   포스팅 빈도: {strategy.get('posting_frequency')}")
    print(f"   수익화 방법: {strategy.get('monetization_method')}")
    print()
    
    # Step 2-1: SERP 크롤링
    print("📌 Step 2-1: 상위 블로그 수집 중...")
    step2_1 = SERPCrawlerNode()
    serp_result = step2_1.crawl(scored_result, platform=primary or "네이버 블로그")
    
    print(f"✅ {serp_result.get('total_results')}개 블로그 수집 완료")
    print()
    
    # Step 2-2: 30일 콘텐츠 계획
    print("📌 Step 2-2: 30일 콘텐츠 로테이션 생성 중...")
    step2_2 = ContentPlannerNode()
    content_plan = step2_2.plan(serp_result)
    
    plan_items = content_plan.get("30_days_plan", [])
    print(f"✅ 30일 콘텐츠 계획 생성 완료")
    print()
    
    # 샘플 글감 미리보기
    print("📅 30일 글감 미리보기 (1~7일):")
    for item in plan_items[:7]:
        day = item.get('day')
        title = item.get('title')
        content_type = item.get('content_type')
        print(f"   Day {day}: [{content_type}] {title}")
    if len(plan_items) > 7:
        print(f"   ... 외 {len(plan_items) - 7}일")
    print()
    
    # 전체 결과 저장
    final_result = {
        "user_idea": user_idea,
        "refined_idea_result": refined_result,  # 대화형 구체화 결과
        "expanded_topics": expanded_topics,
        "scored_topics": scored_result,
        "platform_recommendation": platform_result,
        "serp_data": serp_result,
        "content_plan": content_plan
    }
    
    # 결과를 파일로 저장
    output_file = "outputs/initial_pipeline_result.json"
    import os
    os.makedirs("outputs", exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print("=" * 80)
    print(f"💾 전체 결과 저장 완료: {output_file}")
    print("=" * 80)
    print()
    
    print("🎉 초기 단계 파이프라인 완료!")
    print()
    print("다음 단계:")
    print("  1. outputs/initial_pipeline_result.json 파일 확인")
    print("  2. 30일 계획 중 원하는 날짜 선택")
    print("  3. main_post_test.py 실행하여 실제 글 작성")
    print()
    
    return final_result


if __name__ == "__main__":
    # 사용 예시
    user_input = input("💡 아이디어를 입력하세요: ")
    
    if not user_input.strip():
        user_input = "블로그 자동화"
        print(f"(기본값 사용: {user_input})")
    
    # 대화형 구체화 건너뛰기 옵션
    skip = input("\n대화형 구체화를 건너뛰시겠습니까? (y/N): ").strip().lower()
    skip_refinement = (skip == 'y' or skip == 'yes')
    
    result = run_initial_pipeline(user_input, skip_refinement=skip_refinement)
