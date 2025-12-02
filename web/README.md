# Hyeok Crawler 뉴스 포털 웹 애플리케이션

Flask 기반 뉴스 크롤러 웹 인터페이스

## 시작하기

### 1. 의존성 설치

```bash
pip install -r ../requirements.txt
```

### 2. 로고 이미지 배치

`static/images/` 폴더에 다음 이미지들을 배치하세요:
- `shinhyeok-logo.png` - Hyeok Crawler 메인 로고
- `donga-logo.png` - 동아일보 로고
- `chosun-logo.png` - 조선일보 로고
- `joongang-logo.png` - 중앙일보 로고
- `favicon.ico` - 파비콘
- `no-image.png` - 기본 이미지

### 3. 서버 실행

```bash
python app.py
```

서버가 시작되면 브라우저에서 `http://localhost:5000` 접속

## 주요 기능

- ✅ 카테고리별 뉴스 필터링 (정치, 스포츠, 경제)
- ✅ 신문사별 뉴스 선택 (동아, 조선, 중앙)
- ✅ 날짜별 뉴스 조회
- ✅ 최신 뉴스 배너 슬라이더 (자동 재생)
- ✅ 반응형 디자인
- ✅ 뉴스 카드 애니메이션

## API 엔드포인트

### GET /api/categories
카테고리 목록 반환

### GET /api/sources
신문사 목록 반환

### GET /api/news/:category/:source
특정 카테고리와 신문사의 뉴스 조회
- Query: `date` (YYYY-MM-DD)

### GET /api/latest
최신 뉴스 조회 (배너용)
- Query: `limit` (기본값: 4)

### GET /api/dates/:category/:source
사용 가능한 날짜 목록 반환

## 디렉토리 구조

```
web/
├── app.py                 # Flask 서버
├── static/
│   ├── css/
│   │   └── style.css     # 메인 스타일시트
│   ├── js/
│   │   └── main.js       # 메인 JavaScript
│   └── images/           # 이미지 파일
├── templates/
│   ├── base.html         # 기본 레이아웃
│   ├── index.html        # 메인 페이지
│   └── components/       # 재사용 컴포넌트
│       ├── header.html
│       ├── navigation.html
│       ├── banner_slider.html
│       └── footer.html
└── README.md
```

## 기술 스택

- **백엔드**: Flask, Flask-CORS
- **프론트엔드**: HTML5, CSS3, JavaScript (Vanilla)
- **라이브러리**: Swiper.js (슬라이더)
- **디자인**: 반응형 웹 디자인

## 개발 정보

- 개발자: Kimsunghyuck
- 참고 디자인: HS Hyosung Advanced Materials
- 저장소: https://github.com/Kimsunghyuck/news-crawler
