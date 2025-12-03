# Hyeok Crawler

주요 언론사(동아일보, 조선일보, 중앙일보)의 6개 카테고리 뉴스를 자동 수집하는 크롤러 및 웹 포털입니다.

## 🌟 주요 기능

- **뉴스 티커 배너**: 실시간 뉴스 헤드라인을 세로 슬라이드로 표시 (네이버 증권 스타일)
- **자동 크롤링**: 6개 카테고리(정치/스포츠/경제/사회/국제/문화) × 3개 언론사 = 매일 90개 뉴스 수집
- **이미지 추출**: 각 기사의 대표 이미지 자동 수집 (Open Graph)
- **웹 포털**: 반응형 UI, 카테고리/언론사/날짜 필터링
- **GitHub Pages**: 정적 사이트로 무료 호스팅 가능
- **GitHub Actions**: 매일 오전 9시 20분 자동 실행

## 🎨 UI 기능

### 뉴스 티커 배너
- 모든 카테고리의 최신 뉴스를 세로 슬라이드로 표시
- 카테고리별 색상 뱃지 (정치: 파란색, 스포츠: 빨간색, 경제: 초록색, 사회: 보라색, 국제: 핫핑크, 문화: 노란색)
- 4.5초 간격으로 자동 전환 (1.2초 부드러운 애니메이션)
- 티커 클릭 시 해당 기사로 이동
- 반응형 디자인 (모바일 최적화)

### 반응형 네비게이션
- 데스크톱: 로고(좌측) + 카테고리 중앙 정렬
- 992px 이하: 로고(상단) + 카테고리 가로 배치
- 768px 이하: 로고 + 카테고리 세로 배치 (전체 화면)

## 📁 프로젝트 구조

```
news-crawler/
├── docs/                    # GitHub Pages 정적 사이트
│   ├── index.html          # 메인 페이지
│   ├── static/             # CSS, JS, 이미지
│   └── data/               # JSON 뉴스 데이터
├── crawler.py              # 크롤링 + 이미지 추출
├── parser.py               # HTML 파싱
├── report_generator.py     # 보고서 생성
├── config.py               # 설정
├── data/                   # 원본 데이터
└── reports/                # 보고서
```

## 🚀 빠른 시작

### 로컬 테스트

```bash
# docs 폴더에서 HTTP 서버 실행
cd docs
python -m http.server 8000

# 브라우저에서 localhost:8000 접속
```

### 크롤링 실행

```bash
# 필요한 라이브러리 설치
pip install -r requirements.txt

# 크롤링 실행 (90개 뉴스 + 이미지)
python crawler.py
```

### GitHub Pages 배포

1. **저장소 Public으로 변경** (Settings → Danger Zone)
2. **GitHub Pages 활성화**:
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`, Folder: `/docs`
   - Save
3. 완료! `https://<username>.github.io/<repo-name>` 에서 확인

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

## 🛠️ 기술 스택

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **UI Library**: Swiper.js (뉴스 티커 슬라이더)
- **Backend**: Python, BeautifulSoup4, Requests
- **Hosting**: GitHub Pages (정적 사이트)
- **Automation**: GitHub Actions (매일 오전 9시 20분 KST)

## 📈 수집 현황

| 카테고리 | 언론사 | 기사 수 | 이미지 | 티커 표시 |
|---------|--------|--------|--------|----------|
| 정치 | 동아/조선/중앙 | 15개 | ✅ | ✅ |
| 스포츠 | 동아/조선/중앙 | 15개 | ✅ | ✅ |
| 경제 | 동아/조선/중앙 | 15개 | ✅ | ✅ |
| 사회 | 동아/조선/중앙 | 15개 | ✅ | ✅ |
| 국제 | 동아/조선/중앙 | 15개 | ✅ | ✅ |
| 문화 | 동아/조선/중앙 | 15개 | ✅ | ✅ |
| **합계** | **18개 소스** | **90개** | **90개** | **90개** |

---

**최종 업데이트**: 2025년 12월 3일  
**버전**: 3.0 (사회/국제/문화 카테고리 추가)
