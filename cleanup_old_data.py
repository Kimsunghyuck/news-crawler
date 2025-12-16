"""
오래된 뉴스 데이터 정리 스크립트
1개월(30일) 이상 지난 JSON 파일을 자동으로 삭제합니다.
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """한국 시간(KST)으로 현재 시간을 반환합니다."""
    return datetime.now(KST)

# 로깅 설정
def setup_logging():
    """로깅을 설정합니다."""
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/cleanup.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# 설정
DATA_RETENTION_DAYS = 30  # 데이터 보관 기간 (일)
TARGET_FOLDERS = ["data", "docs/data"]  # 정리할 폴더 목록

def parse_date_from_filename(filename: str) -> datetime | None:
    """
    파일명에서 날짜를 추출합니다.
    파일명 형식:
    - 신 형식: news_2025-12-16_09-20.json
    - 구 형식: news_2025-12-16.json

    Args:
        filename: 파일명

    Returns:
        datetime 객체 또는 None (파싱 실패 시)
    """
    # 신 형식 (시간대 포함): news_2025-12-16_09-20.json
    pattern_new = r'news_(\d{4}-\d{2}-\d{2})_\d{2}-\d{2}\.json'
    match = re.match(pattern_new, filename)

    if match:
        date_str = match.group(1)
        try:
            # 날짜를 KST 시간대로 파싱
            return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=KST)
        except ValueError:
            logger.error(f"날짜 파싱 실패: {date_str}")
            return None

    # 구 형식 (시간대 없음): news_2025-12-16.json
    pattern_old = r'news_(\d{4}-\d{2}-\d{2})\.json'
    match = re.match(pattern_old, filename)

    if match:
        date_str = match.group(1)
        try:
            # 날짜를 KST 시간대로 파싱
            return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=KST)
        except ValueError:
            logger.error(f"날짜 파싱 실패: {date_str}")
            return None

    return None

def cleanup_old_files(folder_path: str, retention_days: int) -> tuple[int, int]:
    """
    지정된 폴더에서 오래된 파일을 삭제합니다.

    Args:
        folder_path: 정리할 폴더 경로
        retention_days: 보관 기간 (일)

    Returns:
        (삭제된 파일 수, 전체 파일 수) 튜플
    """
    if not os.path.exists(folder_path):
        logger.warning(f"폴더가 존재하지 않습니다: {folder_path}")
        return 0, 0

    current_date = get_kst_now()
    cutoff_date = current_date - timedelta(days=retention_days)

    deleted_count = 0
    total_count = 0

    # 모든 하위 폴더를 순회하며 JSON 파일 찾기
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if not filename.startswith('news_') or not filename.endswith('.json'):
                continue

            total_count += 1
            file_path = os.path.join(root, filename)

            # 파일명에서 날짜 추출
            file_date = parse_date_from_filename(filename)

            if file_date is None:
                logger.warning(f"날짜를 파싱할 수 없는 파일: {file_path}")
                continue

            # 보관 기간이 지난 파일 삭제
            if file_date < cutoff_date:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"삭제됨: {file_path} (날짜: {file_date.strftime('%Y-%m-%d')})")
                except Exception as e:
                    logger.error(f"파일 삭제 실패: {file_path}, 오류: {e}")

    return deleted_count, total_count

def cleanup_empty_directories(folder_path: str) -> int:
    """
    빈 디렉토리를 삭제합니다.

    Args:
        folder_path: 정리할 폴더 경로

    Returns:
        삭제된 디렉토리 수
    """
    if not os.path.exists(folder_path):
        return 0

    deleted_count = 0

    # 하위 디렉토리부터 확인 (bottom-up)
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                # 디렉토리가 비어있으면 삭제
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    deleted_count += 1
                    logger.info(f"빈 디렉토리 삭제: {dir_path}")
            except Exception as e:
                logger.error(f"디렉토리 삭제 실패: {dir_path}, 오류: {e}")

    return deleted_count

def main():
    """메인 함수"""
    logger.info("=" * 60)
    logger.info(f"데이터 정리 시작 (보관 기간: {DATA_RETENTION_DAYS}일)")
    logger.info(f"현재 시간: {get_kst_now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    logger.info("=" * 60)

    total_deleted = 0
    total_files = 0

    # 각 폴더 정리
    for folder in TARGET_FOLDERS:
        logger.info(f"\n폴더 정리 중: {folder}")
        deleted, total = cleanup_old_files(folder, DATA_RETENTION_DAYS)
        total_deleted += deleted
        total_files += total
        logger.info(f"  - 전체 파일: {total}개, 삭제: {deleted}개")

    # 빈 디렉토리 정리
    logger.info("\n빈 디렉토리 정리 중...")
    empty_dirs_deleted = 0
    for folder in TARGET_FOLDERS:
        empty_dirs_deleted += cleanup_empty_directories(folder)

    # 요약
    logger.info("\n" + "=" * 60)
    logger.info("정리 완료")
    logger.info(f"  - 전체 파일 수: {total_files}개")
    logger.info(f"  - 삭제된 파일: {total_deleted}개")
    logger.info(f"  - 삭제된 빈 디렉토리: {empty_dirs_deleted}개")
    logger.info(f"  - 남은 파일: {total_files - total_deleted}개")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
