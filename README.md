# 🚀 BLOG_AUTOMATION_LANGGRAPH

GPT-5 + LangGraph 기반 블로그 자동화 프로젝트  
> “주제를 입력하면, 블로그 분석·전략 수립·콘텐츠 작성까지 자동으로!”

---

## 📌 주요 기능
1. **아이디어 구체화** — 상위 블로그 30개 분석 + 플랫폼 추천  
2. **지침 자동화** — 톤/문체/글 분량/업로드 시간 자동 결정  
3. **콘텐츠 생성** — SEO 완성 HTML 자동 저장  
4. **예약 발행** — 여행 등 부재 시 7일치 자동 생성  
5. **OSMU 확장** — 영상/뉴스레터/카드뉴스로 파생

---

## ⚙️ 기술 스택
| 구분 | 사용 기술 |
|------|------------|
| AI | OpenAI GPT-5 |
| 워크플로 | LangGraph |
| 스케줄링 | Python schedule |
| 크롤링 | requests + BeautifulSoup |
| 저장 | JSON / YAML / HTML |
| 확장 | Notion API, Google Sheets API |

---

## 📂 폴더 구조
(생략 — 상단 참조)

---

## 🚀 실행 방법

```bash
pip install -r requirements.txt
python scripts/discovery_node.py
