"""
WordPress Renderer
워드프레스(.org) 전용 렌더링
"""

from typing import Dict, Any, Optional
from .base_renderer import BaseRenderer


class WordPressRenderer(BaseRenderer):
    """워드프레스 블로그 최적화 렌더러"""
    
    def __init__(self, template_dir: str = "templates"):
        super().__init__(template_dir)
    
    def render(self, state: Dict[str, Any], template_name: Optional[str] = None) -> str:
        """워드프레스용 HTML 생성"""
        if template_name is None:
            template_name = 'wordpress_template.html'
            
        content = state.get('content', '')
        
        # 워드프레스 특화 서식 적용
        formatted_content = self.apply_platform_specific_formatting(content)
        state['content'] = formatted_content
        
        return super().render(state, template_name)
    
    def apply_platform_specific_formatting(self, content: str) -> str:
        """워드프레스 블로그 특화 서식"""
        # 워드프레스 블록 에디터 스타일 적용
        
        # 이미지를 wp-block-image로 감싸기
        content = content.replace('<img', '<div class="wp-block-image"><img')
        content = content.replace('</img>', '</img></div>')
        content = content.replace('/>', '/></div>')  # 자기 닫기 태그 처리
        
        # 인용구를 워드프레스 스타일로
        content = content.replace('<blockquote>', '<blockquote class="wp-block-quote">')
        
        # 단락을 wp-block-paragraph로
        content = content.replace('<p>', '<p class="wp-block-paragraph">')
        
        return content
