# nodes/serp_crawler_node.py
import json
import requests
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from utils.logger import get_logger
from utils.llm_client import LLMClient
import os
import time
from urllib.parse import urlparse

logger = get_logger("SERPCrawlerNode")


class SERPCrawlerNode:
    """
    Step2-1: SERP 크롤링 노드
    - 주제 관련 상위 30개 블로그 URL 수집
    - 각 블로그의 새글(최근글) 목록 크롤링 (최대 10개)
    - 각 블로그의 인기글 목록 크롤링 (최대 10개)
    """

    def __init__(self) -> None:
        self.llm = LLMClient()
        self.naver_client_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_client_secret = os.getenv("NAVER_CLIENT_SECRET")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def crawl(self, topic_data: Dict[str, Any], platform: str = "네이버 블로그") -> Dict[str, Any]:
        """주제 관련 상위 블로그 수집 + 각 블로그의 새글/인기글 크롤링"""
        logger.info("SERPCrawlerNode: SERP 크롤링 시작")

        selected_topic = topic_data.get("selected_topic", {})
        topic_title = selected_topic.get("title", "")
        
        if not topic_title:
            raise ValueError("크롤링할 주제가 없습니다")

        # 네이버 검색 API 사용
        if platform == "네이버 블로그" and self.naver_client_id:
            results = self._search_naver_blog(topic_title)
        else:
            # API 없을 시 LLM으로 추천 URL 생성
            results = self._generate_mock_results(topic_title)

        # 각 블로그에서 새글/인기글 크롤링
        logger.info(f"SERPCrawlerNode: {len(results)}개 블로그의 새글/인기글 크롤링 시작...")
        total_recent_posts = 0
        total_popular_posts = 0
        
        for idx, blog_info in enumerate(results, 1):
            logger.info(f"  [{idx}/{len(results)}] {blog_info['title']} 크롤링 중...")
            
            # 네이버 블로그 URL에서 블로그 홈 추출
            blog_home_url = self._extract_blog_home(blog_info['url'])
            
            if blog_home_url:
                # 새글 크롤링 (최대 10개)
                recent_posts = self._crawl_recent_posts(blog_home_url, max_count=10)
                blog_info['recent_posts'] = recent_posts
                total_recent_posts += len(recent_posts)
                
                # 인기글 크롤링 (최대 10개)
                popular_posts = self._crawl_popular_posts(blog_home_url, max_count=10)
                blog_info['popular_posts'] = popular_posts
                total_popular_posts += len(popular_posts)
                
                logger.info(f"    ✅ 새글 {len(recent_posts)}개, 인기글 {len(popular_posts)}개 수집")
            else:
                blog_info['recent_posts'] = []
                blog_info['popular_posts'] = []
                logger.warning(f"    ⚠️ 블로그 홈 URL 추출 실패")
            
            # 요청 간 딜레이 (서버 부하 방지)
            time.sleep(0.5)

        logger.info(f"SERPCrawlerNode: 총 {len(results)}개 블로그, 새글 {total_recent_posts}개, 인기글 {total_popular_posts}개 수집 완료")
        
        return {
            "topic": topic_title,
            "platform": platform,
            "total_results": len(results),
            "total_recent_posts": total_recent_posts,
            "total_popular_posts": total_popular_posts,
            "serp_results": results
        }

    def _search_naver_blog(self, query: str, display: int = 30) -> List[Dict[str, Any]]:
        """네이버 블로그 검색 API"""
        try:
            url = "https://openapi.naver.com/v1/search/blog.json"
            headers = {
                "X-Naver-Client-Id": self.naver_client_id,
                "X-Naver-Client-Secret": self.naver_client_secret
            }
            params = {
                "query": query,
                "display": display,
                "sort": "sim"  # 정확도순
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("items", [])
            
            results = []
            for idx, item in enumerate(items, 1):
                results.append({
                    "rank": idx,
                    "title": self._clean_html(item.get("title", "")),
                    "url": item.get("link", ""),
                    "description": self._clean_html(item.get("description", "")),
                    "blogger": item.get("bloggername", ""),
                    "postdate": item.get("postdate", "")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"네이버 블로그 검색 실패: {e}")
            return self._generate_mock_results(query)

    def _generate_mock_results(self, query: str, count: int = 30) -> List[Dict[str, Any]]:
        """API 없을 시 Mock 데이터 생성"""
        logger.warning("네이버 API 없음 - Mock 데이터 생성")
        
        results = []
        for i in range(1, count + 1):
            results.append({
                "rank": i,
                "title": f"{query} 관련 블로그 포스트 {i}",
                "url": f"https://example.com/blog/{i}",
                "description": f"{query}에 대한 상세 설명입니다.",
                "blogger": f"블로거{i}",
                "postdate": "20250114"
            })
        
        return results

    def _clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        text = text.replace("<b>", "").replace("</b>", "")
        text = text.replace("&quot;", '"').replace("&amp;", "&")
        return text

    def _extract_blog_home(self, post_url: str) -> str | None:
        """블로그 포스트 URL에서 블로그 홈 URL 추출"""
        try:
            # https://blog.naver.com/user_id/post_id -> https://blog.naver.com/user_id
            parsed = urlparse(post_url)
            if 'blog.naver.com' in parsed.netloc:
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 1:
                    blog_id = path_parts[0]
                    return f"https://blog.naver.com/{blog_id}"
            return None
        except Exception as e:
            logger.error(f"블로그 홈 URL 추출 실패: {e}")
            return None

    def _crawl_recent_posts(self, blog_home_url: str, max_count: int = 10) -> List[Dict[str, str]]:
        """블로그의 최근 글 목록 크롤링"""
        try:
            # 네이버 블로그 새글 목록은 ProxyView로 접근
            # https://blog.naver.com/BlogHome.naver?blogId=user_id&skinType=...
            blog_id = blog_home_url.split('/')[-1]
            
            # 실제로는 iframe 내부 URL 접근 필요
            # 간단한 방법: PostList.naver API 활용
            recent_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&currentPage=1"
            
            response = requests.get(recent_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            posts = []
            # 네이버 블로그 구조: <div class="post_list"> 또는 변경될 수 있음
            # 안전하게 a 태그에서 링크 추출
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if not href or not isinstance(href, str):
                    continue
                    
                title = link.get_text(strip=True)
                
                # 블로그 포스트 링크 필터링
                if '/PostView.naver' in href or f'/{blog_id}/' in href:
                    if title and len(title) > 5:  # 제목이 있는 경우만
                        posts.append({
                            'title': title[:100],  # 제목 길이 제한
                            'url': href if href.startswith('http') else f"https://blog.naver.com{href}"
                        })
                
                if len(posts) >= max_count:
                    break
            
            return posts[:max_count]
            
        except Exception as e:
            logger.warning(f"최근글 크롤링 실패 ({blog_home_url}): {e}")
            return []

    def _crawl_popular_posts(self, blog_home_url: str, max_count: int = 10) -> List[Dict[str, str]]:
        """블로그의 인기글 목록 크롤링"""
        try:
            blog_id = blog_home_url.split('/')[-1]
            
            # 네이버 블로그 인기글: 조회수 순 또는 공감순
            # PostList.naver에 orderBy 파라미터 추가
            popular_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&currentPage=1&orderBy=sim"
            
            response = requests.get(popular_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            posts = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if not href or not isinstance(href, str):
                    continue
                    
                title = link.get_text(strip=True)
                
                if '/PostView.naver' in href or f'/{blog_id}/' in href:
                    if title and len(title) > 5:
                        posts.append({
                            'title': title[:100],
                            'url': href if href.startswith('http') else f"https://blog.naver.com{href}"
                        })
                
                if len(posts) >= max_count:
                    break
            
            return posts[:max_count]
            
        except Exception as e:
            logger.warning(f"인기글 크롤링 실패 ({blog_home_url}): {e}")
            return []
