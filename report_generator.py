"""
뉴스 데이터를 한국어 보고서로 변환하는 모듈
크롤링한 날짜를 제목에 포함하여 자동 생성
"""

import json
import os
from datetime import datetime
from collections import defaultdict
import re


def load_news_data(json_file):
    """JSON 파일에서 뉴스 데이터를 로드합니다."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


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


def translate_category(category):
    """카테고리를 한국어로 번역합니다."""
    translations = {
        'Announcements': '발표',
        'Product': '제품',
        'Policy': '정책',
        'Research': '연구',
        'Economic Research': '경제 연구',
        'Company': '회사',
        'Engineering': '엔지니어링'
    }
    return translations.get(category, category)


def translate_month(month_str):
    """월 약어를 한국어로 번역합니다."""
    months = {
        'Jan': '1월', 'Feb': '2월', 'Mar': '3월', 'Apr': '4월',
        'May': '5월', 'Jun': '6월', 'Jul': '7월', 'Aug': '8월',
        'Sep': '9월', 'Oct': '10월', 'Nov': '11월', 'Dec': '12월'
    }
    
    for eng, kor in months.items():
        month_str = month_str.replace(eng, kor)
    
    # "Nov 24, 2025" -> "2025년 11월 24일"
    match = re.search(r'(\d{1,2})월\s+(\d{1,2}),\s+(\d{4})', month_str)
    if match:
        month, day, year = match.groups()
        return f"{year}년 {month} {day}일"
    
    return month_str


def group_by_category(news_items):
    """카테고리별로 뉴스를 그룹화합니다."""
    grouped = defaultdict(list)
    
    for item in news_items:
        category = item.get('category', '기타')
        grouped[category].append(item)
    
    return grouped


def generate_markdown_report(news_items, output_file, report_date=None):
    """마크다운 형식의 한국어 보고서를 생성합니다."""
    
    if report_date is None:
        report_date = datetime.now().strftime('%Y년 %m월 %d일')
    
    # 날짜순 정렬
    sorted_news = sorted(news_items, key=lambda x: x.get('date', ''), reverse=True)
    
    # 카테고리별 그룹화
    grouped = group_by_category(sorted_news)
    
    # 보고서 생성
    report = []
    report.append(f"# 📰 Anthropic 뉴스 보고서 - {report_date}\n\n")
    report.append(f"**보고서 생성일**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n")
    report.append(f"**총 뉴스 개수**: {len(sorted_news)}개\n")
    report.append("---\n\n")
    
    # 목차
    report.append("## 📑 목차\n\n")
    for category in sorted(grouped.keys()):
        kor_category = translate_category(category)
        count = len(grouped[category])
        report.append(f"- [{kor_category}](#{category.lower().replace(' ', '-')}) ({count}개)\n")
    report.append("\n---\n\n")
    
    # 요약
    report.append("## 📊 주요 통계\n\n")
    report.append("| 카테고리 | 뉴스 개수 |\n")
    report.append("|---------|----------|\n")
    for category in sorted(grouped.keys()):
        kor_category = translate_category(category)
        count = len(grouped[category])
        report.append(f"| {kor_category} | {count}개 |\n")
    report.append("\n---\n\n")
    
    # 최신 뉴스 하이라이트
    report.append("## 🔥 최신 뉴스 하이라이트\n\n")
    for i, item in enumerate(sorted_news[:5], 1):
        title = clean_title(item['title'])
        date = translate_month(item.get('date', '날짜 미상'))
        category = translate_category(item.get('category', ''))
        url = item['url']
        
        report.append(f"### {i}. {title}\n\n")
        report.append(f"- **날짜**: {date}\n")
        report.append(f"- **카테고리**: {category}\n")
        report.append(f"- **링크**: [{url}]({url})\n\n")
    
    report.append("---\n\n")
    
    # 카테고리별 상세 뉴스
    report.append("## 📰 카테고리별 상세 뉴스\n\n")
    
    for category in sorted(grouped.keys()):
        kor_category = translate_category(category)
        items = grouped[category]
        
        report.append(f"### {kor_category}\n\n")
        
        for item in items:
            title = clean_title(item['title'])
            date = translate_month(item.get('date', '날짜 미상'))
            url = item['url']
            
            report.append(f"#### {title}\n\n")
            report.append(f"- **발표일**: {date}\n")
            report.append(f"- **원문 링크**: [{url}]({url})\n")
            report.append(f"- **수집 시간**: {item['scraped_at'][:19].replace('T', ' ')}\n\n")
        
        report.append("\n")
    
    # 푸터
    report.append("---\n\n")
    report.append("## 📌 보고서 정보\n\n")
    report.append(f"- **데이터 출처**: [Anthropic 공식 뉴스 페이지](https://www.anthropic.com/news)\n")
    report.append(f"- **크롤링 시스템**: Anthropic News Crawler\n")
    report.append(f"- **자동 업데이트**: 6시간마다\n")
    report.append(f"- **데이터 형식**: JSON\n\n")
    
    # 파일 저장
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    return output_file


def generate_report_from_json(json_file, output_file=None, report_date=None):
    """
    JSON 파일에서 보고서를 생성합니다.
    
    Args:
        json_file: 뉴스 JSON 파일 경로
        output_file: 출력 파일 경로 (None이면 자동 생성)
        report_date: 보고서 날짜 (None이면 오늘 날짜)
    
    Returns:
        생성된 보고서 파일 경로
    """
    # 보고서 날짜 설정
    if report_date is None:
        report_date = datetime.now().strftime('%Y-%m-%d')
    
    # 출력 파일 경로 설정
    if output_file is None:
        from config import REPORT_DIR, REPORT_TEMPLATE
        output_file = REPORT_TEMPLATE.format(date=report_date)
    
    # 뉴스 데이터 로드
    news_items = load_news_data(json_file)
    
    # 보고서 생성
    report_file = generate_markdown_report(news_items, output_file, 
                                          datetime.now().strftime('%Y년 %m월 %d일'))
    
    return report_file, len(news_items)


def main():
    """메인 함수"""
    json_file = "data/news.json"
    
    print("=" * 60)
    print("📰 Anthropic 뉴스 보고서 생성기")
    print("=" * 60)
    print(f"\n📂 데이터 로드 중: {json_file}")
    
    try:
        report_file, count = generate_report_from_json(json_file)
        
        print(f"✅ {count}개의 뉴스 로드 완료")
        print(f"📝 보고서 생성 완료: {report_file}")
        print(f"📊 총 {count}개의 뉴스가 포함되었습니다.")
        print("\n" + "=" * 60)
        print("✨ 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
