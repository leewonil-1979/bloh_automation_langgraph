"""
아이디어 구체화 노드 자동 테스트 (개선된 버전)
- 플랫폼 추천 포함
- 30일 에버그린 전략 포함
"""

from nodes.idea_refiner_node import IdeaRefinerNode
import json


def test_auto_refined():
    """개선된 아이디어 구체화 자동 테스트"""
    print("\n" + "="*80)
    print("🤖 개선된 아이디어 구체화 자동 테스트")
    print("="*80)
    
    refiner = IdeaRefinerNode()
    
    # 테스트 아이디어
    idea = "4인 가족 아이들(미취학 ~중고등학생)과 함께 갈 수 있는 공연, 전시 등 소개하는 블로그"
    
    print(f"\n💡 테스트 아이디어: {idea}\n")
    
    # 자동 모드로 실행 (AI가 질문과 답변 자동 생성)
    result = refiner.refine_interactive(idea, auto_mode=True)
    
    print("\n\n" + "="*80)
    print("📊 결과")
    print("="*80)
    
    print(f"\n✅ 정교화된 아이디어:\n{result['refined_idea']}\n")
    
    print("\n📌 추출된 세부 정보:")
    details = result['extracted_details']
    
    # 주요 정보 출력
    print(f"\n🎯 핵심 주제: {details.get('main_topic', 'N/A')}")
    print(f"\n👥 타겟 독자: {details.get('target_audience', 'N/A')}")
    
    # 추천 플랫폼
    platform = details.get('recommended_platform', {})
    print(f"\n📱 추천 플랫폼:")
    print(f"   메인: {platform.get('primary', 'N/A')}")
    print(f"   이유: {platform.get('reason', 'N/A')}")
    print(f"   보조: {', '.join(platform.get('secondary', []))}")
    
    # 에버그린 전략
    evergreen = details.get('evergreen_strategy', {})
    print(f"\n♻️  30일 에버그린 전략:")
    print(f"   로테이션 소주제:")
    for topic in evergreen.get('rotation_topics', []):
        print(f"     - {topic}")
    print(f"   재활용 방법: {evergreen.get('reusability', 'N/A')}")
    
    # 수익화 전략
    monetization = details.get('monetization_strategy', {})
    print(f"\n💰 수익화 전략:")
    print(f"   방법: {', '.join(monetization.get('methods', []))}")
    print(f"   잠재력: {monetization.get('potential', 'N/A')}")
    print(f"   근거: {monetization.get('reason', 'N/A')}")
    
    # 결과 저장
    output_file = "outputs/idea_refiner_enhanced_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n💾 결과 저장: {output_file}")
    
    return result


if __name__ == "__main__":
    result = test_auto_refined()
    
    print("\n\n" + "="*80)
    print("🎉 테스트 완료!")
    print("="*80)
