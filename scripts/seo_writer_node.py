"""
SEO Writer Node
3️⃣ SEO 글 본문 생성
"""

from typing import Dict, Any


class SEOWriterNode:
    """SEO 최적화 블로그 본문 작성"""
    
    def __init__(self):
        pass
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        SEO Writer 노드 실행
        
        Args:
            state: 현재 상태
            
        Returns:
            업데이트된 상태 (본문 내용)
        """
        print("✍️ SEO Writer Node 실행 중...")
        
        keywords = state.get("keywords", [])
        tone = state.get("tone", "")
        style = state.get("style", "")
        writing_loop = state.get("writing_loop", {})
        
        # TODO: AI를 사용하여 본문 작성
        content = self._generate_content(keywords, tone, style, writing_loop)
        
        state.update({
            "content": content
        })
        
        return state
    
    def _generate_content(self, keywords: list, tone: str, style: str, 
                         writing_loop: dict) -> str:
        """SEO 최적화 본문 생성"""
        # TODO: LLM을 사용한 본문 생성
        
        intro = writing_loop.get("introduction", "")
        body = writing_loop.get("body", "")
        conclusion = writing_loop.get("conclusion", "")
        
        # 샘플 본문
        content = f"""
# 샘플 블로그 포스트

## 소개
{intro}

## 본문
{body}

키워드: {', '.join(keywords)}
톤: {tone}
스타일: {style}

## 결론
{conclusion}
"""
        
        return content
