"""
자동 스케줄링 모듈
정해진 주기마다 자동으로 뉴스를 크롤링합니다.
"""

import schedule
import time
import logging
from datetime import datetime

from config import CRAWL_TIME
from crawler import crawl_news, setup_logging
from report_generator import get_kst_now


logger = setup_logging()


def scheduled_crawl():
    """스케줄에 따라 실행되는 크롤링 작업"""
    logger.info("\n" + "=" * 60)
    logger.info("⏰ 자동 스케줄링 작업 시작")
    logger.info(f"실행 시간: {get_kst_now().strftime('%Y-%m-%d %H:%M:%S')} (KST)")
    logger.info("=" * 60 + "\n")
    
    try:
        success = crawl_news()
        
        if success:
            logger.info("✓ 스케줄링 크롤링 성공!")
        else:
            logger.warning("✗ 스케줄링 크롤링 실패")
            
    except Exception as e:
        logger.error(f"스케줄링 작업 중 오류 발생: {e}", exc_info=True)


def run_scheduler():
    """
    스케줄러를 시작합니다.
    
    매일 오전 9시에 자동으로 크롤링 및 보고서 생성을 실행합니다.
    """
    logger.info("=" * 60)
    logger.info("🤖 Anthropic 뉴스 크롤러 자동 스케줄러 시작")
    logger.info("=" * 60)
    
    # 매일 특정 시간에 실행
    schedule.every().day.at(CRAWL_TIME).do(scheduled_crawl)
    logger.info(f"✓ 스케줄 등록: 매일 {CRAWL_TIME}에 실행")
    
    # 프로그램 시작 시 즉시 한 번 실행
    logger.info("\n🚀 초기 크롤링 시작 (프로그램 시작 시)")
    scheduled_crawl()
    
    # 다음 실행 예정 시간 표시
    next_run = schedule.next_run()
    if next_run:
        logger.info(f"\n⏰ 다음 크롤링 예정 시간: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    logger.info("\n" + "=" * 60)
    logger.info("스케줄러 실행 중... (Ctrl+C로 종료)")
    logger.info("=" * 60 + "\n")
    
    # 무한 루프로 스케줄 실행
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크
            
    except KeyboardInterrupt:
        logger.info("\n\n" + "=" * 60)
        logger.info("⏹️  스케줄러 종료 (사용자 중단)")
        logger.info("=" * 60)


def main():
    """메인 함수"""
    run_scheduler()


if __name__ == "__main__":
    main()
