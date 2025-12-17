# Hyeok News Crawler

한국 3대 언론사(동아일보, 조선일보, 중앙일보)의 뉴스를 자동 수집하는 크롤러 및 웹 포털입니다.  
GitHub Actions로 하루 3번 자동 실행되며, GitHub Pages로 무료 호스팅됩니다.

## 🌟 주요 기능

- **자동 크롤링**: 6개 카테고리 × 3개 언론사 = 하루 3번 최대 270개 뉴스 수집
- **트렌드 분석**: 실시간 키워드 빈도 분석 및 카테고리별 트렌드 제공
- **통계 대시보드**: Chart.js 기반 데이터 시각화 (파이/바/라인 차트)
- **이미지 추출**: Open Graph/Twitter Card 메타데이터 기반 썸네일 추출
- **뉴스 티커**: 최신 헤드라인을 세로 슬라이드 애니메이션으로 표시
- **북마크 기능**: LocalStorage 기반 즐겨찾기 시스템
- **이메일 인증**: Firebase Email Link Authentication (비밀번호 없는 로그인)
- **정적 웹사이트**: 카테고리/언론사/날짜별 필터링 + 다크모드 지원
- **완전 자동화**: GitHub Actions 스케줄러 (하루 3번: 9:00, 15:00, 19:00 KST)
- **데이터 관리**: 30일 이상 지난 뉴스 자동 삭제 (저장소 용량 최적화)

## 📁 프로젝트 구조

```
news-crawler/
├── crawler.py              # HTTP 요청 + 이미지 추출 + JSON 저장
├── parser.py               # HTML 파싱 (18개 파서 함수)
├── analyzer.py             # 트렌드 키워드 분석
├── report_generator.py     # 마크다운 보고서 생성
├── cleanup_old_data.py     # 30일 이상 데이터 자동 정리
├── scheduler.py            # 로컬 스케줄러 (테스트용)
├── config.py               # 중앙 설정 (SSOT)
├── requirements.txt        # Python 의존성
├── Dockerfile              # Docker 이미지 빌드 설정
├── docker-compose.yml      # Docker Compose 설정
├── FIREBASE_SETUP.md       # Firebase 프로젝트 설정 가이드
├── EMAIL_AUTH_GUIDE.md     # 이메일 인증 사용 가이드
├── data/                   # 원본 JSON 데이터
│   └── {category}/{source}/news_{date}_{time}.json  # 시간 스탬프 포함
├── docs/                   # GitHub Pages 정적 사이트
│   ├── index.html          # 메인 페이지 (인증 UI 포함)
│   ├── static/             # CSS, JS, 이미지
│   │   ├── css/style.css   # 스타일 (인증 UI 포함)
│   │   └── js/
│   │       ├── main.js     # 메인 로직
│   │       └── auth.js     # Firebase 이메일 인증
│   └── data/               # JSON 복사본 (배포용)
│       └── trends/         # 트렌드 분석 데이터
├── reports/                # 마크다운 보고서
│   ├── combined/           # 전체 리포트
│   └── {category}/{source}/report_{date}.md
└── .github/workflows/      # GitHub Actions
    ├── daily-crawl.yml     # 하루 3번 자동 실행 (09:00, 15:00, 19:00)
    ├── test-website.yml    # Playwright E2E 테스트
    └── manual-crawl.yml    # 수동 트리거
```

## 🚀 빠른 시작

### 1. 크롤링 실행

```powershell
# 의존성 설치
pip install -r requirements.txt

# 크롤링 실행 (90개 뉴스 + 이미지)
python crawler.py
```

### 2. 로컬 웹서버 테스트

```powershell
# GitHub Pages 미리보기
cd docs
python -m http.server 8000
# → http://localhost:8000
```

### 3. GitHub Pages 배포

1. **저장소 Public으로 변경**
2. **Settings → Pages**
   - Source: Deploy from a branch
   - Branch: `main`, Folder: `/docs`
3. **Settings → Actions → General**
   - Workflow permissions: **Read and write permissions** 체크
4. 완료! `https://<username>.github.io/<repo-name>`

상세 가이드: [`docs/GITHUB_PAGES_SETUP.md`](docs/GITHUB_PAGES_SETUP.md)

## 📊 데이터 구조

### JSON 예시

```json
[
  {
    "title": "기사 제목",
    "url": "https://...",
    "date": "2025-12-02",
    "category": "정치",
    "source": "동아일보",
    "image_url": "https://...",
    "scraped_at": "2025-12-02T16:10:05+09:00"
  }
]
```

## 🛠️ 기술 스택 및 아키텍처

### Frontend
- **HTML5 + CSS3**: 반응형 레이아웃 (Flexbox, Grid)
- **Vanilla JavaScript**: 비동기 데이터 로딩 (Fetch API)
- **Swiper.js 11.1.14**: 뉴스 티커 세로 슬라이드 애니메이션
- **Chart.js 3.9.1**: 통계 차트 라이브러리 (파이/바/라인 차트)
- **Firebase Authentication 10.7.1**: Email Link 인증 (비밀번호 없는 로그인)

### Backend (Python 3.x)
- **BeautifulSoup4 (lxml)**: HTML 파싱 엔진
- **Requests**: HTTP 클라이언트 (User-Agent 헤더 포함)
- **datetime (KST)**: 한국 표준시 타임존 처리

### 크롤링 원리
1. **HTTP 요청**: `requests.get()` + 재시도 로직 (3회, 5초 지연)
2. **HTML 파싱**: 언론사별 CSS 셀렉터로 뉴스 링크 추출
3. **이미지 추출**: Open Graph → Twitter Card → 본문 첫 이미지 순서로 fallback
4. **데이터 저장**: JSON 포맷 (`data/{category}/{source}/news_{date}.json`)
5. **중복 제거**: URL 기반 자동 중복 제거 (하루 3번 크롤링 시)
6. **트렌드 분석**: 제목에서 한글 키워드 추출 + 빈도 분석

### 자동화
- **GitHub Actions**: 하루 3번 실행
  - 오전 9:00 KST (cron: `0 0 * * *` UTC)
  - 오후 3:00 KST (cron: `0 6 * * *` UTC)
  - 저녁 7:00 KST (cron: `0 10 * * *` UTC)
- **배포 파이프라인**: `data/` → `docs/data/` 복사 후 자동 커밋/푸시
- **트렌드 생성**: 크롤링 후 자동으로 `docs/data/trends/trends_{date}.json` 생성

### 호스팅
- **GitHub Pages**: 정적 사이트 무료 호스팅 (`/docs` 폴더)

### 개발 도구
- **Claude Code**: Anthropic의 공식 CLI 도구를 활용한 AI 기반 개발
  - 코드 작성, 리팩토링, 디버깅 자동화
  - GitHub Actions 워크플로우 구성 및 E2E 테스트 설정
  - 실시간 협업을 통한 빠른 프로토타이핑
  - 문서 자동 생성 및 프로젝트 구조 설계

### Docker 지원
- **Docker Compose**: 개발 환경 컨테이너화
  - Python 3.11 기반 이미지
  - 자동 의존성 설치 및 크롤링 실행
  - 로컬 개발 환경 일관성 보장

```bash
# Docker로 크롤링 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d
```


## 📅 개발 일지

### Day 1-2: 초기 설계 (2025-12-02)
- 프로젝트 구조 설계 및 3개 카테고리(정치/스포츠/경제) 크롤러 구현
- BeautifulSoup4 기반 파서 9개 함수 작성 (동아/조선/중앙 × 3 카테고리)
- `config.py` 중앙 집중식 설정 시스템 구축
- Open Graph 이미지 추출 로직 개발
- JSON 데이터 저장 구조 확립 (`data/{category}/{source}/`)

### Day 3: 확장 및 자동화 (2025-12-03)
- 3개 카테고리 추가: 사회/국제/문화 (총 18개 파서 함수)
- GitHub Actions 워크플로우 설정 (daily-crawl.yml, manual-crawl.yml)
- 마크다운 보고서 생성기 개발 (`report_generator.py`)
- KST 타임존 처리 표준화 (`get_kst_now()`)
- 에러 핸들링 및 로깅 시스템 구축

### Day 4: 웹 포털 및 UI (2025-12-04)
- GitHub Pages 정적 사이트 구축 (`docs/index.html`)
- 뉴스 티커 배너 개발 (Swiper.js 세로 슬라이드)
- 카테고리별 색상 뱃지 시스템 (6개 카테고리)
- 반응형 네비게이션 (데스크톱/태블릿/모바일)
- 날짜/카테고리/언론사 필터링 기능
- 이미지 fallback 처리 (로딩 실패 시 placeholder)

### Day 5: 트렌드 분석 및 UI 개선 (2025-12-05)
- **하루 3번 크롤링 시스템 구현** (9시/15시/19시)
- **트렌드 분석 모듈 개발** (`analyzer.py`)
  - 한글 키워드 추출 (정규식 기반)
  - 빈도 분석 및 불용어 처리
  - 카테고리별 트렌드 집계
- **트렌드 패널 UI 추가**
  - 우측 슬라이드 사이드바
  - Top 10 키워드 랭킹 표시
  - 카테고리별 키워드 뱃지
- **통계 대시보드 구현**
  - Chart.js 기반 데이터 시각화
  - 카테고리별 분포 파이 차트
  - 신문사별 비교 바 차트
  - 최근 7일 트렌드 라인 차트
  - 탭 네비게이션 (트렌드/통계 전환)
- **아이콘 스타일 통일** (다크모드/북마크/트렌드)
- **중복 제거 로직 구현** (URL 기반)
- **404 에러 최적화** (존재하는 데이터만 수집)
- README 최신화 및 프로젝트 문서화 완료

### Day 6: 시간 스탬프 시스템 및 데이터 통합 (2025-12-09 ~ 2025-12-16)
- **파일명 시스템 개편**
  - `news_{date}.json` → `news_{date}_{time}.json` (예: `news_2025-12-09_09-20.json`)
  - 하루 3회 크롤링 데이터를 개별 파일로 분리 저장
  - `get_crawl_time_str()` 함수 추가 (parser.py)
- **데이터 통합 로직 구현**
  - 메인 화면: 각 시간대별 1개 기사 표시 (최신 타임스탬프 우선)
  - 카테고리 화면: 3개 시간대 데이터 통합 + URL 기반 중복 제거
  - 뉴스 티커: 전체 시간대 통합 데이터 랜덤 표시
  - 통계 대시보드: 3개 시간대 중복 제거 후 집계
- **트렌드 분석 개선**
  - `analyzer.py` 수정: 3개 시간대 파일 모두 분석
  - `analyze_daily_keywords()`, `analyze_category_keywords()` 함수 업데이트
  - 키워드 빈도수 정확도 향상 (90개 → 최대 270개 기사 분석)
- **E2E 테스트 구축**
  - Playwright 기반 자동화 테스트 추가 (`test-website.yml`)
  - 페이지 로드, 카테고리 전환, 날짜 선택, JavaScript 에러 체크
  - 홈 대시보드 우선 표시 로직에 맞춰 테스트 수정
- **Git 워크플로우 최적화**
  - `git pull --rebase` 자동 병합 처리
  - CI/CD 파이프라인 안정화

### Day 7: 데이터 관리 및 Docker 지원 (2025-12-16 ~ 2025-12-17)
- **데이터 자동 정리 시스템 구축**
  - `cleanup_old_data.py` 개발: 30일 이상 지난 뉴스 자동 삭제
  - 정규식 기반 날짜 파싱 (신/구 파일명 형식 모두 지원)
  - 빈 디렉토리 자동 정리 기능
  - GitHub Actions에 통합 (매 크롤링마다 실행)
- **Docker 컨테이너화**
  - Dockerfile 작성 (Python 3.11-slim 기반)
  - docker-compose.yml 설정 (볼륨 마운트, 한국 시간대)
  - 개발 환경 일관성 보장 및 배포 간소화
- **크롤링 시간 최적화**
  - 09:20 → 09:00 KST로 변경 (정시 실행)
  - cron 표현식 업데이트
- **문서화 개선**
  - README.md 최신화 (Docker, 데이터 정리)
  - CLAUDE.md 작성 (개발자 가이드)

### Day 8: Email Authentication 구현 (2025-12-17)
- **Firebase Email Link Authentication 통합**
  - Firebase 프로젝트 생성 및 설정
  - Email Link (passwordless) 인증 방식 구현
  - `docs/static/js/auth.js` 개발: Firebase SDK 통합
  - 인증 상태 관리 (onAuthStateChanged)
- **랜딩 페이지 UI 개발**
  - 3단계 인증 플로우 구현 (입장 → 이메일 입력 → 대기 화면)
  - 애니메이션 효과 (fadeIn, shake)
  - 로딩 스피너 및 에러 메시지 표시
  - 다크모드 지원
- **보안 기능**
  - 이메일 링크 만료 처리
  - localStorage 기반 이메일 임시 저장
  - Authorized domains 설정 (localhost, GitHub Pages)
  - 자동 로그인 유지
- **문서화**
  - `FIREBASE_SETUP.md` 작성: Firebase 프로젝트 설정 가이드
  - `EMAIL_AUTH_GUIDE.md` 작성: 인증 플로우 사용 가이드
  - 디버깅 팁 및 일반적인 문제 해결 방법

## 📈 수집 현황

| 카테고리 | 언론사 | 기사 수/회 | 하루 총 | 이미지 | 트렌드 | 자동화 |
|---------|--------|-----------|---------|--------|--------|--------|
| 정치 | 동아/조선/중앙 | 15개 | 45개 | ✅ | ✅ | ✅ |
| 스포츠 | 동아/조선/중앙 | 15개 | 45개 | ✅ | ✅ | ✅ |
| 경제 | 동아/조선/중앙 | 15개 | 45개 | ✅ | ✅ | ✅ |
| 사회 | 동아/조선/중앙 | 15개 | 45개 | ✅ | ✅ | ✅ |
| 국제 | 동아/조선/중앙 | 15개 | 45개 | ✅ | ✅ | ✅ |
| 문화 | 동아/조선/중앙 | 15개 | 45개 | ✅ | ✅ | ✅ |
| **합계** | **18개 소스** | **90개** | **270개/일** | **90개** | **실시간** | **하루 3번** |

**크롤링 시간**: 09:00, 15:00, 19:00 (KST)
**중복 제거**: URL 기반 자동 처리
**트렌드 분석**: 전체 + 카테고리별 키워드 Top 20

---

## 📚 추가 문서

- **[CLAUDE.md](CLAUDE.md)**: Claude Code 개발자를 위한 상세 가이드
  - 아키텍처 설계 원칙
  - 코드 컨벤션 및 패턴
  - 새 기능 추가 방법
  - 디버깅 팁

- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)**: Firebase 프로젝트 설정 가이드
  - Firebase 프로젝트 생성
  - Email Link Authentication 활성화
  - Authorized domains 설정
  - Firebase Config 입력 방법

- **[EMAIL_AUTH_GUIDE.md](EMAIL_AUTH_GUIDE.md)**: 이메일 인증 사용 가이드
  - 인증 플로우 설명
  - 로컬 테스트 방법
  - 디버깅 및 문제 해결
  - GitHub Pages 배포 시 주의사항

- **[GitHub Pages 설정 가이드](docs/GITHUB_PAGES_SETUP.md)**: 배포 상세 가이드

---

**최종 업데이트**: 2025년 12월 17일
**버전**: 8.0 (Email Authentication + Firebase 통합)
**개발 도구**: [Claude Code](https://claude.com/claude-code) by Anthropic
