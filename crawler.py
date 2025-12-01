"""
Anthropic 뉴스 크롤러 메인 모듈
뉴스 페이지를 크롤링하고 JSON 파일로 저장합니다.
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

from config import (
    NEWS_URL, HEADERS, REQUEST_DELAY, REQUEST_TIMEOUT,
    DATA_DIR, NEWS_JSON_TEMPLATE, LOGS_DIR, LOG_FILE,
    MAX_RETRIES, RETRY_DELAY, AUTO_GENERATE_REPORT
)
from parser import parse_news_page


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


def get_today_json_file():
    """오늘 날짜의 JSON 파일 경로를 반환합니다."""
    today = datetime.now().strftime('%Y-%m-%d')
    return NEWS_JSON_TEMPLATE.format(date=today)


def load_existing_news() -> List[Dict[str, str]]:
    """
    기존 뉴스 데이터를 로드합니다.
    
    Returns:
        기존 뉴스 항목 리스트
    """
    json_file = get_today_json_file()
    
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"기존 뉴스 {len(data)} 개 로드됨")
                return data
        except Exception as e:
            logger.error(f"기존 데이터 로드 실패: {e}")
            return []
    else:
        logger.info("기존 뉴스 데이터 없음")
        return []


def save_news(news_items: List[Dict[str, str]]):
    """
    뉴스 데이터를 JSON 파일로 저장합니다.
    
    Args:
        news_items: 저장할 뉴스 항목 리스트
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    json_file = NEWS_JSON_TEMPLATE.format(date=today)
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(news_items, f, ensure_ascii=False, indent=2)
        
        logger.info(f"뉴스 {len(news_items)}개를 {json_file}에 저장 완료")
        
    except Exception as e:
        logger.error(f"데이터 저장 실패: {e}")


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
    Anthropic 뉴스를 크롤링합니다.
    
    Returns:
        성공 여부
    """
    logger.info("=" * 60)
    logger.info("뉴스 크롤링 시작")
    logger.info(f"현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 1. 뉴스 페이지 가져오기
        html_content = fetch_page(NEWS_URL)
        if not html_content:
            logger.error("페이지를 가져올 수 없습니다")
            return False
        
        # 2. HTML 파싱
        logger.info("HTML 파싱 중...")
        new_news = parse_news_page(html_content)
        logger.info(f"파싱 완료: {len(new_news)}개 뉴스 항목 발견")
        
        if not new_news:
            logger.warning("파싱된 뉴스가 없습니다")
            return False
        
        # 3. 기존 뉴스 로드
        existing_news = load_existing_news()
        
        # 4. 병합
        merged_news = merge_news(existing_news, new_news)
        
        # 5. 저장
        save_news(merged_news)
        
        logger.info("=" * 60)
        logger.info("크롤링 완료!")
        logger.info(f"총 뉴스 개수: {len(merged_news)}")
        logger.info("=" * 60)
        
        # Rate limiting
        time.sleep(REQUEST_DELAY)
        
        # 자동 보고서 생성
        if AUTO_GENERATE_REPORT:
            try:
                logger.info("=" * 60)
                logger.info("📝 보고서 자동 생성 시작")
                logger.info("=" * 60)
                
                from report_generator import generate_report_from_json
                json_file = get_today_json_file()
                report_file, _ = generate_report_from_json(json_file)
                
                logger.info(f"✅ 보고서 생성 완료: {report_file}")
                logger.info("=" * 60)
                
            except Exception as e:
                logger.error(f"보고서 생성 실패: {e}", exc_info=True)
        
        return True
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}", exc_info=True)
        return False


def main():
    """메인 함수 - 단일 실행용"""
    success = crawl_news()
    
    json_file = get_today_json_file()
    
    if success:
        print(f"\n✓ 크롤링 성공! 데이터는 {json_file}에 저장되었습니다.")
    else:
        print("\n✗ 크롤링 실패. 로그를 확인하세요.")


if __name__ == "__main__":
    main()
