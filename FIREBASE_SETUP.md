# Firebase Email OTP 설정 가이드

## 1. Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com/) 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력 (예: `hyeok-news-crawler`)
4. Google Analytics는 선택사항 (학습 목적이면 비활성화 가능)
5. "프로젝트 만들기" 클릭

## 2. 웹 앱 추가

1. Firebase 프로젝트 대시보드에서 **웹 아이콘 (</>)** 클릭
2. 앱 닉네임 입력 (예: `Hyeok News Web`)
3. "Firebase Hosting 설정" 체크 해제 (GitHub Pages 사용 중)
4. "앱 등록" 클릭
5. Firebase SDK 구성 코드가 표시됨 → **복사해두기**

```javascript
// 예시 (실제 값은 다름)
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abcdef1234567890"
};
```

## 3. Authentication 활성화

1. 왼쪽 메뉴에서 **Authentication** 클릭
2. "시작하기" 버튼 클릭
3. **Sign-in method** 탭 선택
4. **이메일/비밀번호** 선택
5. 첫 번째 옵션만 활성화 (이메일/비밀번호)
6. "저장" 클릭

## 4. 프로젝트 설정 (중요!)

### 4-1. 승인된 도메인 추가
1. Authentication → Settings → Authorized domains
2. 기본적으로 `localhost`와 `*.firebaseapp.com`만 허용됨
3. GitHub Pages 도메인 추가:
   - 예: `your-username.github.io`
   - 또는 커스텀 도메인 (설정한 경우)

### 4-2. 이메일 템플릿 설정 (선택사항)
1. Authentication → Templates
2. "이메일 주소 확인" 템플릿 선택
3. 발신자 이름, 답장 이메일 수정 가능

## 5. Firebase Config 설정

Firebase 설정값을 auth.js에 직접 입력:

1. **docs/static/js/auth.js 파일 열기**

2. **17~24번 줄의 firebaseConfig 객체 수정**:

```javascript
// 수정 전 (기본값)
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "YOUR_AUTH_DOMAIN",
    projectId: "YOUR_PROJECT_ID",
    storageBucket: "YOUR_STORAGE_BUCKET",
    messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
    appId: "YOUR_APP_ID"
};

// 수정 후 (실제 값 입력)
const firebaseConfig = {
    apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",  // 실제 API Key 입력
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789012",
    appId: "1:123456789012:web:abcdef1234567890"
};
```

3. **actionCodeSettings의 url 수정 (65번 줄)**:

```javascript
// 로컬 테스트용
const actionCodeSettings = {
    url: 'http://localhost:8000',  // 로컬 개발 시
    handleCodeInApp: true,
};

// GitHub Pages 배포용
const actionCodeSettings = {
    url: 'https://your-username.github.io/document-test',  // 실제 도메인
    handleCodeInApp: true,
};
```

## 6. 로컬 테스트

```bash
cd docs
python -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```

## 주의사항

- **API Key 공개 문제**: Firebase API Key는 클라이언트에 노출되어도 괜찮습니다 (보안 규칙으로 보호됨)
- 하지만 GitHub 공개 저장소에 올리면 악용될 수 있으니 `.gitignore` 추가 권장
- **무료 플랜 제한**:
  - 월 10,000회 이메일 전송 (OTP 포함)
  - 일일 100회 SMS 전송 (SMS OTP 사용 시)
  - 학습 목적이면 충분함

## 다음 단계

Firebase 설정이 완료되면 코드에 통합하면 됩니다!
