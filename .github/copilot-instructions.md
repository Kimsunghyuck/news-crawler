# Copilot Instructions - News Crawler

## 프로젝트 개요
한국 3대 언론사(동아일보, 조선일보, 중앙일보)에서 정치/스포츠/경제 뉴스를 자동 수집하는 크롤러 및 정적 웹사이트. GitHub Actions로 매일 자동 실행되며, GitHub Pages로 무료 호스팅.

## 핵심 아키텍처

### 데이터 파이프라인
```
crawler.py → parser.py → data/{category}/{source}/news_{date}.json
    ↓
report_generator.py → reports/{category}/{source}/report_{date}.md
    ↓
docs/data/ (GitHub Pages 배포용)
```

### 디렉토리 구조 규칙
- **data/**: 원본 JSON 데이터 (`{category}/{source}/news_{date}.json`)
- **docs/**: GitHub Pages 정적 사이트 (HTML + JSON 복사본)
- **reports/**: 마크다운 보고서 (개별 + combined)
- **web/**: Flask 개발 서버 (로컬 테스트용, 배포에는 미사용)

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

## GitHub Actions 자동화

### 워크플로우
- **daily-crawl.yml**: 매일 한국시간 오전 9:20 실행 (cron: `20 0 * * *` UTC)
- **manual-crawl.yml**: 수동 트리거 가능
- 중요: Settings → Actions → General에서 "Read and write permissions" 필수

### 배포 프로세스
1. crawler.py 실행 → data/ 생성
2. `cp -r data/* docs/data/` (GitHub Pages용 복사)
3. git add/commit/push (봇 계정)

## 주의사항

- **docs/ 폴더는 수동 편집 금지**: crawler.py가 data/에서 자동 복사
- **web/ 앱은 개발용**: 실제 배포는 docs/ 정적 사이트 사용
- **파서 추가 시 lxml 필수**: BeautifulSoup의 기본 파서보다 빠름
- **이미지 URL 검증 생략**: 크롤링 속도 우선 (클라이언트 측에서 fallback 처리)

## 빠른 참조

### 파일별 역할
- `crawler.py`: HTTP 요청 + 이미지 추출 + JSON 저장
- `parser.py`: HTML → 뉴스 항목 딕셔너리 (1000+ 줄, 9개 파서 함수)
- `report_generator.py`: JSON → 마크다운 보고서
- `config.py`: 모든 설정의 단일 진실 소스 (SSOT)

### 테스트 명령어
```powershell
# 특정 날짜 보고서 생성
python report_generator.py

# 스케줄러 실행 (매일 자동화, Ctrl+C로 종료)
python scheduler.py
```
