"""
Metadata Node
4️⃣ 제목/태그/메타데이터 생성
"""

from typing import Dict, Any


class MetadataNode:
    """제목, 태그, 메타 설명 생성"""
    
    def __init__(self):
        pass
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Metadata 노드 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태 (제목, 태그, 메타 설명)
        """
        print("🏷️ Metadata Node 실행 중...")
        
        content = state.get("content", "")
        keywords = state.get("keywords", [])
        
        # TODO: AI를 사용하여 메타데이터 생성
        title = self._generate_title(content, keywords)
        tags = self._generate_tags(content, keywords)
        meta_description = self._generate_meta_description(content, keywords)
        
        state.update({
            "title": title,
            "tags": tags,
            "meta_description": meta_description
        })
        
        return state
    
    def _generate_title(self, content: str, keywords: list) -> str:
        """제목 생성"""
        # TODO: LLM을 사용한 제목 생성
        return f"샘플 제목 - {keywords[0] if keywords else 'Blog'}"
    
    def _generate_tags(self, content: str, keywords: list) -> list:
        """태그 생성"""
        # TODO: LLM을 사용한 태그 생성
        return keywords[:5]
    
    def _generate_meta_description(self, content: str, keywords: list) -> str:
        """메타 설명 생성"""
        # TODO: LLM을 사용한 메타 설명 생성
        return f"이 글은 {', '.join(keywords[:3])}에 대한 내용입니다."
