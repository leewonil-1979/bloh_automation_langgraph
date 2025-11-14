# test_hybrid_writing.py
"""
GPT + Claude 협업 글쓰기 테스트
- 30일 계획 중 Day 1 선택
- 2-Stage 협업으로 실제 블로그 글 작성
"""

import json
from nodes.hybrid_post_writer_node import HybridPostWriterNode
from utils.logger import get_logger

logger = get_logger("HybridTest")


def load_plan():
    """30일 계획 로드"""
    with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["content_plan"]["30_days_plan"]


def load_serp():
    """SERP 데이터 로드"""
    with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["serp_data"]


def test_day1():
    """Day 1 글 작성 테스트"""
    print("=" * 80)
    print("🎨 GPT + Claude 협업 글쓰기 테스트")
    print("=" * 80)
    print()
    
    # 30일 계획 로드
    plan = load_plan()
    serp = load_serp()
    
    # Day 1 선택
    day1 = plan[0]
    print(f"📅 선택된 주제: Day {day1.get('day')}")
    print(f"📝 제목: {day1.get('title')}")
    print(f"🏷️ 카테고리: {day1.get('category')}")
    print(f"🔑 키워드: {', '.join(day1.get('main_keywords', []))}")
    print()
    
    # 협업 글쓰기 실행
    writer = HybridPostWriterNode()
    result = writer.write(day1, serp)
    
    # 결과 저장
    output_file = "outputs/hybrid_blog_post_day1.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 80)
    print(f"💾 결과 저장: {output_file}")
    print("=" * 80)
    print()
    
    # 미리보기
    print("📄 생성된 글 미리보기:")
    print("-" * 80)
    content = result.get("final_content", "")
    preview = content[:500] + "..." if len(content) > 500 else content
    print(preview)
    print("-" * 80)
    print()
    
    print(f"📊 통계:")
    print(f"  - 총 글자 수: {result.get('word_count')}자")
    print(f"  - Stage 1 모델: {result['metadata']['stage1_model']}")
    print(f"  - Stage 2 모델: {result['metadata']['stage2_model']}")
    print()
    
    # 뼈대도 출력
    print("📐 생성된 뼈대 (Skeleton):")
    print("-" * 80)
    skeleton = result.get("skeleton", {})
    outline = skeleton.get("outline", [])
    for section in outline:
        print(f"## {section.get('h2_title')}")
        if "h3_subsections" in section:
            for subsec in section["h3_subsections"]:
                print(f"  ### {subsec.get('h3_title')}")
    print("-" * 80)
    print()
    
    print("✅ 테스트 완료!")
    print()
    print("다음 단계:")
    print("  1. outputs/hybrid_blog_post_day1.json 파일 확인")
    print("  2. 글의 자연스러움, 구조, SEO 평가")
    print("  3. Day 2, 3... 순차 작성 또는 자동화")
    print()


if __name__ == "__main__":
    test_day1()
