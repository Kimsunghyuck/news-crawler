# Anthropic 뉴스 크롤러

Anthropic 웹사이트(https://www.anthropic.com/news)에서 최신 뉴스를 자동으로 크롤링하고 한국어 보고서로 변환하는 완전 자동화 시스템입니다.

## 🌟 주요 기능

- ✅ Anthropic 뉴스 페이지에서 최신 뉴스 자동 크롤링
- ✅ 뉴스 제목, URL, 날짜, 카테고리 추출
- ✅ **날짜별 JSON 파일 저장** - 매일 별도 파일로 관리
- ✅ **한국어 보고서 자동 생성** - 크롤링 후 즉시 보고서 생성
- ✅ **GitHub Actions 완전 자동화** ⭐ - 컴퓨터 안 켜도 자동 실행!
- ✅ **매일 아침 9시 자동 실행** - GitHub 서버에서 자동 크롤링
- ✅ **날짜별 파일 관리** - 크롤링 날짜가 파일명에 포함
- ✅ 중복 제거 및 증분 업데이트
- ✅ 에러 처리 및 재시도 로직
- ✅ 상세한 로깅

## 📁 프로젝트 구조

```
news-crawler/
├── .github/
│   └── workflows/
│       ├── daily-crawl.yml      # 매일 자동 크롤링 (GitHub Actions)
│       └── manual-crawl.yml     # 수동 실행 워크플로우
├── config.py                    # 설정 파일
├── crawler.py                   # 크롤링 메인 로직 + 자동 보고서 생성
├── parser.py                    # HTML 파싱 함수
├── report_generator.py          # 한국어 보고서 생성 모듈
├── scheduler.py                 # 로컬 자동 스케줄링 모듈 (선택)
├── requirements.txt             # 필요한 라이브러리
├── data/                        # 크롤링 데이터 저장 폴더
│   ├── .gitkeep
│   └── news_2025-12-01.json    # 날짜별 뉴스 데이터
├── reports/                     # 보고서 저장 폴더
│   └── anthropic_news_report_2025-12-01.md
├── logs/                        # 로그 파일 폴더
│   └── crawler.log
└── docs/
    └── GITHUB_ACTIONS_SETUP.md  # GitHub Actions 설정 가이드
```

## 🚀 빠른 시작

### GitHub Actions 자동화 (추천) ⭐

**컴퓨터를 켜지 않아도 매일 자동으로 크롤링합니다!**

1. **저장소 Fork 또는 Clone**
2. **GitHub Actions 권한 설정**
   - 저장소 → Settings → Actions → General
   - Workflow permissions → "Read and write permissions" 선택
   - Save 클릭
3. **완료!** 매일 오전 9시에 자동 실행됩니다.

자세한 설정 방법: [`docs/GITHUB_ACTIONS_SETUP.md`](docs/GITHUB_ACTIONS_SETUP.md)

### 로컬 실행 (선택)

#### 1. 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

#### 2-A. 단일 실행 (한 번만 크롤링)

```bash
python crawler.py
```

#### 2-B. 로컬 스케줄러 (컴퓨터 켜둘 때)

```bash
python scheduler.py
```

## ⚙️ 설정 변경

### 크롤링 시간 변경

#### 로컬 스케줄러 (`config.py`)

```python
# 매일 오전 9시 실행 (기본값)
CRAWL_TIME = "09:00"

# 예: 오후 6시로 변경
CRAWL_TIME = "18:00"
```

#### GitHub Actions (`.github/workflows/daily-crawl.yml`)

```yaml
schedule:
  # 매일 한국시간 오전 9시 (UTC 0시)
  - cron: '0 0 * * *'
  
  # 예: 매일 한국시간 오후 6시 (UTC 9시)
  - cron: '0 9 * * *'
```

## 📊 출력 데이터

### data/ 폴더
- `news_2025-12-01.json` - 날짜별 뉴스 데이터 (JSON)

```json
[
  {
    "title": "Introducing Claude Opus 4.5",
    "url": "https://www.anthropic.com/news/claude-opus-4-5",
    "date": "Nov 24, 2025",
    "category": "Announcements",
    "scraped_at": "2025-12-01T09:00:00"
  }
]
```

### reports/ 폴더
- `anthropic_news_report_2025-12-01.md` - 날짜별 한국어 보고서

마크다운 형식의 보고서 포함:
- 날짜가 포함된 제목
- 카테고리별 분류
- 주요 통계
- 최신 뉴스 하이라이트
- 상세 뉴스 목록

## 🤖 자동화 방식

### GitHub Actions (추천) ⭐

**장점:**
- ✅ **컴퓨터를 안 켜도 됨!**
- ✅ 완전 무료 (월 2,000분 제공)
- ✅ 매일 자동 실행
- ✅ 결과가 자동으로 GitHub에 저장
- ✅ 수동 실행 버튼 제공

**작동 방식:**
1. 매일 한국시간 오전 9시에 GitHub 서버에서 자동 실행
2. 뉴스 크롤링 + 한국어 보고서 생성
3. 결과를 자동으로 GitHub 저장소에 커밋
4. 로컬에서 `git pull`로 최신 데이터 확인

### 로컬 스케줄러 (선택)

**특징:**
- 프로그램을 실행한 상태로 컴퓨터 켜두기
- 매일 오전 9시에 자동 실행
- `Ctrl+C`로 종료 가능

## 📝 파일 구조

### 날짜별 파일 관리

- **12월 1일**: `news_2025-12-01.json`, `anthropic_news_report_2025-12-01.md`
- **12월 2일**: `news_2025-12-02.json`, `anthropic_news_report_2025-12-02.md`
- **12월 3일**: `news_2025-12-03.json`, `anthropic_news_report_2025-12-03.md`

각 날짜마다 독립적인 파일로 관리되어 히스토리 추적이 쉽습니다.

## 🔧 수동 실행

### GitHub에서 수동 실행

1. 저장소 → Actions 탭
2. "Manual Crawl (수동 실행)" 선택
3. "Run workflow" 버튼 클릭
4. 약 1-2분 후 결과 확인

### 로컬에서 수동 실행

```bash
python crawler.py
```

## 📈 모니터링

### GitHub Actions 실행 로그
- Actions 탭에서 모든 실행 기록 확인
- 각 단계별 상세 로그 제공
- 실패 시 에러 메시지 확인 가능

### 로컬 로그
- `logs/crawler.log` 파일에서 확인
- 실시간 콘솔 출력

## 🛠️ 문제 해결

### GitHub Actions 관련
자세한 문제 해결은 [`docs/GITHUB_ACTIONS_SETUP.md`](docs/GITHUB_ACTIONS_SETUP.md) 참조

**주요 체크 사항:**
- ✅ Workflow permissions가 "Read and write"로 설정되어 있는지 확인
- ✅ `.gitignore`에서 JSON 파일이 제외되지 않았는지 확인
- ✅ 워크플로우 파일이 `.github/workflows/` 폴더에 있는지 확인

### 크롤링 오류
- 네트워크 연결 확인
- Anthropic 웹사이트 접속 가능 여부 확인
- `logs/crawler.log` 파일에서 상세 오류 확인

## 📚 문서

- [GitHub Actions 설정 가이드](docs/GITHUB_ACTIONS_SETUP.md) - 완전 자동화 설정 방법
- [config.py](config.py) - 모든 설정 옵션
- [.github/workflows/](.github/workflows/) - 워크플로우 정의

## 🎯 사용 예시

### 최신 데이터 확인

```bash
# GitHub에서 최신 데이터 받기
git pull origin main

# 오늘의 뉴스 데이터 확인
cat data/news_2025-12-01.json

# 오늘의 보고서 확인
cat reports/anthropic_news_report_2025-12-01.md
```

### 특정 날짜 데이터 확인

```bash
# 12월 1일 데이터
cat data/news_2025-12-01.json

# 12월 2일 데이터
cat data/news_2025-12-02.json
```

## 🔄 업데이트 전략

- **중복 제거**: URL 기준으로 자동 중복 제거
- **날짜별 스냅샷**: 매일 독립적인 파일 생성
- **Git 히스토리**: 모든 변경사항이 Git에 기록됨

## 💡 활용 방법

1. **정기 모니터링**: 매일 아침 9시에 최신 뉴스 자동 수집
2. **데이터 분석**: JSON 데이터를 활용해 뉴스 트렌드 분석
3. **보고서 확인**: 한국어 보고서로 쉽게 내용 파악
4. **히스토리 추적**: 날짜별 파일로 변화 추적

## 🆓 비용

- **GitHub Actions**: 완전 무료 (월 2,000분 제공)
- **실제 사용량**: 매일 약 2분 (월 60분 정도)
- **여유 분량**: 33배 이상

## 📄 라이선스

MIT License

---

**만든 날짜**: 2025년 12월 1일  
**최종 업데이트**: 2025년 12월 1일  
**상태**: ✅ 완전 자동화 완료

## ⭐ 추천 워크플로우

1. **초기 설정**: GitHub Actions 권한 설정 (1회)
2. **자동 실행**: 매일 오전 9시 자동 크롤링
3. **결과 확인**: 필요할 때 `git pull`로 최신 데이터 확인
4. **수동 실행**: 원할 때 언제든 GitHub에서 수동 실행

**이제 컴퓨터를 끄고 다른 일을 하세요. GitHub가 알아서 크롤링합니다! 🚀**
