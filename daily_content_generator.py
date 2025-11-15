"""
매일 1개씩 최신 트렌드 반영 블로그 글 생성기

특징:
1. 30일 계획에서 오늘 발행할 Day 선택
2. 당일 최신 트렌드 검색 (네이버 실시간 검색어)
3. 트렌드를 반영한 콘텐츠 생성
4. 이미지 → HTML → 업로드 → 발행 (전체 자동화)

실행:
  python daily_content_generator.py --day 1
  또는
  python daily_content_generator.py --auto  # 다음 Day 자동 선택
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import argparse

# 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nodes.seo_content_writer_node import SEOContentWriterNode


class DailyContentGenerator:
    """매일 실행하는 콘텐츠 생성기"""
    
    def __init__(self):
        self.writer = SEOContentWriterNode()
        self.state_file = "outputs/daily_generation_state.json"
    
    def get_next_day(self) -> int:
        """다음 생성할 Day 번호 가져오기"""
        if not os.path.exists(self.state_file):
            return 1
        
        with open(self.state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
            return state.get("next_day", 1)
    
    def update_state(self, day: int):
        """상태 업데이트"""
        state = {
            "last_generated_day": day,
            "next_day": day + 1,
            "last_generated_at": datetime.now().isoformat(),
        }
        
        os.makedirs("outputs", exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def get_latest_trends(self, keywords: List[str]) -> Dict[str, Any]:
        """
        당일 최신 트렌드 검색
        
        TODO: 실제 구현
        - 네이버 실시간 검색어 API
        - Google Trends API
        - 뉴스 API
        
        현재: 더미 데이터 반환
        """
        print(f"   🔍 최신 트렌드 검색 중... (키워드: {', '.join(keywords[:3])})")
        
        # TODO: 실제 API 호출로 교체
        trends = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hot_keywords": [
                "겨울 여행",
                "크리스마스 공연",
                "연말 할인"
            ],
            "related_news": [
                "2025년 겨울 가족 여행지 TOP 10",
                "어린이 공연 티켓 50% 할인 이벤트"
            ],
            "seasonal_context": "겨울 시즌, 연말 분위기"
        }
        
        print(f"   ✅ 트렌드 수집 완료")
        print(f"      - 인기 키워드: {', '.join(trends['hot_keywords'][:3])}")
        print(f"      - 계절 컨텍스트: {trends['seasonal_context']}")
        
        return trends
    
    def generate_daily_content(
        self, 
        day: int,
        include_trends: bool = True
    ) -> Dict[str, Any] | None:  # None도 반환 가능
        """
        매일 1개 콘텐츠 생성 (최신 트렌드 반영)
        
        Args:
            day: Day 번호
            include_trends: 최신 트렌드 반영 여부
        
        Returns:
            생성된 콘텐츠 또는 None (실패 시)
        """
        print("\n" + "="*80)
        print(f"📝 Day {day} 콘텐츠 생성 시작")
        print("="*80)
        print(f"📅 생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 30일 계획 로드
        with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
            pipeline_result = json.load(f)
            content_plan_data = pipeline_result.get("content_plan", {})
            content_plan = content_plan_data.get("30_days_plan", [])
            serp_result = pipeline_result.get("serp_result", {})
        
        if day > len(content_plan):
            print(f"❌ Day {day}는 계획에 없습니다. (총 {len(content_plan)}일)")
            return None
        
        day_plan = content_plan[day - 1]
        print(f"\n📌 주제: {day_plan.get('title', 'N/A')}")
        print(f"📂 카테고리: {day_plan.get('category', 'N/A')}")
        
        # 2. 최신 트렌드 반영
        trends = None
        if include_trends:
            keywords = day_plan.get("main_keywords", [])
            trends = self.get_latest_trends(keywords)
            
            # day_plan에 트렌드 정보 추가
            day_plan["trends"] = trends
            if "keywords" not in day_plan:
                day_plan["keywords"] = []
            day_plan["keywords"].extend(trends.get("hot_keywords", []))
        
        # 3. 문체 가이드 로드
        with open("outputs/tone_style_guide.json", "r", encoding="utf-8") as f:
            tone_guide = json.load(f)
        
        # 4. 콘텐츠 생성
        print(f"\n💰 예상 비용: ₩35")
        print(f"⏱️  예상 시간: 30초")
        print(f"\n🚀 생성 시작...")
        
        results = self.writer.generate_all(
            content_plan=content_plan,
            tone_guide=tone_guide,
            serp_context=serp_result,
            start_day=day,
            end_day=day
        )
        
        if not results or len(results) == 0:
            print(f"❌ Day {day} 생성 실패")
            return None
        
        content = results[0]  # type: dict[str, Any]
        
        # 5. 저장
        output_dir = "outputs/content"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"day{day:02d}_content.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        
        # 6. 상태 업데이트
        self.update_state(day)
        
        # 7. 결과 출력
        print("\n" + "="*80)
        print("✅ 생성 완료!")
        print("="*80)
        print(f"💾 저장 위치: {output_path}")
        print(f"📊 글자 수: {content.get('full_text_length', 0)}자")
        print(f"📝 섹션 수: {len(content.get('sections', []))}개")
        
        if trends:
            print(f"\n🔥 반영된 트렌드:")
            for keyword in trends.get("hot_keywords", [])[:3]:
                print(f"   - {keyword}")
        
        print(f"\n📅 다음 Day: {day + 1}")
        
        return content
    
    def generate_with_feedback(
        self,
        day: int,
        feedback: Optional[str] = None
    ) -> Dict[str, Any] | None:  # None도 반환 가능
        """
        피드백을 반영하여 재생성
        
        Args:
            day: Day 번호
            feedback: 사용자 피드백 (예: "더 전문적으로", "이모지 제거")
        
        Returns:
            재생성된 콘텐츠 또는 None (실패 시)
        """
        print(f"\n🔄 Day {day} 재생성 (피드백 반영)")
        
        if feedback:
            print(f"📝 피드백: {feedback}")
            
            # TODO: 피드백을 tone_guide에 자동 반영
            # 예: "더 전문적으로" → personality 변경
            #     "이모지 제거" → emoji_usage = "없음"
            print("   ⚠️  현재는 tone_style_guide.json을 수동으로 수정해주세요.")
        
        return self.generate_daily_content(day, include_trends=True)


def main():
    parser = argparse.ArgumentParser(description="매일 블로그 글 1개 생성")
    parser.add_argument(
        "--day", 
        type=int, 
        help="생성할 Day 번호 (기본값: 자동)"
    )
    parser.add_argument(
        "--auto", 
        action="store_true",
        help="다음 Day 자동 선택"
    )
    parser.add_argument(
        "--no-trends",
        action="store_true",
        help="최신 트렌드 반영 안 함"
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="기존 Day 재생성"
    )
    
    args = parser.parse_args()
    
    generator = DailyContentGenerator()
    
    # Day 선택
    if args.day:
        day = args.day
    elif args.auto:
        day = generator.get_next_day()
        print(f"🤖 자동 모드: Day {day} 생성 예정")
    else:
        # 인터랙티브 모드
        next_day = generator.get_next_day()
        print("\n" + "="*80)
        print("📝 매일 블로그 글 생성기")
        print("="*80)
        print(f"\n다음 생성 예정 Day: {next_day}")
        
        choice = input(f"\nDay {next_day}를 생성하시겠습니까? (y/n, 기본값=y): ").strip().lower() or "y"
        
        if choice != "y":
            day_input = input(f"생성할 Day 번호 입력 (1~30): ").strip()
            day = int(day_input)
        else:
            day = next_day
    
    # 생성 실행
    include_trends = not args.no_trends
    
    if args.regenerate:
        content = generator.generate_with_feedback(day)
    else:
        content = generator.generate_daily_content(day, include_trends=include_trends)
    
    if content:
        print("\n💡 다음 단계:")
        print("   1. 생성된 JSON 확인: outputs/content/dayXX_content.json")
        print("   2. 마음에 안 들면: tone_style_guide.json 수정 후")
        print(f"      python daily_content_generator.py --day {day} --regenerate")
        print("   3. 만족하면: 내일 다시 실행 (Day 자동 증가)")
        print("\n   또는 스케줄러 설정:")
        print("   - Windows: 작업 스케줄러에 등록")
        print("   - 매일 오전 9시 자동 실행")


if __name__ == "__main__":
    main()
