"""
Image Alt Node
5️⃣ 이미지 기획 + ALT 생성
"""

from typing import Dict, Any, List
import pandas as pd


class ImageAltNode:
    """이미지 위치 기획 및 ALT 텍스트 생성"""
    
    def __init__(self):
        pass
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Image Alt 노드 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태 (이미지 계획)
        """
        print("🖼️ Image Alt Node 실행 중...")
        
        content = state.get("content", "")
        blog_config = state.get("blog_config", {})
        
        # 이미지 스타일 및 개수
        image_style = blog_config.get("image_style", "")
        image_count_range = blog_config.get("image_count", "3-5")
        
        # 이미지 계획 생성
        image_plan = self._generate_image_plan(content, image_style, image_count_range)
        
        state.update({
            "image_plan": image_plan
        })
        
        return state
    
    def _generate_image_plan(self, content: str, image_style: str, 
                            image_count_range: str) -> List[Dict[str, str]]:
        """이미지 기획 생성"""
        # TODO: AI를 사용한 이미지 기획
        
        # 샘플 이미지 계획
        image_plan = [
            {
                "position": 1,
                "description": f"Hero Image - {image_style}",
                "alt_text": "메인 히어로 이미지"
            },
            {
                "position": 2,
                "description": f"Diagram - {image_style}",
                "alt_text": "개념 설명 다이어그램"
            },
            {
                "position": 3,
                "description": f"Screenshot - {image_style}",
                "alt_text": "실제 사용 예시 스크린샷"
            }
        ]
        
        return image_plan
