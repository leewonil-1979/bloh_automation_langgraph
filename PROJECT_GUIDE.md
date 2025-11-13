# 프로젝트 가이드

## 전체 워크플로우

```
아이디어 입력
    ↓
Discovery Node (검색 + 플랫폼 추천)
    ↓
Strategy Node (루프/문체 설정)
    ↓
SEO Writer Node (본문 작성)
    ↓
Metadata Node (제목/태그 생성)
    ↓
Image Alt Node (이미지 기획)
    ↓
Output Node (HTML 생성 및 저장)
    ↓
OSMU Node (다른 플랫폼용 변환)
```

## 노드별 설명

### 1. Discovery Node
- 키워드 검색
- 경쟁사 분석
- 트렌드 분석
- 플랫폼 추천

### 2. Strategy Node
- 블로그별 루프 로딩 (woncamp.yaml, won201.yaml)
- 문체/톤 자동 설정

### 3. SEO Writer Node
- SEO 최적화 본문 작성
- 키워드 자연스럽게 삽입

### 4. Metadata Node
- 제목 생성
- 태그 생성
- 메타 설명 생성

### 5. Image Alt Node
- 이미지 위치 기획
- ALT 텍스트 생성

### 6. Output Node
- HTML 파일 생성
- metadata.json 저장

### 7. Scheduler Node
- 예약 발행 기능

### 8. OSMU Node
- YouTube 스크립트
- SNS 포스팅
- 뉴스레터 변환

## 사용 방법

1. 블로그 설정 파일 수정 (`configs/woncamp.yaml`)
2. 메인 루프 실행
3. `outputs/` 폴더에서 결과 확인
