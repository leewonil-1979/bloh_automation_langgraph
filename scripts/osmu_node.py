"""
OSMU Node
8️⃣ One Source Multi Use 변환
"""

from typing import Dict, Any
import os


class OSMUNode:
    """블로그 내용을 다른 플랫폼용으로 변환"""
    
    def __init__(self):
        pass
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        OSMU 노드 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태 (OSMU 스크립트)
        """
        print("🔄 OSMU Node 실행 중...")
        
        content = state.get("content", "")
        blog_config = state.get("blog_config", {})
        osmu_platforms = blog_config.get("osmu_platforms", [])
        
        osmu_scripts = {}
        
        for platform in osmu_platforms:
            script = self._convert_to_platform(content, platform)
            osmu_scripts[platform] = script
        
        # OSMU 스크립트 저장
        output_path = state.get("output_path", "")
        if output_path:
            self._save_osmu_scripts(osmu_scripts, output_path)
        
        state.update({
            "osmu_scripts": osmu_scripts
        })
        
        return state
    
    def _convert_to_platform(self, content: str, platform: str) -> str:
        """플랫폼별 변환"""
        # TODO: AI를 사용한 플랫폼별 최적화
        
        if platform == "youtube":
            return self._to_youtube_script(content)
        elif platform == "instagram":
            return self._to_instagram_post(content)
        elif platform == "twitter":
            return self._to_twitter_thread(content)
        elif platform == "linkedin":
            return self._to_linkedin_post(content)
        elif platform == "medium":
            return self._to_medium_article(content)
        else:
            return content
    
    def _to_youtube_script(self, content: str) -> str:
        """YouTube 스크립트 변환"""
        return f"# YouTube Script\n\n{content[:500]}...\n\n[계속...]"
    
    def _to_instagram_post(self, content: str) -> str:
        """Instagram 포스트 변환"""
        return f"📱 Instagram Post\n\n{content[:200]}...\n\n#hashtag1 #hashtag2"
    
    def _to_twitter_thread(self, content: str) -> str:
        """Twitter 스레드 변환"""
        return f"🐦 Twitter Thread\n\n1/ {content[:280]}\n\n2/ [계속...]"
    
    def _to_linkedin_post(self, content: str) -> str:
        """LinkedIn 포스트 변환"""
        return f"💼 LinkedIn Post\n\n{content[:300]}...\n\n#professional #insights"
    
    def _to_medium_article(self, content: str) -> str:
        """Medium 아티클 변환"""
        return f"# Medium Article\n\n{content}"
    
    def _save_osmu_scripts(self, osmu_scripts: Dict[str, str], output_path: str):
        """OSMU 스크립트 저장"""
        osmu_file = os.path.join(output_path, "osmu_scripts.txt")
        
        with open(osmu_file, 'w', encoding='utf-8') as f:
            for platform, script in osmu_scripts.items():
                f.write(f"\n{'='*50}\n")
                f.write(f"{platform.upper()}\n")
                f.write(f"{'='*50}\n\n")
                f.write(script)
                f.write("\n\n")
        
        print(f"✅ OSMU 스크립트 저장: {osmu_file}")
