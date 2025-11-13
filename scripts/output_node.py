"""
Output Node
6️⃣ HTML 완성 및 저장 (플랫폼별 렌더러 호출)
"""

from typing import Dict, Any
import os
import sys
import json
from datetime import datetime
import pandas as pd

# 렌더러 임포트
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from html_renderers import (
    NaverRenderer,
    TistoryRenderer,
    WordPressRenderer,
    BrunchRenderer,
    BaseRenderer
)


class OutputNode:
    """HTML 파일 및 메타데이터 저장 (플랫폼별 렌더링)"""
    
    def __init__(self, output_dir: str = "outputs", template_dir: str = "templates"):
        self.output_dir = output_dir
        self.template_dir = template_dir
        
        # 플랫폼별 렌더러 초기화
        self.renderers = {
            'naver': NaverRenderer(template_dir),
            'tistory': TistoryRenderer(template_dir),
            'wordpress': WordPressRenderer(template_dir),
            'brunch': BrunchRenderer(template_dir),
            'base': BaseRenderer(template_dir)
        }
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Output 노드 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태 (저장 경로)
        """
        print("💾 Output Node 실행 중...")
        
        blog_name = state.get("blog_name", "woncamp")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 출력 디렉토리 생성
        output_path = os.path.join(self.output_dir, today, blog_name)
        os.makedirs(output_path, exist_ok=True)
        
        # HTML 저장
        html_path = self._save_html(state, output_path)
        
        # 메타데이터 저장
        metadata_path = self._save_metadata(state, output_path)
        
        # 이미지 계획 저장
        image_plan_path = self._save_image_plan(state, output_path)
        
        state.update({
            "output_path": output_path,
            "html_path": html_path,
            "metadata_path": metadata_path,
            "image_plan_path": image_plan_path
        })
        
        print(f"✅ 저장 완료: {output_path}")
        
        return state
    
    def _save_html(self, state: Dict[str, Any], output_path: str) -> str:
        """플랫폼별 렌더러를 사용하여 HTML 저장"""
        # 플랫폼 정보 가져오기 (기본값: base)
        platform = state.get("platform", "base")
        
        # 해당 플랫폼의 렌더러 선택
        renderer = self.renderers.get(platform, self.renderers['base'])
        
        # 렌더링
        html = renderer.render(state)
        
        # 파일 확장자 결정 (브런치는 .md)
        extension = ".md" if platform == "brunch" else ".html"
        filename = f"post_{platform}{extension}"
        
        # 저장
        html_path = os.path.join(output_path, filename)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✓ {platform} 렌더링 완료: {filename}")
        
        return html_path
    
    def _save_metadata(self, state: Dict[str, Any], output_path: str) -> str:
        """메타데이터 JSON 저장"""
        metadata = {
            "title": state.get("title", ""),
            "tags": state.get("tags", []),
            "meta_description": state.get("meta_description", ""),
            "keywords": state.get("keywords", []),
            "created_at": datetime.now().isoformat()
        }
        
        metadata_path = os.path.join(output_path, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata_path
    
    def _save_image_plan(self, state: Dict[str, Any], output_path: str) -> str:
        """이미지 계획 CSV 저장"""
        image_plan = state.get("image_plan", [])
        
        if image_plan:
            df = pd.DataFrame(image_plan)
            image_plan_path = os.path.join(output_path, "image_plan.csv")
            df.to_csv(image_plan_path, index=False, encoding='utf-8-sig')
            return image_plan_path
        
        return ""
    
    def _get_default_template(self) -> str:
        """기본 HTML 템플릿"""
        return """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{meta_description}}">
    <meta name="keywords" content="{{tags}}">
    <title>{{title}}</title>
</head>
<body>
    <article>
        <h1>{{title}}</h1>
        <div class="content">
            {{content}}
        </div>
    </article>
</body>
</html>"""
