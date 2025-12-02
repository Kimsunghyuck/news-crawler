# GitHub Pages 배포 가이드

이 프로젝트는 GitHub Pages를 통해 정적 웹사이트로 배포할 수 있습니다.

## 🌐 배포 방법

### 1. GitHub Pages 활성화

1. GitHub 저장소 페이지로 이동
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Pages** 선택
4. **Source** 섹션에서:
   - **Branch**: `main` 선택
   - **Folder**: `/docs` 선택
   - **Save** 버튼 클릭

### 2. 배포 완료!

약 1-2분 후 웹사이트가 다음 주소에서 접속 가능합니다:
```
https://<username>.github.io/<repository-name>/
```

예시: `https://kimsunghyuck.github.io/news-crawler/`

## 📊 작동 방식

### 정적 웹사이트 구조

```
docs/
├── index.html           # 메인 페이지
├── static/
│   ├── css/
│   │   └── style.css   # 스타일시트
│   ├── js/
│   │   └── main.js     # JavaScript (Flask API 제거됨)
│   └── images/         # 이미지 파일들
└── data/               # 뉴스 JSON 데이터
    ├── politics/
    ├── sports/
    └── economy/
```

### 데이터 흐름

1. **크롤링**: GitHub Actions가 매일 오전 9시 20분에 자동 실행
2. **데이터 생성**: `data/` 폴더에 JSON 파일 생성
3. **복사**: `docs/data/` 폴더로 데이터 복사
4. **커밋**: 변경사항을 자동으로 커밋 & 푸시
5. **배포**: GitHub Pages가 자동으로 업데이트

### JavaScript가 JSON 직접 로드

Flask 서버 없이 JavaScript가 직접 JSON 파일을 fetch합니다:

```javascript
// 예시: 정치 > 동아일보 > 2025-12-02
const response = await fetch('data/politics/donga/news_2025-12-02.json');
const newsData = await response.json();
```

## 🔄 업데이트 방법

### 자동 업데이트 (GitHub Actions)

매일 오전 9시 20분에 자동으로:
1. 뉴스 크롤링
2. `docs/data/` 폴더 업데이트
3. GitHub에 자동 푸시
4. GitHub Pages 자동 재배포

### 수동 업데이트

로컬에서 크롤링 후 배포:

```bash
# 1. 크롤링 실행
python crawler.py

# 2. docs 폴더로 데이터 복사
cp -r data/* docs/data/

# 3. Git 커밋 & 푸시
git add docs/data/
git commit -m "Update news data"
git push origin main

# 4. 약 1-2분 후 웹사이트 자동 업데이트
```

## 🎯 장점

✅ **완전 무료**: GitHub Pages 무료 호스팅
✅ **빠른 속도**: CDN을 통한 전 세계 배포
✅ **자동 HTTPS**: 보안 연결 자동 제공
✅ **자동 배포**: Git 푸시만 하면 자동 업데이트
✅ **서버 불필요**: Flask 서버 없이 작동
✅ **유지보수 간편**: 정적 파일만 관리

## 🔧 문제 해결

### 페이지가 표시되지 않을 때

1. **GitHub Pages 설정 확인**
   - Settings → Pages → Branch가 `main`, Folder가 `/docs`인지 확인

2. **파일 경로 확인**
   - `docs/index.html` 파일이 있는지 확인
   - `docs/data/` 폴더에 JSON 파일이 있는지 확인

3. **배포 상태 확인**
   - Actions 탭에서 워크플로우 실행 상태 확인
   - Pages 섹션에서 배포 URL 확인

### 데이터가 업데이트되지 않을 때

1. **GitHub Actions 로그 확인**
   - Actions 탭에서 최근 실행 로그 확인

2. **브라우저 캐시 삭제**
   - `Ctrl + Shift + R` (하드 리프레시)

3. **데이터 파일 확인**
   - `docs/data/` 폴더에 최신 날짜 파일 있는지 확인

## 📱 접속 방법

배포 후 웹사이트 접속:

```
https://<username>.github.io/<repository-name>/
```

예시:
- `https://kimsunghyuck.github.io/news-crawler/`

## 🚀 추가 옵션

### 커스텀 도메인 사용

1. Settings → Pages → Custom domain에 도메인 입력
2. DNS 설정에서 CNAME 레코드 추가:
   ```
   CNAME: <username>.github.io
   ```

### 로컬 테스트

정적 웹사이트를 로컬에서 테스트:

```bash
# Python 간단한 HTTP 서버
cd docs
python -m http.server 8000

# 브라우저에서 접속
# http://localhost:8000
```

## 📊 비교: Flask vs GitHub Pages

| 항목 | Flask (이전) | GitHub Pages (현재) |
|------|-------------|-------------------|
| 호스팅 비용 | 유료/무료 티어 | 완전 무료 |
| 서버 관리 | 필요 | 불필요 |
| 배포 속도 | 느림 (5-10분) | 빠름 (1-2분) |
| HTTPS | 설정 필요 | 자동 제공 |
| CDN | 추가 설정 | 자동 제공 |
| 유지보수 | 복잡 | 간단 |

---

**참고**: 이 방식은 정적 웹사이트로, Flask 서버 없이 작동합니다. 모든 기능이 클라이언트 사이드 JavaScript로 구현되어 있습니다.
