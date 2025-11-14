"""
아이디어 구체화 노드 테스트
대화형 티키타카 테스트
"""

from nodes.idea_refiner_node import IdeaRefinerNode
import json


def test_auto_mode():
    """자동 모드 테스트 (AI가 자동으로 답변 생성)"""
    print("\n" + "="*80)
    print("🤖 자동 모드 테스트 (AI가 질문과 답변 자동 생성)")
    print("="*80)
    
    refiner = IdeaRefinerNode()
    
    test_ideas = [
        "가족 여행 블로그",
        "반려동물 건강 관리",
        "부동산 투자 초보자 가이드"
    ]
    
    # 첫 번째 아이디어로 테스트
    idea = test_ideas[0]
    print(f"\n테스트 아이디어: {idea}\n")
    
    result = refiner.refine_interactive(idea, auto_mode=True)
    
    print("\n\n" + "="*80)
    print("📊 결과 저장")
    print("="*80)
    
    # 결과 저장
    output_file = "outputs/idea_refiner_test_auto.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 결과 저장 완료: {output_file}")
    
    return result


def test_interactive_mode():
    """대화형 모드 테스트 (실제 사용자 입력)"""
    print("\n" + "="*80)
    print("👤 대화형 모드 테스트 (실제 입력 받기)")
    print("="*80)
    
    refiner = IdeaRefinerNode()
    
    idea = input("\n💡 블로그 아이디어를 입력하세요: ").strip()
    if not idea:
        idea = "가족 여행 블로그"
        print(f"(기본값 사용: {idea})")
    
    print("\n💬 대화 중 언제든 '충분'이라고 입력하면 종료됩니다.\n")
    
    result = refiner.refine_interactive(idea, auto_mode=False)
    
    print("\n\n" + "="*80)
    print("📊 결과 저장")
    print("="*80)
    
    # 결과 저장
    output_file = "outputs/idea_refiner_test_interactive.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 결과 저장 완료: {output_file}")
    
    return result


if __name__ == "__main__":
    print("\n아이디어 구체화 노드 테스트")
    print("="*80)
    print("\n테스트 모드를 선택하세요:")
    print("1. 자동 모드 (AI가 질문과 답변 자동 생성)")
    print("2. 대화형 모드 (실제 사용자 입력)")
    
    choice = input("\n선택 (1/2, 기본값=1): ").strip()
    
    if choice == "2":
        result = test_interactive_mode()
    else:
        result = test_auto_mode()
    
    print("\n\n" + "="*80)
    print("🎉 테스트 완료!")
    print("="*80)
