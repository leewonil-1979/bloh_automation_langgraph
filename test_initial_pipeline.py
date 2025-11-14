# test_initial_pipeline.py
"""
초기 파이프라인 간단 테스트
"""

from initial_pipeline import run_initial_pipeline


def test_pipeline():
    """초기 파이프라인 테스트"""
    
    # 테스트 아이디어
    test_ideas = [
        "블로그 자동화",
        "부동산 투자",
        "건강한 식단",
        "영어 공부법"
    ]
    
    print("🧪 초기 파이프라인 테스트")
    print()
    print("사용 가능한 테스트 아이디어:")
    for i, idea in enumerate(test_ideas, 1):
        print(f"  {i}. {idea}")
    print()
    
    choice = input("테스트할 아이디어 번호를 선택하세요 (1-4, 엔터=1): ").strip()
    
    if not choice:
        choice = "1"
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(test_ideas):
            selected_idea = test_ideas[idx]
        else:
            print("잘못된 번호입니다. 기본값 사용")
            selected_idea = test_ideas[0]
    except ValueError:
        print("숫자를 입력하세요. 기본값 사용")
        selected_idea = test_ideas[0]
    
    print(f"\n선택된 아이디어: {selected_idea}")
    print()
    
    # 파이프라인 실행
    result = run_initial_pipeline(selected_idea)
    
    return result


if __name__ == "__main__":
    test_pipeline()
