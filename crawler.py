"""
멀티 카테고리 뉴스 크롤러 메인 모듈
여러 뉴스 소스를 카테고리별로 크롤링하고 JSON 파일로 저장합니다.
"""

import requests
import json
import time
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import re

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """한국 시간(KST)으로 현재 시간을 반환합니다."""
    return datetime.now(KST)

from config import (
    NEWS_SOURCES, HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT,
    DATA_DIR, NEWS_JSON_TEMPLATE, LOGS_DIR, LOG_FILE,
    MAX_RETRIES, RETRY_DELAY, AUTO_GENERATE_REPORT,
    CATEGORY_EN_MAP, SOURCE_EN_MAP, COMBINED_REPORT_TEMPLATE
)
import parser


# 로깅 설정
def setup_logging():
    """로깅을 설정합니다."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def extract_article_image(article_url: str, source: str) -> str:
    """
    기사 URL에서 대표 이미지를 추출합니다.
    
    Args:
        article_url: 기사 URL
        source: 뉴스 소스 이름
        
    Returns:
        이미지 URL 문자열 (없으면 빈 문자열)
    """
    try:
        response = requests.get(article_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        image_url = ""
        
        # Open Graph 이미지 메타 태그 (가장 일반적)
        og_image = soup.find('meta', property='og:image')
        if og_image:
            image_url = og_image.get('content', '')
        
        # Twitter 카드 이미지
        if not image_url:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image:
                image_url = twitter_image.get('content', '')
        
        # 기사 본문의 첫 번째 이미지
        if not image_url:
            article_body = soup.find(['article', 'div'], class_=re.compile(r'article|content|body'))
            if article_body:
                img_tag = article_body.find('img')
                if img_tag:
                    image_url = img_tag.get('src', '') or img_tag.get('data-src', '')
        
        # 상대 URL을 절대 URL로 변환
        if image_url and image_url.startswith('/'):
            from urllib.parse import urlparse
            parsed = urlparse(article_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            image_url = f"{base_url}{image_url}"
        
        return image_url
        
    except Exception as e:
        logger.debug(f"이미지 추출 실패 ({article_url}): {e}")
        return ""


def fetch_page(url: str, retries: int = MAX_RETRIES) -> Optional[str]:
    """
    URL에서 HTML 페이지를 가져옵니다.
    
    Args:
        url: 크롤링할 URL
        retries: 재시도 횟수
        
    Returns:
        HTML 문자열 또는 실패 시 None
    """
    for attempt in range(retries):
        try:
            logger.info(f"페이지 가져오기 시도 ({attempt + 1}/{retries}): {url}")
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            logger.info(f"페이지 가져오기 성공: {url}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"요청 실패 (시도 {attempt + 1}/{retries}): {e}")
            
            if attempt < retries - 1:
                logger.info(f"{RETRY_DELAY}초 후 재시도...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"최대 재시도 횟수 초과: {url}")
                return None
    
    return None


def get_category_source_path(category: str, source: str, date: str, is_report: bool = False) -> str:
    """
    카테고리와 소스에 따른 파일 경로를 생성합니다.
    
    Args:
        category: 카테고리 (한글)
        source: 소스 이름 (한글)
        date: 날짜 (YYYY-MM-DD)
        is_report: 보고서 경로 여부
        
    Returns:
        파일 경로
    """
    category_en = CATEGORY_EN_MAP.get(category, category.lower())
    source_en = SOURCE_EN_MAP.get(source, source.lower().replace(' ', '_'))
    
    if is_report:
        from config import REPORT_TEMPLATE
        return REPORT_TEMPLATE.format(category=category_en, source=source_en, date=date)
    else:
        return NEWS_JSON_TEMPLATE.format(category=category_en, source=source_en, date=date)


def get_today_json_file():
    """오늘 날짜의 통합 JSON 파일 경로를 반환합니다 (하위 호환성)."""
    today = datetime.now().strftime('%Y-%m-%d')
    # 통합 JSON은 더 이상 사용하지 않지만, 하위 호환성을 위해 유지
    return f"{DATA_DIR}/news_{today}.json"


def load_existing_news_by_source(category: str, source: str) -> List[Dict[str, str]]:
    """
    특정 카테고리/소스의 기존 뉴스 데이터를 로드합니다.
    
    Args:
        category: 카테고리
        source: 소스 이름
        
    Returns:
        기존 뉴스 항목 리스트
    """
    today = datetime.now().strftime('%Y-%m-%d')
    json_file = get_category_source_path(category, source, today)
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"[{source}] 기존 뉴스 {len(data)}개 로드됨")
                return data
        except Exception as e:
            logger.error(f"[{source}] 기존 데이터 로드 실패: {e}")
            return []
    else:
        logger.info(f"[{source}] 기존 뉴스 데이터 없음")
        return []


def save_news_by_source(category: str, source: str, news_items: List[Dict[str, str]]):
    """
    특정 카테고리/소스의 뉴스 데이터를 JSON 파일로 저장합니다.
    
    Args:
        category: 카테고리
        source: 소스 이름
        news_items: 저장할 뉴스 항목 리스트
    """
    today = datetime.now().strftime('%Y-%m-%d')
    json_file = get_category_source_path(category, source, today)
    
    # 디렉토리 생성
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[{source}] 뉴스 {len(news_items)}개를 {json_file}에 저장 완료")
        
    except Exception as e:
        logger.error(f"[{source}] 데이터 저장 실패: {e}")


def load_all_news() -> List[Dict[str, str]]:
    """
    모든 카테고리/소스의 뉴스를 로드하여 통합합니다.
    
    Returns:
        통합된 뉴스 항목 리스트
    """
    all_news = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for category, sources in NEWS_SOURCES.items():
        for source_config in sources:
            source_name = source_config['name']
            json_file = get_category_source_path(category, source_name, today)
            
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_news.extend(data)
                except Exception as e:
                    logger.error(f"[{source_name}] 데이터 로드 실패: {e}")
    
    return all_news


def merge_news(existing_news: List[Dict[str, str]], new_news: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    기존 뉴스와 새 뉴스를 병합합니다 (중복 제거).
    
    Args:
        existing_news: 기존 뉴스 리스트
        new_news: 새로 크롤링한 뉴스 리스트
        
    Returns:
        병합된 뉴스 리스트
    """
    # URL을 키로 사용하여 중복 제거
    news_dict = {item['url']: item for item in existing_news}
    
    new_count = 0
    for item in new_news:
        if item['url'] not in news_dict:
            news_dict[item['url']] = item
            new_count += 1
        else:
            # 기존 항목 업데이트 (스크랩 시간 등)
            news_dict[item['url']].update(item)
    
    logger.info(f"새로운 뉴스 {new_count}개 발견")
    
    # 리스트로 변환 후 날짜 기준 정렬
    merged_news = list(news_dict.values())
    merged_news.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return merged_news


def crawl_news() -> bool:
    """
    모든 카테고리의 뉴스를 크롤링합니다.
    
    Returns:
        성공 여부
    """
    logger.info("=" * 60)
    logger.info("멀티 카테고리 뉴스 크롤링 시작")
    kst_now = get_kst_now()
    logger.info(f"현재 시간 (KST): {kst_now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"실행 시간대: {kst_now.strftime('%p %I시')} KST".replace('AM', '오전').replace('PM', '오후'))
    logger.info("=" * 60)
    
    try:
        all_news_count = 0
        category_stats = {}
        
        # 각 카테고리별로 크롤링
        for category, sources in NEWS_SOURCES.items():
            if not sources:  # 소스가 없는 카테고리는 건너뛰기
                logger.info(f"'{category}' 카테고리: 설정된 뉴스 소스 없음")
                continue
            
            logger.info(f"\n{'='*60}")
            logger.info(f"카테고리: {category}")
            logger.info(f"{'='*60}")
            
            category_stats[category] = 0
            
            for source_config in sources:
                source_name = source_config['name']
                url = source_config['url']
                parser_name = source_config['parser']
                max_articles = source_config.get('max_articles', 20)
                
                logger.info(f"\n크롤링 소스: {source_name}")
                logger.info(f"URL: {url}")
                
                # 1. 페이지 가져오기
                html_content = fetch_page(url)
                if not html_content:
                    logger.error(f"{source_name} 페이지를 가져올 수 없습니다")
                    continue
                
                # 2. 적절한 파서 함수 가져오기
                try:
                    parser_func = getattr(parser, f'parse_{parser_name}')
                except AttributeError:
                    logger.error(f"파서 함수 'parse_{parser_name}'를 찾을 수 없습니다")
                    continue
                
                # 3. HTML 파싱
                logger.info(f"HTML 파싱 중... (파서: {parser_name})")
                
                # max_articles 인자를 받는 파서들
                if parser_name in ['donga_politics', 'chosun_politics', 'joongang_politics',
                                    'donga_sports', 'chosun_sports', 'joongang_sports',
                                    'donga_economy', 'chosun_economy', 'joongang_economy']:
                    new_news = parser_func(html_content, max_articles)
                else:
                    new_news = parser_func(html_content)
                    
                logger.info(f"파싱 완료: {len(new_news)}개 뉴스 항목 발견")
                
                # 각 뉴스 항목의 기사 URL에서 이미지 추출
                for item in new_news:
                    if not item.get('image_url'):  # 이미지 URL이 없는 경우에만
                        image_url = extract_article_image(item['url'], source_name)
                        item['image_url'] = image_url
                        time.sleep(0.5)  # 과도한 요청 방지
                
                # 카테고리와 소스 정보 추가
                for item in new_news:
                    item['main_category'] = category
                    if 'source' not in item:
                        item['source'] = source_name
                
                # 4. 기존 뉴스 로드 (소스별)
                existing_news = load_existing_news_by_source(category, source_name)
                
                # 5. 병합
                merged_news = merge_news(existing_news, new_news)
                
                # 6. 소스별로 저장
                save_news_by_source(category, source_name, merged_news)
                
                all_news_count += len(merged_news)
                category_stats[category] += len(merged_news)
                
                # Rate limiting
                time.sleep(REQUEST_DELAY)
        
        if all_news_count == 0:
            logger.warning("파싱된 뉴스가 없습니다")
            return False
        
        logger.info("\n" + "=" * 60)
        logger.info("크롤링 완료!")
        logger.info(f"총 뉴스 개수: {all_news_count}")
        
        # 카테고리별 통계
        logger.info("\n카테고리별 뉴스 개수:")
        for cat, count in sorted(category_stats.items()):
            if count > 0:
                logger.info(f"  - {cat}: {count}개")
        
        logger.info("=" * 60)
        
        # 자동 보고서 생성
        if AUTO_GENERATE_REPORT:
            try:
                logger.info("=" * 60)
                logger.info("📝 통합 보고서 자동 생성 시작")
                logger.info("=" * 60)
                
                from report_generator import generate_combined_report
                today = datetime.now().strftime('%Y-%m-%d')
                report_file = generate_combined_report(today)
                
                logger.info(f"✅ 통합 보고서 생성 완료: {report_file}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"보고서 생성 실패: {e}", exc_info=True)
        
        # 트렌드 데이터 자동 생성
        try:
            logger.info("=" * 60)
            logger.info("📊 트렌드 분석 데이터 생성 시작")
            logger.info("=" * 60)
            
            from analyzer import save_trend_data
            today = get_kst_now().strftime('%Y-%m-%d')
            trend_file = save_trend_data(today)
            
            if trend_file:
                logger.info(f"✅ 트렌드 데이터 생성 완료: {trend_file}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"트렌드 데이터 생성 실패: {e}", exc_info=True)
        
        return True
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}", exc_info=True)
        return False


def main():
    """메인 함수 - 단일 실행용"""
    success = crawl_news()
    
    if success:
        print(f"\n✓ 크롤링 성공! 데이터는 카테고리/소스별 폴더에 저장되었습니다.")
        print(f"  - 데이터: {DATA_DIR}/{{category}}/{{source}}/")
        print(f"  - 보고서: {COMBINED_REPORT_TEMPLATE.split('/')[0]}/combined/")
    else:
        print("\n✗ 크롤링 실패. 로그를 확인하세요.")


if __name__ == "__main__":
    main()
