# 멀티 카테고리 뉴스 크롤러 + 웹 포털

정치, 스포츠, 경제 등 다양한 카테고리의 뉴스를 자동으로 크롤링하고, 웹 인터페이스로 제공하는 완전 자동화 시스템입니다.

## 🌟 주요 기능

### 크롤링 시스템
- ✅ **멀티 카테고리 지원** - 정치, 스포츠, 경제 (3개 카테고리)
- ✅ **다중 뉴스 소스** - 동아일보, 조선일보, 중앙일보
- ✅ **"많이 본 뉴스" 타겟팅** - 각 신문사의 인기 기사 섹션 정확히 파싱
- ✅ **기사 이미지 자동 수집** - 각 기사 URL에서 대표 이미지 추출 (Open Graph)
- ✅ **카테고리/소스별 독립 관리** - 체계적인 폴더 구조
- ✅ **날짜별 JSON 파일 저장** - 매일 별도 파일로 관리
- ✅ **한국어 보고서 자동 생성** - 개별 보고서 + 통합 보고서
- ✅ **중복 제거 및 증분 업데이트**
- ✅ **에러 처리 및 재시도 로직**
- ✅ **상세한 로깅**

### 웹 포털 (NEW! 🎉)
- ✅ **현대적인 웹 인터페이스** - HS Hyosung Advanced Materials 스타일
- ✅ **배너 슬라이더** - 최신 뉴스 4개를 자동 회전 (Swiper.js)
- ✅ **카테고리 네비게이션** - 호버 드롭다운 메뉴
- ✅ **신문사별 필터링** - 동아일보, 조선일보, 중앙일보 선택
- ✅ **날짜 선택 기능** - 특정 날짜의 기사 조회
- ✅ **반응형 디자인** - 모바일, 태블릿, 데스크톱 완벽 지원
- ✅ **이미지 지원** - 기사 썸네일 이미지 표시
- ✅ **빈 상태 처리** - 기사가 없을 때 안내 메시지
- ✅ **이미지 오류 처리** - 이미지 로드 실패 시 대체 UI

### 자동화 (선택)
- ✅ **GitHub Actions 완전 자동화** ⭐ - 컴퓨터 안 켜도 자동 실행!
- ✅ **매일 아침 9시 자동 실행** - GitHub 서버에서 자동 크롤링

## 📁 프로젝트 구조

```
news-crawler/
├── .github/
│   └── workflows/
│       ├── daily-crawl.yml           # 매일 자동 크롤링 (GitHub Actions)
│       └── manual-crawl.yml          # 수동 실행 워크플로우
├── web/                              # 웹 포털 (Flask)
│   ├── app.py                        # Flask 서버
│   ├── templates/
│   │   ├── base.html                 # 기본 레이아웃
│   │   ├── index.html                # 메인 페이지
│   │   └── components/
│   │       ├── navigation.html       # 네비게이션 바
│   │       ├── banner_slider.html    # 배너 슬라이더
│   │       └── footer.html           # 푸터
│   └── static/
│       ├── css/
│       │   └── style.css             # 전체 스타일시트
│       ├── js/
│       │   └── main.js               # 메인 JavaScript
│       └── images/
│           ├── mainIcon.png          # 메인 로고
│           ├── donga1.png            # 동아일보 로고
│           ├── chosun.png            # 조선일보 로고
│           ├── joongang.png          # 중앙일보 로고
│           └── favicon.ico           # 파비콘
├── config.py                         # 설정 파일 (모든 카테고리/소스 정의)
├── crawler.py                        # 크롤링 메인 로직 + 이미지 추출
├── parser.py                         # HTML 파싱 함수 (9개 파서)
├── report_generator.py               # 한국어 보고서 생성 모듈
├── scheduler.py                      # 로컬 자동 스케줄링 모듈 (선택)
├── requirements.txt                  # 필요한 라이브러리
├── data/                             # 크롤링 데이터 저장 폴더
│   ├── politics/
│   │   ├── donga/
│   │   │   └── news_2025-12-02.json  # 동아일보 정치 (5개) + 이미지 URL
│   │   ├── chosun/
│   │   │   └── news_2025-12-02.json  # 조선일보 정치 (5개) + 이미지 URL
│   │   └── joongang/
│   │       └── news_2025-12-02.json  # 중앙일보 정치 (5개) + 이미지 URL
│   ├── sports/
│   │   ├── donga/
│   │   │   └── news_2025-12-02.json  # 동아일보 스포츠 (5개) + 이미지 URL
│   │   ├── chosun/
│   │   │   └── news_2025-12-02.json  # 조선일보 스포츠 (5개) + 이미지 URL
│   │   └── joongang/
│   │       └── news_2025-12-02.json  # 중앙일보 스포츠 (5개) + 이미지 URL
│   └── economy/
│       ├── donga/
│       │   └── news_2025-12-02.json  # 동아일보 경제 (5개) + 이미지 URL
│       ├── chosun/
│       │   └── news_2025-12-02.json  # 조선일보 경제 (5개) + 이미지 URL
│       └── joongang/
│           └── news_2025-12-02.json  # 중앙일보 경제 (5개) + 이미지 URL
├── reports/                     # 보고서 저장 폴더
│   ├── politics/
│   │   ├── donga/
│   │   │   └── report_2025-12-02.md
│   │   ├── chosun/
│   │   │   └── report_2025-12-02.md
│   │   └── joongang/
│   │       └── report_2025-12-02.md
│   ├── sports/
│   │   ├── donga/
│   │   │   └── report_2025-12-02.md
│   │   ├── chosun/
│   │   │   └── report_2025-12-02.md
│   │   └── joongang/
│   │       └── report_2025-12-02.md
│   ├── economy/
│   │   ├── donga/
│   │   │   └── report_2025-12-02.md
│   │   ├── chosun/
│   │   │   └── report_2025-12-02.md
│   │   └── joongang/
│   │       └── report_2025-12-02.md
│   └── combined/
│       └── report_2025-12-02.md    # 전체 통합 보고서
├── logs/                        # 로그 파일 폴더
│   └── crawler.log
└── docs/
    └── GITHUB_ACTIONS_SETUP.md  # GitHub Actions 설정 가이드
```

## 🚀 빠른 시작

### 웹 포털 실행 (추천) 🌐

```bash
# 1. 필요한 라이브러리 설치
pip install -r requirements.txt

# 2. 웹 서버 실행
cd web
python app.py

# 3. 브라우저에서 접속
# http://127.0.0.1:5000
```

**웹 포털 기능:**
- 📰 최신 뉴스 배너 슬라이더
- 🗂️ 카테고리별 뉴스 조회 (정치/스포츠/경제)
- 📰 신문사별 필터링 (동아/조선/중앙일보)
- 📅 날짜별 기사 조회
- 🖼️ 기사 이미지 표시
- 📱 반응형 디자인 (모바일/태블릿/PC)

### 크롤링 실행

#### 단일 실행 (한 번만 크롤링)

```bash
python crawler.py
```

**실행 결과:**
- 45개 뉴스 크롤링 (정치 15개 + 스포츠 15개 + 경제 15개)
- 각 기사의 이미지 URL 자동 추출 (Open Graph 메타 태그)
- JSON 파일 저장 (`data/{category}/{source}/news_{date}.json`)
- 한국어 보고서 자동 생성 (`reports/`)

#### 로컬 스케줄러 (매일 자동 실행)

```bash
python scheduler.py
```

### GitHub Actions 자동화 (선택) ⭐

**컴퓨터를 켜지 않아도 매일 자동으로 크롤링합니다!**

1. **저장소 Fork 또는 Clone**
2. **GitHub Actions 권한 설정**
   - 저장소 → Settings → Actions → General
   - Workflow permissions → "Read and write permissions" 선택
   - Save 클릭
3. **완료!** 매일 오전 9시에 자동 실행됩니다.

자세한 설정 방법: [`docs/GITHUB_ACTIONS_SETUP.md`](docs/GITHUB_ACTIONS_SETUP.md)

## 📊 출력 데이터 구조

### JSON 파일 (이미지 URL 포함!)

```json
[
  {
    "title": "李 \"내란 가담자 확실한 처벌 필요…가혹한 조사는 없어야\"",
    "url": "https://www.donga.com/news/Politics/article/all/20251202/132885245/2",
    "date": "2025-12-02",
    "category": "정치",
    "source": "동아일보",
    "image_url": "https://dimg.donga.com/wps/NEWS/IMAGE/2025/12/02/132885246.2.jpg",
    "scraped_at": "2025-12-02T16:10:05.000062+09:00",
    "main_category": "정치"
  }
]
```

**주요 필드:**
- `title`: 기사 제목
- `url`: 기사 전체 URL
- `date`: 발행 날짜
- `category`: 카테고리 (한글)
- `source`: 신문사 이름
- `image_url`: 기사 대표 이미지 URL ⭐ (NEW!)
- `scraped_at`: 크롤링 시간
- `main_category`: 메인 카테고리

### 이미지 추출 방식

크롤러는 각 기사 URL에 접속하여 다음 순서로 이미지를 추출합니다:

1. **Open Graph 이미지** (`og:image` 메타 태그) - 최우선
2. **Twitter 카드 이미지** (`twitter:image` 메타 태그)
3. **본문 첫 번째 이미지** (article 태그 내 img)

**지원 신문사:**
- 동아일보: `https://dimg.donga.com/wps/NEWS/IMAGE/...`
- 조선일보: `https://www.chosun.com/resizer/v2/...`
- 중앙일보: `https://pds.joongang.co.kr/news/FbMetaImage/...`

## 🎨 웹 포털 기능 상세

### 배너 슬라이더
- **Swiper.js** 기반 자동 슬라이드
- 최신 뉴스 4개 표시
- 자동 재생 (5초 간격)
- 이미지 + 제목 + 카테고리 표시

### 네비게이션
- **호버 드롭다운**: 카테고리에 마우스를 올리면 신문사 목록 표시
- **통합 드롭다운**: 모든 카테고리가 동일한 신문사 옵션 공유
- **화이트 테마**: 깔끔한 흰색 배경 디자인

### 뉴스 카드
- **그리드 레이아웃**: 반응형 3-4열 그리드
- **이미지 썸네일**: 기사 대표 이미지 표시
- **이미지 오류 처리**: 
  - 이미지 로드 실패 시 대체 UI 표시
  - 사진 아이콘 + "이미지 준비중" 텍스트
  - 그라디언트 배경
- **호버 효과**: 카드 위로 마우스 올리면 살짝 올라감
- **클릭 동작**: 새 탭에서 원문 기사 열기

### 날짜 선택기
- **달력 UI**: HTML5 date input
- **날짜 범위**: 오늘까지만 선택 가능
- **실시간 업데이트**: 날짜 변경 시 자동으로 해당 날짜 기사 로드

### 빈 상태 처리
- **데이터 없음**: 선택한 날짜에 기사가 없을 때
  - 문서 아이콘 표시
  - "해당 날짜에 대한 기사가 존재하지 않습니다" 메시지
  - "다른 날짜를 선택해주세요" 안내

### REST API 엔드포인트

```python
GET /api/latest?limit=4          # 최신 뉴스 (배너용)
GET /api/news/{category}/{source}?date={date}  # 특정 카테고리/소스/날짜
GET /api/categories              # 카테고리 목록
GET /api/sources                 # 신문사 목록
GET /api/dates                   # 사용 가능한 날짜 목록
GET /api/stats                   # 통계 정보
```

## 🛠️ 기술 스택

### Backend
- **Flask 3.0.0**: 웹 서버
- **Flask-CORS 4.0.0**: CORS 처리
- **BeautifulSoup4**: HTML 파싱
- **Requests**: HTTP 요청
- **lxml**: XML/HTML 파서

### Frontend
- **HTML5 + CSS3**: 마크업 및 스타일
- **Vanilla JavaScript**: 클라이언트 로직
- **Swiper.js 11**: 배너 슬라이더
- **Jinja2**: 템플릿 엔진

### 크롤링
- **Python 3.x**
- **BeautifulSoup4 + lxml**: HTML 파싱
- **Requests**: 웹 페이지 가져오기
- **JSON**: 데이터 저장

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

## ⚙️ 설정 변경

### 크롤링 설정 (`config.py`)

```python
# 크롤링할 최대 기사 수
MAX_ARTICLES_PER_SOURCE = 5

# 요청 간 대기 시간 (초)
REQUEST_DELAY = 2

# 크롤링 시간 (로컬 스케줄러)
CRAWL_TIME = "09:00"
```

### GitHub Actions 크롤링 시간 변경

`.github/workflows/daily-crawl.yml`:
```yaml
schedule:
  # 매일 한국시간 오전 9시 (UTC 0시)
  - cron: '0 0 * * *'
```

## 📈 모니터링

### 웹 포털
- 실시간 뉴스 확인: `http://127.0.0.1:5000`
- 카테고리/신문사별 필터링
- 날짜별 기사 조회

### 로그 파일
- `logs/crawler.log`: 크롤링 상세 로그
- Flask 콘솔: 웹 서버 접속 로그

### GitHub Actions
- Actions 탭에서 실행 기록 확인
- 각 단계별 상세 로그
- 실패 시 에러 메시지

## 💡 활용 방법

1. **웹 포털 사용** 🌐
   - `python web/app.py` 실행
   - 브라우저에서 `http://127.0.0.1:5000` 접속
   - 카테고리/신문사/날짜 선택하여 뉴스 조회

2. **정기 모니터링**
   - 매일 아침 9시에 자동 크롤링
   - 웹 포털에서 최신 뉴스 확인

3. **데이터 분석**
   - JSON 데이터를 활용한 뉴스 트렌드 분석
   - 신문사별 기사 비교

4. **히스토리 추적**
   - 날짜별 파일로 변화 추적
   - Git 히스토리로 과거 데이터 확인

## 🎯 주요 개선 사항 (2025-12-02)

### 이미지 수집 기능 추가 ⭐
- ✅ 각 기사 URL에서 대표 이미지 자동 추출
- ✅ Open Graph 메타 태그 우선 사용
- ✅ 모든 신문사 이미지 URL 정상 수집
- ✅ 상대 경로 → 절대 경로 자동 변환

### 웹 포털 구축 🌐
- ✅ Flask 기반 REST API 서버
- ✅ 현대적인 UI/UX (HS Hyosung 스타일)
- ✅ 배너 슬라이더 (Swiper.js)
- ✅ 반응형 디자인
- ✅ 이미지 썸네일 표시
- ✅ 날짜별 기사 조회
- ✅ 빈 상태 처리
- ✅ 이미지 오류 처리 (대체 UI)

### UI/UX 개선
- ✅ 호버 기반 네비게이션
- ✅ 화이트 테마
- ✅ 로딩 상태 표시
- ✅ 에러 처리
- ✅ 빈 상태 메시지 (아이콘 + 텍스트)
- ✅ 이미지 로드 실패 시 "이미지 준비중" UI

## 📊 현재 수집 현황

| 카테고리 | 뉴스 소스 | 기사 수 | 이미지 | 특징 |
|---------|----------|--------|--------|------|
| 정치 | 동아일보 | 5개 | ✅ | "많이 본 정치 뉴스" |
| 정치 | 조선일보 | 5개 | ✅ | "정치 많이 본 뉴스" |
| 정치 | 중앙일보 | 5개 | ✅ | "정치 많이 본 기사" |
| 스포츠 | 동아일보 | 5개 | ✅ | "많이 본 스포츠 뉴스" |
| 스포츠 | 조선일보 | 5개 | ✅ | "스포츠 많이 본 뉴스" |
| 스포츠 | 중앙일보 | 5개 | ✅ | "스포츠 많이 본 기사" |
| 경제 | 동아일보 | 5개 | ✅ | "많이 본 경제 뉴스" |
| 경제 | 조선일보 | 5개 | ✅ | "조선경제 많이 본 뉴스" |
| 경제 | 중앙일보 | 5개 | ✅ | "경제 많이 본 기사" |
| **합계** | **9개 소스** | **45개** | **45개** | **매일 자동 업데이트** |

## 🚀 다음 단계

- [ ] 검색 기능 추가
- [ ] 북마크 기능
- [ ] 공유 기능
- [ ] 다크 모드
- [ ] 모바일 앱 (PWA)
- [ ] 알림 기능
- [ ] 통계 대시보드

## 📄 라이선스

MIT License

---

**만든 날짜**: 2025년 12월 1일  
**웹 포털 추가**: 2025년 12월 2일  
**이미지 수집 추가**: 2025년 12월 2일  
**최종 업데이트**: 2025년 12월 2일  
**상태**: ✅ 웹 포털 + 이미지 수집 완료  
**총 뉴스 수**: 45개 (정치 15개 + 스포츠 15개 + 경제 15개)  
**이미지 수집**: ✅ 100% (45/45개)
