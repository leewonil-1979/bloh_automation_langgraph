# 초기 단계 파이프라인 가이드

## 📌 개요

블로그 자동화 시스템의 **초기 단계 파이프라인**입니다.

아이디어 입력 → 주제 선정 → 플랫폼 추천 → 30일 글감 생성까지 자동화합니다.

---

## 🚀 실행 방법

### 1. 기본 실행

```bash
python initial_pipeline.py
```

프롬프트가 나타나면 아이디어를 입력하세요.

**예시:**
```
💡 아이디어를 입력하세요: 블로그 자동화
```

### 2. 테스트 실행

```bash
python test_initial_pipeline.py
```

미리 준비된 테스트 아이디어 중 선택할 수 있습니다.

---

## 📊 파이프라인 구조

```
사용자 아이디어 입력
      ↓
[Step 0-1] 아이디어 확장 (6-12개 주제 생성)
      ↓
[Step 0-2] 주제 스코어링 및 선정
      ↓
[Step 1] 플랫폼 추천
      ↓
[Step 2-1] SERP 크롤링 (상위 30개)
      ↓
[Step 2-2] 30일 콘텐츠 계획 생성
      ↓
결과 저장 (outputs/initial_pipeline_result.json)
```

---

## 🔧 구성 노드

### 1. IdeaExpanderNode
- **위치:** `nodes/idea_expander_node.py`
- **기능:** 아이디어를 6~12개의 블로그 주제로 확장
- **출력:** 주제 제목, 설명, 카테고리, 타겟 독자, 난이도

### 2. TopicScorerNode
- **위치:** `nodes/topic_scorer_node.py`
- **기능:** 주제별 수익성/확장성/지속성 점수화 및 최적 주제 선정
- **출력:** 스코어, 추천 이유, 플랫폼 제안

### 3. PlatformRecommenderNode
- **위치:** `nodes/platform_recommender_node.py`
- **기능:** 주제에 최적화된 블로그 플랫폼 추천
- **출력:** 메인 플랫폼, 보조 플랫폼, 전략

### 4. SERPCrawlerNode
- **위치:** `nodes/serp_crawler_node.py`
- **기능:** 네이버 블로그 검색 API로 상위 30개 수집
- **출력:** 제목, URL, 설명, 작성자

### 5. ContentPlannerNode
- **위치:** `nodes/content_planner_node.py`
- **기능:** SERP 분석하여 30일 글감 로테이션 생성
- **출력:** 30개 글감 (제목, 타입, 키워드, 개요)

---

## 📁 출력 파일

### `outputs/initial_pipeline_result.json`

전체 파이프라인 결과가 JSON 형식으로 저장됩니다.

**구조:**
```json
{
  "user_idea": "입력한 아이디어",
  "expanded_topics": { /* 확장된 주제들 */ },
  "scored_topics": { /* 스코어링 결과 */ },
  "platform_recommendation": { /* 플랫폼 추천 */ },
  "serp_data": { /* SERP 크롤링 결과 */ },
  "content_plan": { /* 30일 계획 */ }
}
```

---

## 🔄 무한 루프 사용법

30일 계획이 끝나면 새로운 30일 계획을 자동 생성할 수 있습니다.

```python
from nodes.content_planner_node import ContentPlannerNode
import json

# 이전 결과 로드
with open("outputs/initial_pipeline_result.json", "r", encoding="utf-8") as f:
    prev_result = json.load(f)

# 새로운 30일 계획 생성
planner = ContentPlannerNode()
serp_data = prev_result["serp_data"]

# 무한 루프
while True:
    new_plan = planner.plan(serp_data)
    print(f"새로운 30일 계획 생성 완료")
    
    # 계획 실행 또는 중단 조건
    if input("계속? (y/n): ").lower() != 'y':
        break
```

---

## 🎯 다음 단계

초기 파이프라인 실행 후:

1. **결과 확인**
   ```bash
   cat outputs/initial_pipeline_result.json
   ```

2. **특정 글감 선택하여 글 작성**
   ```bash
   python main_post_test.py
   ```

3. **전체 자동화 시스템 연결**
   - 30일 계획을 `scripts/main_loop.py`에 통합
   - 자동 발행 스케줄러 설정

---

## ⚙️ 환경 변수 설정

`.env` 파일에 다음 추가:

```env
# OpenAI API
OPENAI_API_KEY=sk-proj-your-key

# Naver Search API (선택)
NAVER_CLIENT_ID=your-client-id
NAVER_CLIENT_SECRET=your-client-secret
```

**참고:** Naver API 없이도 Mock 데이터로 테스트 가능합니다.

---

## 🐛 트러블슈팅

### 1. JSON 파싱 에러

**증상:** `JSON 파싱 실패` 에러

**해결:**
- `debug_*.txt` 파일 확인
- LLM 응답이 JSON 형식인지 확인
- `max_tokens` 증가

### 2. API 호출 실패

**증상:** `OpenAI API 오류`

**해결:**
- `.env` 파일의 `OPENAI_API_KEY` 확인
- API 잔액 확인

### 3. Naver API 없음

**증상:** `네이버 API 없음 - Mock 데이터 생성`

**해결:**
- 정상 동작입니다 (Mock 데이터 사용)
- 실제 데이터 필요 시 Naver API 등록

---

## 📝 예시 출력

```
================================================================================
🚀 블로그 자동화 시스템 - 초기 단계 파이프라인
================================================================================

📌 Step 0-1: 아이디어 확장 중...
✅ 8개의 주제 후보 생성 완료

📋 생성된 주제 후보:
  - 블로그 자동화 시스템 구축 완벽 가이드
  - 초보자를 위한 블로그 자동 포스팅 툴 비교
  - AI로 블로그 글쓰기 자동화하는 방법
  ... 외 5개

📌 Step 0-2: 주제 스코어링 및 최적 주제 선정 중...
✅ 최종 선정 주제: 블로그 자동화 시스템 구축 완벽 가이드
   총점: 28점
   - 수익성: 8
   - 확장성: 9
   - 지속성: 8
   - 난이도: 3

📌 Step 1: 최적 플랫폼 추천 중...
✅ 추천 플랫폼:
   메인: 티스토리
   보조: 네이버 블로그, 워드프레스

📊 추천 전략:
   콘텐츠 형식: 긴글 + 코드예제
   포스팅 빈도: 주 3-4회
   수익화 방법: 애드센스 + 제휴마케팅

📌 Step 2-1: 상위 블로그 수집 중...
✅ 30개 블로그 수집 완료

📌 Step 2-2: 30일 콘텐츠 로테이션 생성 중...
✅ 30일 콘텐츠 계획 생성 완료

📅 30일 글감 미리보기 (1~7일):
   Day 1: [기본개념] 블로그 자동화란 무엇인가?
   Day 2: [HOW-TO] 블로그 자동화 시작하기
   Day 3: [초보자팁] 블로그 자동화 시 주의사항
   ... 외 27일

================================================================================
💾 전체 결과 저장 완료: outputs/initial_pipeline_result.json
================================================================================

🎉 초기 단계 파이프라인 완료!
```

---

## 📚 참고 자료

- [프로젝트 전체 가이드](PROJECT_GUIDE.md)
- [메인 README](README.md)
- [기존 노드 문서](scripts/)
