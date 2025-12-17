# Python 3.11 베이스 이미지 사용
# slim 버전: 불필요한 패키지 제외, 용량 작음
FROM python:3.11-slim

# 작업 디렉토리 설정
# 컨테이너 내부에서 /app 폴더에서 작업
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 라이브러리 설치
# lxml을 위한 의존성 (libxml2, libxslt)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 먼저 복사 (캐싱 최적화)
# 의존성이 변경되지 않으면 이 레이어 재사용
COPY requirements.txt .

# Python 패키지 설치
# --no-cache-dir: pip 캐시 삭제로 이미지 크기 감소
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 전체 복사
COPY . .

# 필요한 디렉토리 생성
# 크롤링 데이터와 로그를 저장할 폴더
RUN mkdir -p data logs docs/data

# 환경변수 설정 (Python 출력 버퍼링 비활성화)
# 로그를 즉시 확인할 수 있게 함
ENV PYTHONUNBUFFERED=1

# 기본 명령어: 크롤러 실행
# docker run 시 자동 실행됨
CMD ["python", "crawler.py"]
