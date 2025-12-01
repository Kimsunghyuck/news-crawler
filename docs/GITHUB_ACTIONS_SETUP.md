# 🚀 GitHub Actions 설정 가이드

이 가이드는 GitHub Actions를 사용하여 컴퓨터를 켜지 않아도 자동으로 뉴스를 크롤링하는 방법을 설명합니다.

## 📋 목차

1. [GitHub Actions란?](#github-actions란)
2. [설정 방법](#설정-방법)
3. [사용 방법](#사용-방법)
4. [문제 해결](#문제-해결)

## 🤖 GitHub Actions란?

GitHub Actions는 GitHub에서 제공하는 **무료 클라우드 자동화 서비스**입니다.

### 장점
- ✅ **완전 무료** - 월 2,000분 무료 (충분함)
- ✅ **컴퓨터 불필요** - GitHub 서버에서 실행
- ✅ **자동 저장** - 크롤링 결과를 자동으로 저장
- ✅ **24/7 작동** - 내 컴퓨터가 꺼져도 작동

### 동작 방식

```
매일 한국시간 오전 9시
    ↓
GitHub 서버가 자동으로 프로그램 실행
    ↓
뉴스 크롤링 + 보고서 생성
    ↓
결과를 자동으로 GitHub 저장소에 커밋
    ↓
완료!
```

## ⚙️ 설정 방법

### 1단계: 워크플로우 파일 업로드 ✅

이미 완료되었습니다! 다음 파일들이 포함되어 있습니다:
- `.github/workflows/daily-crawl.yml` - 매일 자동 실행
- `.github/workflows/manual-crawl.yml` - 수동 실행

### 2단계: GitHub Actions 권한 설정 (필수!)

1. GitHub 저장소 페이지로 이동: https://github.com/Kimsunghyuck/news-crawler
2. 상단 **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Actions** → **General** 클릭
4. 페이지 하단 **Workflow permissions** 섹션 찾기
5. **Read and write permissions** 선택 ✅
6. **Allow GitHub Actions to create and approve pull requests** 체크 ✅
7. **Save** 버튼 클릭

### 3단계: 워크플로우 활성화

1. 저장소 상단 **Actions** 탭 클릭
2. 워크플로우 목록에서 확인:
   - `Daily Anthropic News Crawl` (매일 자동 실행)
   - `Manual Crawl (수동 실행)` (수동 실행)

## 🎯 사용 방법

### 자동 실행 (추천)

설정 완료 후 **아무것도 하지 않아도** 됩니다!

- 매일 한국시간 오전 9시에 자동으로 실행
- 크롤링 결과가 자동으로 GitHub에 저장됨
- `data/` 및 `reports/` 폴더에 날짜별 파일 생성

### 수동 실행

언제든 수동으로 실행 가능:

1. GitHub 저장소 → **Actions** 탭
2. 왼쪽에서 **Manual Crawl (수동 실행)** 워크플로우 선택
3. 우측 **Run workflow** 버튼 클릭
4. **Run workflow** 다시 클릭
5. 실행 완료까지 약 1-2분 소요

### 실행 결과 확인

1. **Actions** 탭에서 실행 기록 확인
2. 특정 실행을 클릭하여 상세 로그 확인
3. 저장소의 `data/`, `reports/` 폴더에서 결과 파일 확인

## 📊 스케줄 변경

매일 9시가 아닌 다른 시간에 실행하려면:

### `.github/workflows/daily-crawl.yml` 파일 수정

```yaml
schedule:
  # 현재: 매일 한국시간 오전 9시 (UTC 0시)
  - cron: '0 0 * * *'
  
  # 예시: 매일 한국시간 오후 6시 (UTC 9시)
  - cron: '0 9 * * *'
  
  # 예시: 매일 한국시간 오전 6시, 오후 6시 (UTC 21시, 9시)
  - cron: '0 21,9 * * *'
```

### Cron 표현식 가이드

```
분 시 일 월 요일
*  *  *  *  *

예시:
'0 0 * * *'   - 매일 UTC 0시 (한국시간 오전 9시)
'0 9 * * *'   - 매일 UTC 9시 (한국시간 오후 6시)
'0 */6 * * *' - 6시간마다
'0 0 * * 1'   - 매주 월요일 UTC 0시
```

**중요:** GitHub는 UTC 시간을 사용합니다.
- 한국시간 = UTC + 9시간
- 한국시간 오전 9시 = UTC 0시

## 🔍 실행 로그 확인

### 1. GitHub에서 확인

1. **Actions** 탭 → 실행 기록 클릭
2. 각 단계별 로그 확인 가능
3. 에러 발생 시 상세 내용 확인

### 2. 저장소에서 확인

`logs/crawler.log` 파일에 크롤링 로그 저장됨

## ❓ 문제 해결

### Q1: 워크플로우가 실행되지 않아요

**확인 사항:**
- `Settings` → `Actions` → `General`에서 Actions가 활성화되어 있는지 확인
- `Workflow permissions`가 `Read and write permissions`로 설정되어 있는지 확인
- 저장소가 Public 또는 Private인지 확인 (Private도 작동함)

### Q2: 커밋 권한 오류가 발생해요

**해결 방법:**
1. `Settings` → `Actions` → `General`
2. `Workflow permissions` → `Read and write permissions` 선택
3. `Allow GitHub Actions to create and approve pull requests` 체크
4. `Save` 클릭

### Q3: 크롤링은 성공했는데 파일이 저장소에 없어요

**확인 사항:**
- Actions 탭에서 실행 로그의 "결과 파일 커밋" 단계 확인
- 새로운 데이터가 없으면 커밋이 생성되지 않을 수 있음
- 브라우저 새로고침 후 `data/`, `reports/` 폴더 확인

### Q4: 특정 시간에 실행되지 않아요

**GitHub Actions의 제약:**
- 예약된 워크플로우는 최대 15분 정도 지연될 수 있음
- GitHub 서버 부하에 따라 지연 가능
- 정확한 시간이 중요하면 외부 서비스(AWS Lambda 등) 고려

### Q5: 무료 사용량이 초과될까요?

**걱정 없습니다:**
- 월 2,000분 무료 제공
- 한 번 실행 시 약 1-2분 소요
- 매일 실행해도 월 60분 정도만 사용
- 33배 이상 여유

## 📈 모니터링

### 이메일 알림 설정

실행 실패 시 이메일 받기:

1. GitHub 계정 → `Settings`
2. 좌측 `Notifications`
3. `Actions` 섹션 → `Send notifications for failed workflows` 체크

### 실행 기록 확인

- **Actions** 탭에서 모든 실행 기록 확인 가능
- 최근 30일간의 로그 보관
- 각 실행의 성공/실패 상태 확인

## 🎉 완료!

이제 컴퓨터를 켜지 않아도 매일 자동으로 Anthropic 뉴스가 크롤링되고 보고서가 생성됩니다!

## 📚 추가 자료

- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Cron 표현식 생성기](https://crontab.guru/)
- [GitHub Actions 무료 사용량](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)
