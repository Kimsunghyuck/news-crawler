# Copilot Instructions - News Crawler

## 프로젝트 개요
한국 3대 언론사(동아일보, 조선일보, 중앙일보)에서 6개 카테고리 뉴스를 자동 수집하는 크롤러 및 정적 웹사이트. GitHub Actions로 하루 3번 자동 실행되며, GitHub Pages로 무료 호스팅. 트렌드 분석 및 통계 대시보드 포함.

## 핵심 아키텍처

### 데이터 파이프라인
```
crawler.py → parser.py → data/{category}/{source}/news_{date}.json
    ↓
analyzer.py → docs/data/trends/trends_{date}.json
    ↓
report_generator.py → reports/{category}/{source}/report_{date}.md
    ↓
docs/data/ (GitHub Pages 배포용)
```

### 디렉토리 구조 규칙
- **data/**: 원본 JSON 데이터 (`{category}/{source}/news_{date}.json`)
- **docs/**: GitHub Pages 정적 사이트 (HTML + JSON 복사본)
- **reports/**: 마크다운 보고서 (개별 + combined)

### 설정 파일 (config.py)
- `NEWS_SOURCES`: 카테고리별 크롤링 대상 정의
  - 각 소스는 `parser` 필드로 parser.py의 함수명 지정 (`parse_{source}_{category}`)
  - `max_articles`: 소스당 수집 기사 수 (기본 5개)
- `CATEGORY_EN_MAP`, `SOURCE_EN_MAP`: 한글↔영문 디렉토리명 매핑
- KST 타임존 사용: `datetime.now(timezone(timedelta(hours=9)))`

## 개발 워크플로우

### 로컬 테스트
```powershell
# 크롤링 실행 (45개 뉴스 + 이미지)
python crawler.py

# GitHub Pages 미리보기
cd docs; python -m http.server 8000
```

### 새 뉴스 소스 추가
1. `config.py`의 `NEWS_SOURCES`에 딕셔너리 추가
2. `parser.py`에 `parse_{source}_{category}()` 함수 구현
   - 반환값: `[{"title": str, "url": str, "date": str, ...}]`
   - 이미지 추출은 `extract_image_url()` 활용
3. crawler.py는 자동으로 새 소스 감지 및 처리

### 파서 함수 패턴
```python
def parse_{source}_{category}(html_content: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    
    # 1. 뉴스 링크 찾기 (site-specific selector)
    links = soup.find_all('a', class_='article-link')
    
    # 2. 각 링크에서 메타데이터 추출
    for link in links:
        title = link.get_text(strip=True)
        url = link['href']
        # 이미지는 extract_image_url() 사용
        
    return news_items
```

## 중요한 관례

### 날짜 처리
- **항상 KST 사용**: `get_kst_now()` 함수 활용
- 파일명: `news_2025-12-01.json` (ISO 8601)
- JSON 내부: `scraped_at` 필드는 ISO 포맷 + KST 타임존

### 이미지 추출 로직
`crawler.py`의 `extract_article_image()`는 다음 순서로 시도:
1. Open Graph `<meta property="og:image">`
2. Twitter Card `<meta name="twitter:image">`
3. 기사 본문 첫 번째 `<img>`
상대 경로는 자동으로 절대 경로 변환.

### 에러 처리
- 개별 소스 실패 시 다른 소스는 계속 진행
- 재시도: `MAX_RETRIES=3`, `RETRY_DELAY=5` (config.py)
- 로깅: `logs/crawler.log` (INFO 레벨)

### 중복 제거 로직
- **merge_news()**: URL 기반 중복 자동 제거
- 하루 3번 크롤링 시 같은 날짜 파일에 누적 저장
- 중복 기사는 최신 정보로 업데이트
- 최종 저장: 유니크한 기사만 날짜순 정렬

## GitHub Actions 자동화

### 워크플로우
- **daily-crawl.yml**: 하루 3번 자동 실행 (KST 기준)
  - 오전 9:20 (cron: `20 0 * * *` UTC)
  - 오후 3:00 (cron: `0 6 * * *` UTC) 
  - 저녁 7:00 (cron: `0 10 * * *` UTC)
- **manual-crawl.yml**: 수동 트리거 가능
- 중요: Settings → Actions → General에서 "Read and write permissions" 필수

### 배포 프로세스
1. crawler.py 실행 → data/ 생성
2. `cp -r data/* docs/data/` (GitHub Pages용 복사)
3. git add/commit/push (봇 계정)

## 주의사항

- **docs/ 폴더는 수동 편집 금지**: crawler.py가 data/에서 자동 복사
- **파서 추가 시 lxml 필수**: BeautifulSoup의 기본 파서보다 빠름
- **이미지 URL 검증 생략**: 크롤링 속도 우선 (클라이언트 측에서 fallback 처리)

## 빠른 참조

### 파일별 역할
- `crawler.py`: HTTP 요청 + 이미지 추출 + JSON 저장
- `parser.py`: HTML → 뉴스 항목 딕셔너리 (1000+ 줄, 18개 파서 함수)
- `analyzer.py`: 트렌드 키워드 분석 + 빈도 집계
- `report_generator.py`: JSON → 마크다운 보고서
- `config.py`: 모든 설정의 단일 진실 소스 (SSOT)
- `docs/static/js/main.js`: 프론트엔드 로직 (트렌드 패널, 통계 대시보드, 북마크)

### 주요 기능
- **트렌드 분석**: 한글 키워드 추출 (정규식) + 빈도 분석 + 불용어 필터링
- **통계 대시보드**: Chart.js 기반 데이터 시각화
  - 카테고리별 분포 (파이 차트)
  - 신문사별 비교 (바 차트)
  - 최근 7일 트렌드 (라인 차트)
- **북마크**: LocalStorage 기반 즐겨찾기 (최대 100개)
- **다크모드**: CSS 변수 기반 테마 전환

### 테스트 명령어
```powershell
# 크롤링 실행
python crawler.py

# 트렌드 분석
python analyzer.py

# 특정 날짜 보고서 생성
python report_generator.py

# 로컬 웹서버
cd docs; python -m http.server 8000
```

## 최신 업데이트 (v6.0 - 2025-12-05)

### 통계 대시보드
- Chart.js 3.9.1 통합
- 탭 네비게이션 (트렌드/통계)
- 3가지 차트 유형:
  - `renderCategoryPieChart()`: 카테고리 분포
  - `renderSourceBarChart()`: 신문사 비교
  - `renderWeeklyLineChart()`: 7일 트렌드
- `collectDailyStats()`: 일간 통계 수집
- `collectWeeklyStats()`: 주간 통계 수집 (미래 날짜 제외)

### 최적화
- 404 에러 최소화: 존재하는 날짜만 요청
- 중복 제거: URL 기반 자동 처리
- 성능: 병렬 fetch 요청 (async/await)
