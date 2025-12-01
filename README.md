# 멀티 카테고리 뉴스 크롤러

AI, 정치, 스포츠, 경제 등 다양한 카테고리의 뉴스를 자동으로 크롤링하고 한국어 보고서로 변환하는 완전 자동화 시스템입니다.

## 🌟 주요 기능

- ✅ **멀티 카테고리 지원** - 정치, 스포츠, 경제 (3개 카테고리)
- ✅ **다중 뉴스 소스** - 중앙일보, 동아일보, 조선일보
- ✅ **"많이 본 뉴스" 타겟팅** - 각 신문사의 인기 기사 섹션 정확히 파싱
- ✅ **카테고리/소스별 독립 관리** - 체계적인 폴더 구조
- ✅ **날짜별 JSON 파일 저장** - 매일 별도 파일로 관리
- ✅ **한국어 보고서 자동 생성** - 개별 보고서 + 통합 보고서
- ✅ **GitHub Actions 완전 자동화** ⭐ - 컴퓨터 안 켜도 자동 실행!
- ✅ **매일 아침 9시 자동 실행** - GitHub 서버에서 자동 크롤링
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
├── config.py                    # 설정 파일 (모든 카테고리/소스 정의)
├── crawler.py                   # 크롤링 메인 로직 + 자동 보고서 생성
├── parser.py                    # HTML 파싱 함수 (9개 파서)
├── report_generator.py          # 한국어 보고서 생성 모듈
├── scheduler.py                 # 로컬 자동 스케줄링 모듈 (선택)
├── requirements.txt             # 필요한 라이브러리
├── data/                        # 크롤링 데이터 저장 폴더
│   ├── politics/
│   │   ├── donga/
│   │   │   └── news_2025-12-01.json    # 동아일보 정치 (5개)
│   │   ├── chosun/
│   │   │   └── news_2025-12-01.json    # 조선일보 정치 (5개)
│   │   └── joongang/
│   │       └── news_2025-12-01.json    # 중앙일보 정치 (5개)
│   ├── sports/
│   │   ├── donga/
│   │   │   └── news_2025-12-01.json    # 동아일보 스포츠 (5개)
│   │   ├── chosun/
│   │   │   └── news_2025-12-01.json    # 조선일보 스포츠 (5개)
│   │   └── joongang/
│   │       └── news_2025-12-01.json    # 중앙일보 스포츠 (5개)
│   └── economy/
│       ├── donga/
│       │   └── news_2025-12-01.json    # 동아일보 경제 (5개)
│       ├── chosun/
│       │   └── news_2025-12-01.json    # 조선일보 경제 (5개)
│       └── joongang/
│           └── news_2025-12-01.json    # 중앙일보 경제 (5개)
├── reports/                     # 보고서 저장 폴더
│   ├── politics/
│   │   ├── donga/
│   │   │   └── report_2025-12-01.md
│   │   ├── chosun/
│   │   │   └── report_2025-12-01.md
│   │   └── joongang/
│   │       └── report_2025-12-01.md
│   ├── sports/
│   │   ├── donga/
│   │   │   └── report_2025-12-01.md
│   │   ├── chosun/
│   │   │   └── report_2025-12-01.md
│   │   └── joongang/
│   │       └── report_2025-12-01.md
│   ├── economy/
│   │   ├── donga/
│   │   │   └── report_2025-12-01.md
│   │   ├── chosun/
│   │   │   └── report_2025-12-01.md
│   │   └── joongang/
│   │       └── report_2025-12-01.md
│   └── combined/
│       └── report_2025-12-01.md    # 전체 통합 보고서
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

### data/ 폴더 (카테고리/소스별 구조)

**정치 카테고리:**
- `data/politics/donga/news_2025-12-01.json` - 동아일보 정치 "많이 본 뉴스" (5개)
- `data/politics/chosun/news_2025-12-01.json` - 조선일보 정치 "많이 본 뉴스" (5개)
- `data/politics/joongang/news_2025-12-01.json` - 중앙일보 정치 "많이 본 뉴스" (5개)

**스포츠 카테고리:**
- `data/sports/donga/news_2025-12-01.json` - 동아일보 스포츠 "많이 본 뉴스" (5개)
- `data/sports/chosun/news_2025-12-01.json` - 조선일보 스포츠 "많이 본 뉴스" (5개)
- `data/sports/joongang/news_2025-12-01.json` - 중앙일보 스포츠 "많이 본 뉴스" (5개)

```json
[
  {
    "title": "정청래, 계엄 1년 또 내란몰이… \"2차 특검 검토 시점\"",
    "url": "https://www.chosun.com/politics/assembly/2025/12/01/...",
    "date": "2025-12-01",
    "category": "정치",
    "source": "조선일보",
    "scraped_at": "2025-12-01T16:07:29.024304",
    "main_category": "정치"
  }
]
```

### reports/ 폴더 (개별 + 통합 보고서)

**개별 소스별 보고서:**
- `reports/politics/donga/report_2025-12-01.md`
- `reports/politics/chosun/report_2025-12-01.md`
- `reports/politics/joongang/report_2025-12-01.md`
- `reports/sports/donga/report_2025-12-01.md`
- `reports/sports/chosun/report_2025-12-01.md`
- `reports/sports/joongang/report_2025-12-01.md`
- `reports/economy/donga/report_2025-12-01.md`
- `reports/economy/chosun/report_2025-12-01.md`
- `reports/economy/joongang/report_2025-12-01.md`

**통합 보고서:**
- `reports/combined/report_2025-12-01.md` - 전체 카테고리 통합 보고서 (45개 뉴스)

마크다운 형식의 보고서 포함:
- 날짜가 포함된 제목
- 카테고리별/소스별 분류
- 주요 통계 및 목차
- 최신 뉴스 하이라이트 (전체 상위 10개)
- 카테고리별 상세 뉴스 목록

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

**12월 1일 (총 45개 뉴스):**
- 정치: `data/politics/{donga,chosun,joongang}/news_2025-12-01.json` (5+5+5=15개)
- 스포츠: `data/sports/{donga,chosun,joongang}/news_2025-12-01.json` (5+5+5=15개)
- 경제: `data/economy/{donga,chosun,joongang}/news_2025-12-01.json` (5+5+5=15개)
- 통합 보고서: `reports/combined/report_2025-12-01.md`

**12월 2일 (총 45개 뉴스):**
- 동일한 구조로 `news_2025-12-02.json`, `report_2025-12-02.md` 생성

각 날짜마다 독립적인 파일로 관리되어 히스토리 추적이 쉽습니다.

## 🎯 카테고리별 뉴스 소스

### 정치 (15개 기사 - 각 5개씩)
- **동아일보** (https://www.donga.com/news/Politics) - "많이 본 정치 뉴스"
- **조선일보** (https://www.chosun.com/politics/) - "정치 많이 본 뉴스"
- **중앙일보** (https://www.joongang.co.kr/politics) - "정치 많이 본 기사"

### 스포츠 (15개 기사 - 각 5개씩)
- **동아일보** (https://www.donga.com/news/Sports) - "많이 본 스포츠 뉴스"
- **조선일보** (https://www.chosun.com/sports/) - "스포츠 많이 본 뉴스"
- **중앙일보** (https://www.joongang.co.kr/sports) - "스포츠 많이 본 기사"

### 경제 (15개 기사 - 각 5개씩)
- **동아일보** (https://www.donga.com/news/Economy) - "많이 본 경제 뉴스"
- **조선일보** (https://www.chosun.com/economy/) - "조선경제 많이 본 뉴스"
- **중앙일보** (https://www.joongang.co.kr/money) - "경제 많이 본 기사"

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

# 오늘의 통합 보고서 확인
cat reports/combined/report_2025-12-01.md

# 카테고리별 뉴스 데이터 확인
cat data/politics/chosun/news_2025-12-01.json
cat data/sports/joongang/news_2025-12-01.json
```

### 특정 카테고리/소스 확인

```bash
# 정치 뉴스 전체
ls data/politics/*/news_2025-12-01.json

# 스포츠 보고서 전체
ls reports/sports/*/report_2025-12-01.md

# 중앙일보 전체 (정치+스포츠)
cat data/politics/joongang/news_2025-12-01.json
cat data/sports/joongang/news_2025-12-01.json
```

### 특정 날짜 데이터 확인

```bash
# 12월 1일 통합 보고서
cat reports/combined/report_2025-12-01.md

# 12월 2일 통합 보고서
cat reports/combined/report_2025-12-02.md
```

## 🔄 업데이트 전략

- **중복 제거**: URL 기준으로 자동 중복 제거
- **날짜별 스냅샷**: 매일 독립적인 파일 생성
- **카테고리/소스별 독립 관리**: 각 소스마다 별도 JSON/보고서 파일
- **계층적 폴더 구조**: `data/{category}/{source}/news_{date}.json`
- **통합 보고서**: 모든 카테고리를 하나의 보고서로 통합
- **Git 히스토리**: 모든 변경사항이 Git에 기록됨

## 💡 활용 방법

1. **정기 모니터링**: 매일 아침 9시에 최신 뉴스 자동 수집 (45개)
2. **데이터 분석**: JSON 데이터를 활용해 뉴스 트렌드 분석
3. **보고서 확인**: 한국어 보고서로 쉽게 내용 파악
   - 개별 소스별 보고서: 특정 신문사만 집중 분석
   - 통합 보고서: 전체 카테고리 한눈에 보기
4. **히스토리 추적**: 날짜별 파일로 변화 추적
5. **"많이 본 뉴스" 트렌드**: 각 신문사의 인기 기사 동향 파악

## 🆓 비용

- **GitHub Actions**: 완전 무료 (월 2,000분 제공)
- **실제 사용량**: 매일 약 2분 (월 60분 정도)
- **여유 분량**: 33배 이상

## 📄 라이선스

MIT License

---

**만든 날짜**: 2025년 12월 1일  
**최종 업데이트**: 2025년 12월 1일  
**상태**: ✅ 멀티 카테고리 시스템 완료 (정치, 스포츠, 경제)  
**총 뉴스 수**: 45개 (정치 15개 + 스포츠 15개 + 경제 15개)

## ⭐ 추천 워크플로우

1. **초기 설정**: GitHub Actions 권한 설정 (1회)
2. **자동 실행**: 매일 오전 9시 자동 크롤링 (45개 뉴스)
3. **결과 확인**: 필요할 때 `git pull`로 최신 데이터 확인
4. **수동 실행**: 원할 때 언제든 GitHub에서 수동 실행
5. **보고서 활용**:
   - 전체 개요: `reports/combined/report_2025-12-01.md`
   - 특정 분야: `reports/{category}/{source}/report_2025-12-01.md`

**이제 컴퓨터를 끄고 다른 일을 하세요. GitHub가 알아서 크롤링합니다! 🚀**

## 📊 현재 수집 현황

| 카테고리 | 뉴스 소스 | 기사 수 | 특징 |
|---------|----------|--------|------|
| 정치 | 동아일보 | 5개 | "많이 본 정치 뉴스" |
| 정치 | 조선일보 | 5개 | "정치 많이 본 뉴스" |
| 정치 | 중앙일보 | 5개 | "정치 많이 본 기사" |
| 스포츠 | 동아일보 | 5개 | "많이 본 스포츠 뉴스" |
| 스포츠 | 조선일보 | 5개 | "스포츠 많이 본 뉴스" |
| 스포츠 | 중앙일보 | 5개 | "스포츠 많이 본 기사" |
| 경제 | 동아일보 | 5개 | "많이 본 경제 뉴스" |
| 경제 | 조선일보 | 5개 | "조선경제 많이 본 뉴스" |
| 경제 | 중앙일보 | 5개 | "경제 많이 본 기사" |
| **합계** | **9개 소스** | **45개** | **매일 자동 업데이트** |
