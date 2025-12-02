"""
뉴스 데이터를 한국어 보고서로 변환하는 모듈
카테고리/소스별 개별 보고서 및 통합 보고서 생성
"""

import json
import os
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import re
from config import (
    NEWS_SOURCES, CATEGORY_EN_MAP, SOURCE_EN_MAP,
    REPORT_TEMPLATE, COMBINED_REPORT_TEMPLATE, NEWS_JSON_TEMPLATE
)

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """한국 시간(KST)으로 현재 시간을 반환합니다."""
    return datetime.now(KST)


def get_category_source_json_path(category: str, source: str, date: str) -> str:
    """카테고리/소스별 JSON 파일 경로 생성"""
    category_en = CATEGORY_EN_MAP.get(category, category.lower())
    source_en = SOURCE_EN_MAP.get(source, source.lower().replace(' ', '_'))
    return NEWS_JSON_TEMPLATE.format(category=category_en, source=source_en, date=date)


def load_all_news_by_date(date: str) -> dict:
    """
    특정 날짜의 모든 카테고리/소스 뉴스를 로드합니다.
    
    Returns:
        {category: {source: [news_items]}} 형태의 딕셔너리
    """
    all_data = defaultdict(lambda: defaultdict(list))
    
    for category, sources in NEWS_SOURCES.items():
        for source_config in sources:
            source_name = source_config['name']
            json_path = get_category_source_json_path(category, source_name, date)
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        all_data[category][source_name] = data
                except Exception as e:
                    print(f"⚠️ [{source_name}] 데이터 로드 실패: {e}")
    
    return all_data


def clean_title(title):
    """제목에서 날짜와 카테고리를 제거하고 정리합니다."""
    # 원본 저장
    original = title
    
    # 날짜 패턴 제거 (예: "Nov 24, 2025", "Sep 29, 2025")
    title = re.sub(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}', '', title)
    
    # 카테고리 제거
    categories = ['Announcements', 'Product', 'Policy', 'Research', 'Economic Research', 'Company', 'Engineering']
    for cat in categories:
        title = title.replace(cat, '')
    
    # 연속된 공백 정리
    title = re.sub(r'\s+', ' ', title).strip()
    
    # 제목이 너무 짧으면 원본 반환
    if len(title) < 10:
        return original
    
    return title


def generate_source_report(category: str, source: str, news_list: list, date: str) -> str:
    """
    개별 소스의 보고서를 생성합니다.
    
    Args:
        category: 카테고리
        source: 소스 이름
        news_list: 뉴스 항목 리스트
        date: 날짜 (YYYY-MM-DD)
        
    Returns:
        생성된 보고서 파일 경로
    """
    report = []
    report_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y년 %m월 %d일')
    
    report.append(f"# 📰 {category} - {source} 뉴스 보고서\n\n")
    report.append(f"**보고서 날짜**: {report_date}\n")
    report.append(f"**보고서 생성일**: {get_kst_now().strftime('%Y년 %m월 %d일 %H:%M')} (KST)\n")
    report.append(f"**총 뉴스 개수**: {len(news_list)}개\n")
    report.append("---\n\n")
    
    # 뉴스 목록
    report.append("## 📋 뉴스 목록\n\n")
    
    for idx, item in enumerate(news_list, 1):
        title = clean_title(item['title'])
        date_str = item.get('date', '날짜 미상')
        url = item['url']
        
        # scraped_at을 읽기 쉬운 형식으로 변환
        scraped_at = item.get('scraped_at', '')
        if scraped_at:
            # ISO 형식에서 날짜와 시간 추출 (타임존 정보 제거)
            # 예: 2025-12-02T09:08:57.123456+09:00 -> 2025-12-02 09:08:57
            scraped_time = scraped_at.split('.')[0].replace('T', ' ')
        else:
            scraped_time = '수집 시간 미상'
        
        report.append(f"### {idx}. {title}\n\n")
        report.append(f"- **날짜**: {date_str}\n")
        report.append(f"- **링크**: [{url}]({url})\n")
        report.append(f"- **수집 시간**: {scraped_time}\n\n")
    
    # 푸터
    report.append("---\n\n")
    report.append("## 📌 정보\n\n")
    report.append(f"- **카테고리**: {category}\n")
    report.append(f"- **출처**: {source}\n")
    report.append(f"- **데이터 파일**: `data/{CATEGORY_EN_MAP.get(category, category.lower())}/{SOURCE_EN_MAP.get(source, source.lower())}/news_{date}.json`\n\n")
    
    # 파일 저장
    category_en = CATEGORY_EN_MAP.get(category, category.lower())
    source_en = SOURCE_EN_MAP.get(source, source.lower().replace(' ', '_'))
    output_file = REPORT_TEMPLATE.format(category=category_en, source=source_en, date=date)
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    return output_file


def generate_combined_report(date: str) -> str:
    """
    모든 카테고리/소스의 뉴스를 통합한 보고서를 생성합니다.
    
    Args:
        date: 날짜 (YYYY-MM-DD)
        
    Returns:
        생성된 보고서 파일 경로
    """
    # 모든 뉴스 로드
    all_data = load_all_news_by_date(date)
    
    if not all_data:
        print("⚠️ 로드할 뉴스 데이터가 없습니다.")
        return None
    
    # 보고서 생성
    report = []
    report_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y년 %m월 %d일')
    
    # 총 뉴스 개수 계산
    total_count = sum(len(news) for sources in all_data.values() for news in sources.values())
    
    report.append(f"# 📰 종합 뉴스 보고서 - {report_date}\n\n")
    report.append(f"**보고서 생성일**: {get_kst_now().strftime('%Y년 %m월 %d일 %H:%M')} (KST)\n")
    report.append(f"**총 뉴스 개수**: {total_count}개\n")
    report.append("---\n\n")
    
    # 목차
    report.append("## 📑 목차\n\n")
    for category in sorted(all_data.keys()):
        category_count = sum(len(news) for news in all_data[category].values())
        anchor = category.lower().replace(' ', '-')
        report.append(f"- [{category}](#{anchor}) ({category_count}개)\n")
    report.append("\n---\n\n")
    
    # 카테고리별 통계
    report.append("## 📊 카테고리별 통계\n\n")
    report.append("| 카테고리 | 뉴스 개수 | 주요 소스 |\n")
    report.append("|---------|----------|----------|\n")
    for category in sorted(all_data.keys()):
        sources = list(all_data[category].keys())
        category_count = sum(len(news) for news in all_data[category].values())
        sources_str = ', '.join(sources)
        report.append(f"| {category} | {category_count}개 | {sources_str} |\n")
    report.append("\n---\n\n")
    
    # 최신 뉴스 하이라이트 (전체에서 상위 10개)
    all_news_flat = []
    for category, sources_dict in all_data.items():
        for source, news_list in sources_dict.items():
            all_news_flat.extend(news_list)
    
    sorted_news = sorted(all_news_flat, key=lambda x: x.get('date', ''), reverse=True)
    
    report.append("## 🔥 최신 뉴스 하이라이트 (전체)\n\n")
    for i, item in enumerate(sorted_news[:10], 1):
        title = clean_title(item['title'])
        date_str = item.get('date', '날짜 미상')
        main_category = item.get('main_category', '기타')
        source = item.get('source', '알 수 없음')
        url = item['url']
        
        report.append(f"### {i}. [{main_category}] {title}\n\n")
        report.append(f"- **출처**: {source}\n")
        report.append(f"- **날짜**: {date_str}\n")
        report.append(f"- **링크**: [{url}]({url})\n\n")
    
    report.append("---\n\n")
    
    # 카테고리별 상세 뉴스
    report.append("## 📰 카테고리별 상세 뉴스\n\n")
    
    for category in sorted(all_data.keys()):
        sources_dict = all_data[category]
        category_total = sum(len(news) for news in sources_dict.values())
        
        report.append(f"### {category}\n\n")
        report.append(f"**총 {category_total}개의 뉴스**\n\n")
        
        for source in sorted(sources_dict.keys()):
            news_list = sources_dict[source]
            report.append(f"#### {source} ({len(news_list)}개)\n\n")
            
            for idx, item in enumerate(news_list, 1):
                title = clean_title(item['title'])
                date_str = item.get('date', '날짜 미상')
                url = item['url']
                
                report.append(f"{idx}. **{title}**\n")
                report.append(f"   - 날짜: {date_str}\n")
                report.append(f"   - 링크: [{url}]({url})\n\n")
            
            report.append("\n")
        
        report.append("---\n\n")
    
    # 푸터
    report.append("## 📌 보고서 정보\n\n")
    report.append(f"- **크롤링 시스템**: Multi-Category News Crawler\n")
    report.append(f"- **지원 카테고리**: AI, 정치, 스포츠, 경제\n")
    report.append(f"- **데이터 저장**: 카테고리/소스별 폴더 구조\n")
    report.append(f"- **자동 업데이트**: 설정된 스케줄에 따라\n")
    report.append(f"- **데이터 형식**: JSON\n\n")
    
    # 파일 저장
    output_file = COMBINED_REPORT_TEMPLATE.format(date=date)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    print(f"✅ 통합 보고서 생성 완료: {output_file}")
    
    # 개별 소스별 보고서도 생성
    print("\n📝 개별 소스별 보고서 생성 중...")
    source_reports = []
    for category, sources_dict in all_data.items():
        for source, news_list in sources_dict.items():
            source_report = generate_source_report(category, source, news_list, date)
            source_reports.append(source_report)
            print(f"  ✓ [{category}/{source}] 보고서 생성: {source_report}")
    
    return output_file


def main():
    """메인 함수"""
    today = get_kst_now().strftime('%Y-%m-%d')
    
    print("=" * 60)
    print("📰 종합 뉴스 보고서 생성기")
    print("=" * 60)
    print(f"\n📅 날짜: {today}")
    
    try:
        report_file = generate_combined_report(today)
        
        if report_file:
            print(f"✨ 보고서 생성 완료!")
            print("=" * 60)
        else:
            print("⚠️ 생성할 데이터가 없습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
