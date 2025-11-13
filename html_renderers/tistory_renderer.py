"""
Tistory Renderer
티스토리 블로그 전용 렌더링
"""

from typing import Dict, Any, Optional
from .base_renderer import BaseRenderer


class TistoryRenderer(BaseRenderer):
    """티스토리 블로그 최적화 렌더러"""
    
    def __init__(self, template_dir: str = "templates"):
        super().__init__(template_dir)
    
    def render(self, state: Dict[str, Any], template_name: Optional[str] = None) -> str:
        """티스토리용 HTML 생성"""
        if template_name is None:
            template_name = 'tistory_template.html'
            
        content = state.get('content', '')
        
        # 티스토리 특화 서식 적용
        formatted_content = self.apply_platform_specific_formatting(content)
        state['content'] = formatted_content
        
        return super().render(state, template_name)
    
    def apply_platform_specific_formatting(self, content: str) -> str:
        """티스토리 블로그 특화 서식"""
        # 코드 블록을 티스토리 스타일로 변환
        content = content.replace('<pre><code>', '<pre class="code-block"><code>')
        
        # 정보 박스 스타일 적용
        if '📌' in content or 'NOTE' in content.upper():
            content = content.replace('📌', '<div class="content-box">📌')
            content = content.replace('\n\n', '</div>\n\n')
        
        # 티스토리의 불필요한 p 마진 제거 클래스 적용
        content = f'<div class="tt-article-useless-p-margin">{content}</div>'
        
        return content
