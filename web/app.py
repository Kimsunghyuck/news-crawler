"""
뉴스 크롤러 웹 애플리케이션
Flask 기반 웹 서버로 크롤링한 뉴스 데이터를 표시합니다.
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional

app = Flask(__name__)
CORS(app)

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

# 카테고리 및 소스 매핑
CATEGORIES = {
    'politics': '정치',
    'sports': '스포츠',
    'economy': '경제'
}

SOURCES = {
    'donga': '동아일보',
    'chosun': '조선일보',
    'joongang': '중앙일보'
}

def get_kst_now():
    """한국 시간(KST)으로 현재 시간을 반환합니다."""
    return datetime.now(KST)


def load_news_data(category: str, source: str, date: str) -> Optional[List[Dict]]:
    """
    특정 카테고리, 소스, 날짜의 뉴스 데이터를 로드합니다.
    
    Args:
        category: 카테고리 (politics, sports, economy)
        source: 신문사 (donga, chosun, joongang)
        date: 날짜 (YYYY-MM-DD)
    
    Returns:
        뉴스 데이터 리스트 또는 None
    """
    file_path = DATA_DIR / category / source / f'news_{date}.json'
    
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        app.logger.error(f"Error loading {file_path}: {e}")
        return None


def get_latest_news(limit: int = 4) -> List[Dict]:
    """
    최신 뉴스를 가져옵니다 (배너용).
    
    Args:
        limit: 가져올 뉴스 개수
    
    Returns:
        최신 뉴스 리스트
    """
    all_news = []
    today = get_kst_now().strftime('%Y-%m-%d')
    yesterday = (get_kst_now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 오늘과 어제 데이터에서 수집
    for date in [today, yesterday]:
        for category_en, category_ko in CATEGORIES.items():
            for source_en, source_ko in SOURCES.items():
                news_data = load_news_data(category_en, source_en, date)
                if news_data:
                    # 각 기사에 카테고리 한글명과 소스 한글명 추가
                    for article in news_data[:2]:  # 각 소스당 최대 2개
                        article['category_ko'] = category_ko
                        article['source_ko'] = source_ko
                        all_news.append(article)
    
    # 날짜순 정렬 (최신순)
    all_news.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
    
    return all_news[:limit]


def get_available_dates(category: str, source: str, days: int = 7) -> List[str]:
    """
    특정 카테고리와 소스에서 사용 가능한 날짜 목록을 반환합니다.
    
    Args:
        category: 카테고리
        source: 소스
        days: 확인할 최대 일수
    
    Returns:
        사용 가능한 날짜 리스트 (YYYY-MM-DD)
    """
    available_dates = []
    current_date = get_kst_now()
    
    for i in range(days):
        date_str = (current_date - timedelta(days=i)).strftime('%Y-%m-%d')
        file_path = DATA_DIR / category / source / f'news_{date_str}.json'
        if file_path.exists():
            available_dates.append(date_str)
    
    return available_dates


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


@app.route('/api/categories')
def get_categories():
    """카테고리 목록 반환"""
    return jsonify({
        'success': True,
        'data': [
            {'id': key, 'name': value} 
            for key, value in CATEGORIES.items()
        ]
    })


@app.route('/api/sources')
def get_sources():
    """신문사 목록 반환"""
    category = request.args.get('category')
    
    # 모든 카테고리에 동일한 소스 제공
    return jsonify({
        'success': True,
        'data': [
            {'id': key, 'name': value} 
            for key, value in SOURCES.items()
        ]
    })


@app.route('/api/news/<category>/<source>')
def get_news(category, source):
    """
    특정 카테고리와 소스의 뉴스 데이터 반환
    Query Parameters:
        date: 날짜 (선택사항, 기본값: 오늘)
    """
    date = request.args.get('date')
    
    if not date:
        date = get_kst_now().strftime('%Y-%m-%d')
    
    news_data = load_news_data(category, source, date)
    
    if news_data is None:
        return jsonify({
            'success': False,
            'message': f'해당 날짜({date})의 뉴스 데이터가 없습니다.',
            'data': []
        }), 404
    
    return jsonify({
        'success': True,
        'data': news_data,
        'category': CATEGORIES.get(category, category),
        'source': SOURCES.get(source, source),
        'date': date
    })


@app.route('/api/latest')
def get_latest():
    """최신 뉴스 반환 (배너용)"""
    limit = request.args.get('limit', 4, type=int)
    latest_news = get_latest_news(limit)
    
    return jsonify({
        'success': True,
        'data': latest_news,
        'count': len(latest_news)
    })


@app.route('/api/dates/<category>/<source>')
def get_dates(category, source):
    """특정 카테고리와 소스의 사용 가능한 날짜 목록 반환"""
    days = request.args.get('days', 7, type=int)
    dates = get_available_dates(category, source, days)
    
    return jsonify({
        'success': True,
        'data': dates
    })


@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({
        'success': False,
        'message': '요청한 리소스를 찾을 수 없습니다.'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return jsonify({
        'success': False,
        'message': '서버 내부 오류가 발생했습니다.'
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
