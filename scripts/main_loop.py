"""
Main Loop
전체 파이프라인 실행
"""

from typing import Dict, Any, Optional
from topic_refiner_node import TopicRefinerNode
from discovery_node import DiscoveryNode
from strategy_node import StrategyNode
from seo_writer_node import SEOWriterNode
from metadata_node import MetadataNode
from image_alt_node import ImageAltNode
from output_node import OutputNode
from scheduler_node import SchedulerNode
from osmu_node import OSMUNode


class BlogAutomationPipeline:
    """블로그 자동화 메인 파이프라인"""
    
    def __init__(self):
        self.topic_refiner = TopicRefinerNode()
        self.discovery = DiscoveryNode()
        self.strategy = StrategyNode()
        self.seo_writer = SEOWriterNode()
        self.metadata = MetadataNode()
        self.image_alt = ImageAltNode()
        self.output = OutputNode()
        self.scheduler = SchedulerNode()
        self.osmu = OSMUNode()
    
    def run(self, idea: str, blog_name: str = "woncamp", 
            platform: str = "base",
            schedule_time: Optional[str] = None) -> Dict[str, Any]:
        """
        전체 파이프라인 실행
        
        Args:
            idea: 블로그 아이디어
            blog_name: 블로그 이름 (woncamp, wonfinance, wonschool 등)
            platform: 플랫폼 (naver, tistory, wordpress, brunch, base)
            schedule_time: 예약 시간 (예: "14:30")
            
        Returns:
            최종 상태
        """
        print("=" * 60)
        print("🚀 블로그 자동화 파이프라인 시작")
        print("=" * 60)
        
        # 초기 상태
        state = {
            "idea": idea,
            "blog_name": blog_name,
            "platform": platform,
            "schedule_time": schedule_time
        }
        
        # 0. Topic Refiner (주제 정교화)
        state = self.topic_refiner.execute(state)
        
        # 1. Discovery
        state = self.discovery.execute(state)
        
        # 2. Strategy
        state = self.strategy.execute(state)
        
        # 3. SEO Writer
        state = self.seo_writer.execute(state)
        
        # 4. Metadata
        state = self.metadata.execute(state)
        
        # 5. Image Alt
        state = self.image_alt.execute(state)
        
        # 6. Output
        state = self.output.execute(state)
        
        # 7. OSMU
        state = self.osmu.execute(state)
        
        # 8. Scheduler
        state = self.scheduler.execute(state)
        
        print("=" * 60)
        print("✅ 블로그 자동화 파이프라인 완료")
        print("=" * 60)
        print(f"📁 출력 경로: {state.get('output_path')}")
        print(f"📄 HTML: {state.get('html_path')}")
        print(f"📋 메타데이터: {state.get('metadata_path')}")
        
        return state


def main():
    """메인 실행 함수"""
    # 예시 실행
    pipeline = BlogAutomationPipeline()
    
    # 아이디어 입력
    idea = "LangGraph를 활용한 AI 에이전트 개발 가이드"
    blog_name = "woncamp"
    platform = "tistory"  # naver, tistory, wordpress, brunch, base
    
    # 파이프라인 실행
    result = pipeline.run(
        idea=idea,
        blog_name=blog_name,
        platform=platform,
        schedule_time=None  # None이면 즉시 실행
    )
    
    print("\n🎉 완료!")


if __name__ == "__main__":
    main()
