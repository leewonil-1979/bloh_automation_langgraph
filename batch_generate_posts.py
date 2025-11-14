"""
30개 블로그 포스트 일괄 생성 스크립트
GPT+Claude 하이브리드 2단계 협업 글쓰기
"""

import json
import os
from datetime import datetime
from nodes.hybrid_post_writer_node import HybridPostWriterNode
from utils.logger import get_logger

logger = get_logger("BatchGenerator")


def load_content_plan(plan_file: str = "outputs/initial_pipeline_result.json"):
    """30일 콘텐츠 계획 로드"""
    
    if not os.path.exists(plan_file):
        raise FileNotFoundError(
            f"콘텐츠 계획 파일이 없습니다: {plan_file}\n"
            "먼저 'python run_full_pipeline.py'를 실행하세요."
        )
    
    with open(plan_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    content_plan = data.get("content_plan", {})
    plan_items = content_plan.get("30_days_plan", [])
    
    if not plan_items:
        raise ValueError("30일 계획이 비어있습니다.")
    
    return plan_items, data.get("serp_data", {})


def generate_batch_posts(
    start_day: int = 1, 
    end_day: int = 30,
    output_dir: str = "outputs/batch_posts"
):
    """
    배치로 블로그 포스트 생성
    
    Args:
        start_day: 시작 일자 (1~30)
        end_day: 종료 일자 (1~30)
        output_dir: 출력 디렉토리
    """
    
    print("\n" + "="*80)
    print("📝 30일 블로그 포스트 일괄 생성")
    print("="*80)
    print()
    
    # 콘텐츠 계획 로드
    print("📂 콘텐츠 계획 로드 중...")
    plan_items, serp_context = load_content_plan()
    print(f"✅ {len(plan_items)}개 글감 로드 완료")
    print()
    
    # 생성 범위 확인
    start_day = max(1, min(start_day, len(plan_items)))
    end_day = max(start_day, min(end_day, len(plan_items)))
    
    total_count = end_day - start_day + 1
    
    print(f"📅 생성 범위: Day {start_day} ~ Day {end_day} (총 {total_count}개)")
    print()
    
    # 예상 비용 계산
    cost_per_post = 35  # ₩35/포스트 (GPT ₩5 + Claude ₩30)
    total_cost = cost_per_post * total_count
    
    print(f"💰 예상 비용: ₩{total_cost:,} (₩{cost_per_post}/포스트)")
    print(f"⏱️  예상 시간: {total_count * 0.5:.1f}분 (30초/포스트)")
    print()
    
    # 확인
    confirm = input(f"계속 진행하시겠습니까? (Y/n): ").strip().lower()
    if confirm == 'n' or confirm == 'no':
        print("❌ 취소되었습니다.")
        return
    
    print()
    print("="*80)
    print("🚀 생성 시작!")
    print("="*80)
    print()
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 글쓰기 노드 초기화
    writer = HybridPostWriterNode()
    
    # 생성 결과 저장
    results = []
    successful = 0
    failed = 0
    
    # 각 포스트 생성
    for day in range(start_day, end_day + 1):
        plan_item = plan_items[day - 1]
        
        print(f"\n{'='*80}")
        print(f"📝 Day {day}/{len(plan_items)}: {plan_item.get('title', 'N/A')}")
        print(f"{'='*80}")
        
        try:
            # 글 작성 (GPT 뼈대 + Claude 살붙이기)
            result = writer.write(plan_item, serp_context)
            
            # 결과 저장
            output_file = os.path.join(output_dir, f"day{day:02d}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 요약 정보
            final_content = result.get("final_content", "")
            char_count = len(final_content)
            
            print(f"\n✅ 생성 완료!")
            print(f"   제목: {result.get('title', 'N/A')}")
            print(f"   카테고리: {result.get('category', 'N/A')}")
            print(f"   글자 수: {char_count:,}자")
            print(f"   키워드: {', '.join(result.get('keywords', [])[:3])}...")
            print(f"   저장: {output_file}")
            
            results.append({
                "day": day,
                "title": result.get("title"),
                "status": "success",
                "char_count": char_count,
                "file": output_file
            })
            
            successful += 1
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            logger.exception(f"Day {day} 생성 실패")
            
            results.append({
                "day": day,
                "title": plan_item.get("title"),
                "status": "failed",
                "error": str(e)
            })
            
            failed += 1
            
            # 연속 실패 시 중단
            if failed >= 3:
                print("\n⚠️  연속 3회 실패로 중단합니다.")
                break
    
    # 최종 결과
    print("\n" + "="*80)
    print("📊 생성 결과 요약")
    print("="*80)
    print(f"\n✅ 성공: {successful}개")
    print(f"❌ 실패: {failed}개")
    print(f"📁 출력 디렉토리: {output_dir}")
    
    # 통계
    if successful > 0:
        total_chars = sum(r.get("char_count", 0) for r in results if r["status"] == "success")
        avg_chars = total_chars / successful
        
        print(f"\n📈 통계:")
        print(f"   총 글자 수: {total_chars:,}자")
        print(f"   평균 글자 수: {avg_chars:,.0f}자/포스트")
        print(f"   실제 비용: 약 ₩{successful * cost_per_post:,}")
    
    # 요약 파일 저장
    summary_file = os.path.join(output_dir, "generation_summary.json")
    summary = {
        "generated_at": datetime.now().isoformat(),
        "range": f"Day {start_day} ~ Day {end_day}",
        "total_count": total_count,
        "successful": successful,
        "failed": failed,
        "results": results
    }
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 요약 저장: {summary_file}")
    print()
    
    return results


def main():
    """메인 함수"""
    
    print("\n블로그 포스트 일괄 생성 도구")
    print("="*80)
    print("\n옵션:")
    print("  1. 전체 생성 (Day 1~30)")
    print("  2. 범위 지정 생성")
    print("  3. 단일 생성 (1개만)")
    
    choice = input("\n선택 (1/2/3, 기본값=1): ").strip()
    
    if choice == "3":
        day = input("생성할 날짜 (1~30): ").strip()
        try:
            day = int(day)
            generate_batch_posts(start_day=day, end_day=day)
        except ValueError:
            print("❌ 잘못된 입력입니다.")
    
    elif choice == "2":
        start = input("시작 날짜 (1~30): ").strip()
        end = input("종료 날짜 (1~30): ").strip()
        try:
            start = int(start)
            end = int(end)
            generate_batch_posts(start_day=start, end_day=end)
        except ValueError:
            print("❌ 잘못된 입력입니다.")
    
    else:
        # 전체 생성
        generate_batch_posts(start_day=1, end_day=30)
    
    print("\n🎉 완료!")


if __name__ == "__main__":
    main()
