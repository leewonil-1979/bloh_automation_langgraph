"""
Strategy Node
2️⃣ 루프 + 문체/톤/지침 자동화
"""

from typing import Dict, Any
import yaml
import os


class StrategyNode:
    """블로그별 루프 및 문체 설정"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strategy 노드 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태 (루프, 문체 설정 등)
        """
        print("📝 Strategy Node 실행 중...")
        
        blog_name = state.get("blog_name", "woncamp")
        
        # 블로그 설정 로드
        config = self._load_blog_config(blog_name)
        
        state.update({
            "blog_config": config,
            "tone": config.get("tone"),
            "style": config.get("style"),
            "writing_loop": config.get("writing_loop"),
            "target_audience": config.get("target_audience")
        })
        
        return state
    
    def _load_blog_config(self, blog_name: str) -> Dict[str, Any]:
        """블로그 설정 파일 로드"""
        config_path = os.path.join(self.config_dir, f"{blog_name}.yaml")
        
        if not os.path.exists(config_path):
            print(f"⚠️ 설정 파일을 찾을 수 없습니다: {config_path}")
            return {}
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
