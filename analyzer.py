"""
뉴스 트렌드 분석 모듈
수집된 뉴스 데이터에서 키워드를 추출하고 빈도 분석을 수행합니다.
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta
from collections import Counter
from typing import List, Dict
from config import DATA_DIR

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """한국 시간(KST)으로 현재 시간을 반환합니다."""
    return datetime.now(KST)

# 불용어 리스트 (분석에서 제외할 단어들)
STOPWORDS = {
    '있다', '없다', '하다', '되다', '이다', '아니다', '그리고', '그러나', '하지만',
    '또한', '있는', '없는', '하는', '되는', '이는', '것은', '것이', '것을',
    '우리', '저희', '이번', '오늘', '어제', '내일', '올해', '작년', '내년',
    '통해', '위해', '대해', '관련', '따르면', '밝혔다', '전했다', '말했다',
    '이라고', '라고', '한다', '한다고', '했다', '했다고', '될', '될까', '기자',
    '뉴스', '속보', '단독', '특종', '취재', '보도', '발표', '공개', '확인'
}

def extract_korean_nouns(text: str, min_length: int = 2, max_length: int = 10) -> List[str]:
    """
    텍스트에서 한글 명사를 추출합니다 (간단한 정규식 기반).
    
    Args:
        text: 분석할 텍스트
        min_length: 최소 단어 길이
        max_length: 최대 단어 길이
    
    Returns:
        추출된 명사 리스트
    """
    # 한글 단어 추출 (2글자 이상)
    pattern = f'[가-힣]{{{min_length},{max_length}}}'
    words = re.findall(pattern, text)
    
    # 불용어 제거
    filtered_words = [w for w in words if w not in STOPWORDS]
    
    return filtered_words


def analyze_daily_keywords(date: str = None, top_n: int = 20) -> List[Dict[str, any]]:
    """
    특정 날짜의 모든 뉴스에서 키워드를 분석합니다.
    
    Args:
        date: 분석할 날짜 (YYYY-MM-DD), None이면 오늘
        top_n: 상위 N개 키워드 반환
    
    Returns:
        키워드 리스트: [{"word": "키워드", "count": 횟수}, ...]
    """
    if date is None:
        date = get_kst_now().strftime('%Y-%m-%d')
    
    all_keywords = []
    
    # 모든 카테고리/소스의 뉴스 파일 탐색
    for category_dir in os.listdir(DATA_DIR):
        category_path = os.path.join(DATA_DIR, category_dir)
        
        if not os.path.isdir(category_path):
            continue
        
        for source_dir in os.listdir(category_path):
            source_path = os.path.join(category_path, source_dir)
            
            if not os.path.isdir(source_path):
                continue
            
            # 해당 날짜의 뉴스 파일 찾기
            news_file = os.path.join(source_path, f'news_{date}.json')
            
            if os.path.exists(news_file):
                try:
                    with open(news_file, 'r', encoding='utf-8') as f:
                        news_items = json.load(f)
                    
                    # 각 뉴스 제목에서 키워드 추출
                    for item in news_items:
                        title = item.get('title', '')
                        keywords = extract_korean_nouns(title)
                        all_keywords.extend(keywords)
                        
                except Exception as e:
                    print(f"파일 읽기 오류 ({news_file}): {e}")
                    continue
    
    # 빈도 분석
    keyword_counts = Counter(all_keywords)
    
    # 상위 N개 추출
    top_keywords = [
        {"word": word, "count": count}
        for word, count in keyword_counts.most_common(top_n)
    ]
    
    return top_keywords


def analyze_category_keywords(category: str, date: str = None, top_n: int = 10) -> List[Dict[str, any]]:
    """
    특정 카테고리의 키워드를 분석합니다.
    
    Args:
        category: 카테고리 (politics, sports, economy 등)
        date: 분석할 날짜 (YYYY-MM-DD), None이면 오늘
        top_n: 상위 N개 키워드 반환
    
    Returns:
        키워드 리스트
    """
    if date is None:
        date = get_kst_now().strftime('%Y-%m-%d')
    
    all_keywords = []
    category_path = os.path.join(DATA_DIR, category)
    
    if not os.path.isdir(category_path):
        return []
    
    # 해당 카테고리의 모든 소스 탐색
    for source_dir in os.listdir(category_path):
        source_path = os.path.join(category_path, source_dir)
        
        if not os.path.isdir(source_path):
            continue
        
        news_file = os.path.join(source_path, f'news_{date}.json')
        
        if os.path.exists(news_file):
            try:
                with open(news_file, 'r', encoding='utf-8') as f:
                    news_items = json.load(f)
                
                for item in news_items:
                    title = item.get('title', '')
                    keywords = extract_korean_nouns(title)
                    all_keywords.extend(keywords)
                    
            except Exception as e:
                print(f"파일 읽기 오류 ({news_file}): {e}")
                continue
    
    keyword_counts = Counter(all_keywords)
    top_keywords = [
        {"word": word, "count": count}
        for word, count in keyword_counts.most_common(top_n)
    ]
    
    return top_keywords


def save_trend_data(date: str = None):
    """
    트렌드 데이터를 JSON 파일로 저장합니다 (GitHub Pages용).
    
    Args:
        date: 저장할 날짜, None이면 오늘
    """
    if date is None:
        date = get_kst_now().strftime('%Y-%m-%d')
    
    # 전체 키워드 분석
    daily_keywords = analyze_daily_keywords(date, top_n=20)
    
    # 카테고리별 키워드 분석
    categories = ['politics', 'sports', 'economy', 'society', 'international', 'culture']
    category_keywords = {}
    
    for category in categories:
        category_keywords[category] = analyze_category_keywords(category, date, top_n=5)
    
    # 트렌드 데이터 구조
    trend_data = {
        "date": date,
        "generated_at": get_kst_now().isoformat(),
        "daily_top_keywords": daily_keywords,
        "category_keywords": category_keywords
    }
    
    # docs/data/trends/ 디렉토리 생성
    trends_dir = os.path.join('docs', 'data', 'trends')
    os.makedirs(trends_dir, exist_ok=True)
    
    # JSON 파일로 저장
    trend_file = os.path.join(trends_dir, f'trends_{date}.json')
    
    try:
        with open(trend_file, 'w', encoding='utf-8') as f:
            json.dump(trend_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 트렌드 데이터 저장 완료: {trend_file}")
        print(f"   - 전체 키워드: {len(daily_keywords)}개")
        print(f"   - 카테고리별 키워드: {len(categories)}개 카테고리")
        
        # Top 5 키워드 출력
        if daily_keywords:
            print(f"\n🔥 오늘의 핫 키워드:")
            for i, kw in enumerate(daily_keywords[:5], 1):
                print(f"   {i}. {kw['word']} ({kw['count']}회)")
        
        return trend_file
        
    except Exception as e:
        print(f"❌ 트렌드 데이터 저장 실패: {e}")
        return None


def main():
    """트렌드 분석 실행 (테스트용)"""
    print("=" * 60)
    print("뉴스 트렌드 분석 시작")
    print("=" * 60)
    
    today = get_kst_now().strftime('%Y-%m-%d')
    
    # 트렌드 데이터 생성 및 저장
    save_trend_data(today)
    
    print("=" * 60)


if __name__ == "__main__":
    main()
