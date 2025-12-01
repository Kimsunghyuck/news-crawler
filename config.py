"""
Anthropic 뉴스 크롤러 설정 파일
"""

# 크롤링 대상 URL
BASE_URL = "https://www.anthropic.com"
NEWS_URL = f"{BASE_URL}/news"

# HTTP 요청 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

# 요청 간 대기 시간 (초)
REQUEST_DELAY = 2

# 타임아웃 설정 (초)
REQUEST_TIMEOUT = 30

# 데이터 저장 경로
DATA_DIR = "data"
NEWS_JSON_TEMPLATE = f"{DATA_DIR}/news_{{date}}.json"  # 날짜별 파일
LOGS_DIR = "logs"
LOG_FILE = f"{LOGS_DIR}/crawler.log"

# 보고서 저장 경로
REPORT_DIR = "reports"
REPORT_TEMPLATE = f"{REPORT_DIR}/anthropic_news_report_{{date}}.md"

# 스케줄링 설정
# 특정 시간에 실행 (매일 아침 9시)
CRAWL_TIME = "09:00"  # 매일 오전 9시에 실행

# 보고서 자동 생성 설정
AUTO_GENERATE_REPORT = True  # 크롤링 후 자동으로 보고서 생성

# 재시도 설정
MAX_RETRIES = 3
RETRY_DELAY = 5  # 재시도 전 대기 시간 (초)
