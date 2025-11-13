"""
Brunch Renderer
브런치 마크다운 변환
"""

from typing import Dict, Any, Optional
from .base_renderer import BaseRenderer


class BrunchRenderer(BaseRenderer):
    """브런치 마크다운 렌더러"""
    
    def __init__(self, template_dir: str = "templates"):
        super().__init__(template_dir)
    
    def render(self, state: Dict[str, Any], template_name: Optional[str] = None) -> str:
        """브런치용 Markdown 생성"""
        if template_name is None:
            template_name = 'brunch_template.md'
            
        content = state.get('content', '')
        
        # HTML을 Markdown으로 변환
        markdown_content = self.html_to_markdown(content)
        state['content'] = markdown_content
        
        return super().render(state, template_name)
    
    def html_to_markdown(self, html_content: str) -> str:
        """HTML을 Markdown으로 간단 변환"""
        # 간단한 HTML -> Markdown 변환
        content = html_content
        
        # 헤더 변환
        content = content.replace('<h2>', '\n## ')
        content = content.replace('</h2>', '\n')
        content = content.replace('<h3>', '\n### ')
        content = content.replace('</h3>', '\n')
        
        # 강조 변환
        content = content.replace('<strong>', '**')
        content = content.replace('</strong>', '**')
        content = content.replace('<em>', '*')
        content = content.replace('</em>', '*')
        
        # 링크 변환
        # 간단한 정규식 대신 기본 치환
        content = content.replace('<a href="', '[')
        content = content.replace('">', '](')
        content = content.replace('</a>', ')')
        
        # 이미지 변환
        content = content.replace('<img src="', '![](')
        content = content.replace('" alt="', ')')
        
        # 리스트 변환
        content = content.replace('<ul>', '\n')
        content = content.replace('</ul>', '\n')
        content = content.replace('<li>', '- ')
        content = content.replace('</li>', '\n')
        
        # 단락 태그 제거
        content = content.replace('<p>', '\n')
        content = content.replace('</p>', '\n')
        
        return content
    
    def apply_platform_specific_formatting(self, content: str) -> str:
        """브런치 특화 서식"""
        # 브런치는 마크다운 기반이므로 특별한 서식 불필요
        return content
