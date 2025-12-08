"""
멀티 카테고리 뉴스 크롤러 설정 파일
AI, 정치, 스포츠, 경제 4개 카테고리별 뉴스 소스 관리
"""

# 카테고리 영문 매핑
CATEGORY_EN_MAP = {
    # 'AI': 'ai',  # AI는 매일 업데이트되지 않아 주석처리
    '정치': 'politics',
    '스포츠': 'sports',
    '경제': 'economy',
    '사회': 'society',
    '국제': 'international',
    '문화': 'culture'
}

# 소스 이름 영문 매핑
SOURCE_EN_MAP = {
    'Anthropic': 'anthropic',
    '동아일보': 'donga',
    '조선일보': 'chosun',
    '중앙일보': 'joongang'
}

# 카테고리별 뉴스 소스 설정
NEWS_SOURCES = {
    # 'AI': [  # AI는 매일 업데이트되지 않아 주석처리
    #     {
    #         'name': 'Anthropic',
    #         'url': 'https://www.anthropic.com/news',
    #         'parser': 'anthropic_news',  # parser.py의 parse_anthropic_news 함수 사용
    #         'max_articles': 20
    #     },
    #     # 추가 AI 뉴스 소스는 여기에 추가
    # ],
    '정치': [
        {
            'name': '동아일보',
            'url': 'https://www.donga.com/news/Politics',
            'parser': 'donga_politics',  # parser.py의 parse_donga_politics 함수 사용
            'max_articles': 5
        },
        {
            'name': '조선일보',
            'url': 'https://www.chosun.com/politics/',
            'parser': 'chosun_politics',  # parser.py의 parse_chosun_politics 함수 사용
            'max_articles': 5
        },
        {
            'name': '중앙일보',
            'url': 'https://www.joongang.co.kr/politics',
            'parser': 'joongang_politics',  # parser.py의 parse_joongang_politics 함수 사용
            'max_articles': 5
        },
        # 추가 정치 뉴스 소스는 여기에 추가
    ],
    '스포츠': [
        {
            'name': '중앙일보',
            'url': 'https://www.joongang.co.kr/sports',
            'parser': 'joongang_sports',
            'max_articles': 5
        },
        {
            'name': '동아일보',
            'url': 'https://www.donga.com/news/Sports',
            'parser': 'donga_sports',
            'max_articles': 5
        },
        {
            'name': '조선일보',
            'url': 'https://www.chosun.com/sports/',
            'parser': 'chosun_sports',
            'max_articles': 5
        },
    ],
    '경제': [
        {
            'name': '중앙일보',
            'url': 'https://www.joongang.co.kr/money',
            'parser': 'joongang_economy',
            'max_articles': 5
        },
        {
            'name': '동아일보',
            'url': 'https://www.donga.com/news/Economy',
            'parser': 'donga_economy',
            'max_articles': 5
        },
        {
            'name': '조선일보',
            'url': 'https://www.chosun.com/economy/',
            'parser': 'chosun_economy',
            'max_articles': 5
        },
    ],
    '사회': [
        {
            'name': '조선일보',
            'url': 'https://www.chosun.com/national/',
            'parser': 'chosun_society',
            'max_articles': 5
        },
        {
            'name': '중앙일보',
            'url': 'https://www.joongang.co.kr/society',
            'parser': 'joongang_society',
            'max_articles': 5
        },
        {
            'name': '동아일보',
            'url': 'https://www.donga.com/news/Society',
            'parser': 'donga_society',
            'max_articles': 5
        },
    ],
    '국제': [
        {
            'name': '조선일보',
            'url': 'https://www.chosun.com/international/',
            'parser': 'chosun_international',
            'max_articles': 5
        },
        {
            'name': '중앙일보',
            'url': 'https://www.joongang.co.kr/world',
            'parser': 'joongang_international',
            'max_articles': 5
        },
        {
            'name': '동아일보',
            'url': 'https://www.donga.com/news/Inter',
            'parser': 'donga_international',
            'max_articles': 5
        },
    ],
    '문화': [
        {
            'name': '조선일보',
            'url': 'https://www.chosun.com/culture-style/',
            'parser': 'chosun_culture',
            'max_articles': 5
        },
        {
            'name': '중앙일보',
            'url': 'https://www.joongang.co.kr/culture',
            'parser': 'joongang_culture',
            'max_articles': 5
        },
        {
            'name': '동아일보',
            'url': 'https://www.donga.com/news/Culture',
            'parser': 'donga_culture',
            'max_articles': 5
        },
    ]
}

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
# 카테고리/소스별 JSON 파일: data/{category}/{source}/news_{date}_{time}.json
NEWS_JSON_TEMPLATE = f"{DATA_DIR}/{{category}}/{{source}}/news_{{date}}_{{time}}.json"
LOGS_DIR = "logs"
LOG_FILE = f"{LOGS_DIR}/crawler.log"

# 보고서 저장 경로
REPORT_DIR = "reports"
# 카테고리/소스별 보고서: reports/{category}/{source}/report_{date}.md
REPORT_TEMPLATE = f"{REPORT_DIR}/{{category}}/{{source}}/report_{{date}}.md"
# 통합 보고서: reports/combined/report_{date}.md
COMBINED_REPORT_TEMPLATE = f"{REPORT_DIR}/combined/report_{{date}}.md"

# 스케줄링 설정
# 특정 시간에 실행 (매일 아침 9시)
CRAWL_TIME = "09:00"  # 매일 오전 9시에 실행

# 보고서 자동 생성 설정
AUTO_GENERATE_REPORT = True  # 크롤링 후 자동으로 보고서 생성

# 재시도 설정
MAX_RETRIES = 3
RETRY_DELAY = 5  # 재시도 전 대기 시간 (초)
