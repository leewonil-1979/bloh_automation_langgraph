"""
전체 파이프라인 실행 스크립트
Step 0-0: 아이디어 구체화 (GPT+Claude 하이브리드)
Step 0-1: 아이디어 확장
Step 0-2: 주제 스코어링
Step 1: 플랫폼 추천
Step 2-1: SERP 크롤링
Step 2-2: 30일 콘텐츠 계획
"""

from initial_pipeline import run_initial_pipeline
import json


def main():
    """전체 파이프라인 실행"""
    
    print("\n" + "="*80)
    print("🚀 블로그 자동화 시스템 - 전체 파이프라인")
    print("="*80)
    print("\n이 파이프라인은 다음 단계를 실행합니다:")
    print("  Step 0-0: 💬 아이디어 구체화 (GPT+Claude 하이브리드 대화형)")
    print("  Step 0-1: 🌱 아이디어 확장 (6-12개 주제 생성)")
    print("  Step 0-2: 📊 주제 스코어링 (수익성/확장성/지속성/난이도)")
    print("  Step 1:   📱 플랫폼 추천 (네이버/티스토리 등)")
    print("  Step 2-1: 🔍 SERP 크롤링 (상위 30개 블로그 분석)")
    print("  Step 2-2: 📅 30일 콘텐츠 계획 (로테이션 가능 글감)")
    print()
    
    # 사용자 입력
    user_idea = input("💡 블로그 아이디어를 입력하세요: ").strip()
    
    if not user_idea:
        user_idea = "4인 가족 여행 블로그"
        print(f"\n⚠️  입력이 없어 기본값을 사용합니다: '{user_idea}'")
    
    # 모드 선택
    print("\n" + "="*80)
    print("📋 실행 모드 선택")
    print("="*80)
    print("1. 대화형 모드 (권장) - AI가 질문하고 사용자가 답변")
    print("2. 자동 모드 (빠름) - 대화형 구체화 건너뛰기")
    
    mode = input("\n선택 (1/2, 기본값=1): ").strip()
    
    skip_refinement = (mode == "2")
    
    if skip_refinement:
        print("\n⚡ 자동 모드로 실행합니다 (대화형 구체화 건너뛰기)")
    else:
        print("\n💬 대화형 모드로 실행합니다")
        print("   💡 팁: 답변 시 '충분'이라고 입력하면 대화를 조기 종료할 수 있습니다.")
    
    print("\n" + "="*80)
    input("엔터를 눌러 시작하세요...")
    print()
    
    # 파이프라인 실행
    try:
        result = run_initial_pipeline(user_idea, skip_refinement=skip_refinement)
        
        # 결과 요약 출력
        print("\n" + "="*80)
        print("📊 실행 결과 요약")
        print("="*80)
        
        # 아이디어 구체화 결과
        if result.get("refined_idea_result"):
            refined = result["refined_idea_result"]
            details = refined.get("extracted_details", {})
            
            print("\n✨ 구체화된 아이디어:")
            print(f"  핵심 주제: {details.get('main_topic', 'N/A')}")
            print(f"  타겟 독자: {details.get('target_audience', 'N/A')}")
            
            platform = details.get('recommended_platform', {})
            print(f"\n📱 추천 플랫폼:")
            print(f"  메인: {platform.get('primary', 'N/A')}")
            print(f"  보조: {', '.join(platform.get('secondary', []))}")
            
            evergreen = details.get('evergreen_strategy', {})
            print(f"\n♻️  에버그린 전략:")
            for i, topic in enumerate(evergreen.get('rotation_topics', []), 1):
                print(f"  {i}. {topic}")
            
            monetization = details.get('monetization_strategy', {})
            print(f"\n💰 수익화:")
            print(f"  방법: {', '.join(monetization.get('methods', []))}")
            print(f"  잠재력: {monetization.get('potential', 'N/A')}")
        
        # 선정된 주제
        selected = result.get("scored_topics", {}).get("selected_topic", {})
        print(f"\n🎯 최종 선정 주제:")
        print(f"  {selected.get('title', 'N/A')}")
        print(f"  총점: {selected.get('total_score', 0)}점")
        
        # 플랫폼
        platform_rec = result.get("platform_recommendation", {})
        print(f"\n📱 플랫폼 전략:")
        print(f"  메인: {platform_rec.get('primary_platform', 'N/A')}")
        print(f"  콘텐츠 형식: {platform_rec.get('strategy', {}).get('content_format', 'N/A')}")
        print(f"  포스팅 빈도: {platform_rec.get('strategy', {}).get('posting_frequency', 'N/A')}")
        
        # SERP 결과
        serp = result.get("serp_data", {})
        print(f"\n🔍 SERP 분석:")
        print(f"  수집된 블로그: {serp.get('total_results', 0)}개")
        print(f"  최근글: {serp.get('total_recent_posts', 0)}개")
        print(f"  인기글: {serp.get('total_popular_posts', 0)}개")
        
        # 30일 계획
        plan = result.get("content_plan", {}).get("30_days_plan", [])
        print(f"\n📅 30일 콘텐츠 계획:")
        print(f"  총 {len(plan)}개 글감 생성")
        
        # 카테고리별 분포
        categories = {}
        for item in plan:
            cat = item.get('category', '기타')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n  카테고리별 분포:")
        for cat, count in categories.items():
            print(f"    {cat}: {count}개")
        
        print("\n" + "="*80)
        print("✅ 전체 파이프라인 완료!")
        print("="*80)
        print(f"\n💾 상세 결과: outputs/initial_pipeline_result.json")
        print("\n다음 단계:")
        print("  - python test_hybrid_writing.py 실행하여 블로그 글 작성 테스트")
        print("  - python batch_generate_posts.py 실행하여 30개 포스트 일괄 생성")
        print()
        
        return result
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자가 중단했습니다.")
        return None
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
