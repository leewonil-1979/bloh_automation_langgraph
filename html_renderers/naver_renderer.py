"""
Naver Renderer
네이버 블로그 전용 렌더링
"""

from typing import Dict, Any, Optional
from .base_renderer import BaseRenderer


class NaverRenderer(BaseRenderer):
    """네이버 블로그 최적화 렌더러"""
    
    def __init__(self, template_dir: str = "templates"):
        super().__init__(template_dir)
    
    def render(self, state: Dict[str, Any], template_name: Optional[str] = None) -> str:
        """네이버 블로그용 HTML 생성"""
        if template_name is None:
            template_name = 'naver_template.html'
            
        # 네이버 전용 템플릿 사용
        content = state.get('content', '')
        
        # 네이버 블로그 특화 서식 적용
        formatted_content = self.apply_platform_specific_formatting(content)
        state['content'] = formatted_content
        
        return super().render(state, template_name)
    
    def apply_platform_specific_formatting(self, content: str) -> str:
        """네이버 블로그 특화 서식"""
        # 강조 텍스트를 하이라이트로 변환
        content = content.replace('<strong>', '<span class="highlight"><strong>')
        content = content.replace('</strong>', '</strong></span>')
        
        # TIP 박스 변환
        if '💡' in content or 'TIP' in content.upper():
            content = content.replace('💡', '<div class="tip-box">💡')
            # 문단 끝에 닫기 태그 추가 로직 (간단 구현)
            content = content.replace('\n\n', '</div>\n\n')
        
        return content
