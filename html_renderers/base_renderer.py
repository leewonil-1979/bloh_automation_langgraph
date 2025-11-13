"""
Base Renderer
모든 플랫폼 렌더러의 기본 클래스
"""

from typing import Dict, Any, Optional
import os


class BaseRenderer:
    """기본 렌더러 클래스 - 공통 기능 제공"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
    
    def render(self, state: Dict[str, Any], template_name: Optional[str] = None) -> str:
        """
        템플릿을 사용하여 HTML 렌더링
        
        Args:
            state: 블로그 포스트 상태 정보
            template_name: 사용할 템플릿 파일명 (선택적)
            
        Returns:
            렌더링된 HTML 문자열
        """
        if template_name is None:
            return self._get_fallback_template(state)
        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.exists(template_path):
            return self._get_fallback_template(state)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 템플릿 변수 치환
        rendered = self._replace_variables(template, state)
        
        return rendered
    
    def _replace_variables(self, template: str, state: Dict[str, Any]) -> str:
        """템플릿 변수를 실제 값으로 치환"""
        replacements = {
            '{{title}}': state.get('title', ''),
            '{{meta_description}}': state.get('meta_description', ''),
            '{{content}}': state.get('content', ''),
            '{{tags}}': ', '.join(state.get('tags', [])),
            '{{created_at}}': state.get('created_at', '')
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, str(value))
        
        return result
    
    def _get_fallback_template(self, state: Dict[str, Any]) -> str:
        """템플릿이 없을 때 사용할 기본 HTML"""
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>{state.get('title', '')}</title>
</head>
<body>
    <h1>{state.get('title', '')}</h1>
    <div>{state.get('content', '')}</div>
</body>
</html>"""
    
    def apply_platform_specific_formatting(self, content: str) -> str:
        """
        플랫폼별 특수 서식 적용
        (서브클래스에서 오버라이드)
        """
        return content
