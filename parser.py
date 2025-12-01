"""
HTML 파싱 모듈
Anthropic 뉴스 페이지에서 뉴스 항목을 추출합니다.
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import re
from config import BASE_URL


def parse_news_page(html_content: str) -> List[Dict[str, str]]:
    """
    뉴스 페이지 HTML을 파싱하여 뉴스 항목 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        
    Returns:
        뉴스 항목 딕셔너리 리스트 (날짜, 카테고리, 제목, URL 포함)
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    
    # 뉴스 항목 찾기 - 다양한 패턴 시도
    # 방법 1: 링크 요소에서 뉴스 찾기
    news_links = soup.find_all('a', href=re.compile(r'/news/'))
    
    processed_urls = set()  # 중복 방지
    
    for link in news_links:
        url = link.get('href', '')
        
        # /news 페이지 자체는 제외
        if url == '/news' or url in processed_urls:
            continue
            
        # 상대 URL을 절대 URL로 변환
        if url.startswith('/'):
            full_url = BASE_URL + url
        else:
            full_url = url
            
        # 제목 추출
        title = link.get_text(strip=True)
        
        if not title or len(title) < 5:  # 너무 짧은 제목은 제외
            continue
        
        # 부모 요소에서 날짜와 카테고리 찾기
        parent = link.find_parent(['article', 'div', 'li', 'tr'])
        date_str = ""
        category = ""
        
        if parent:
            # 날짜 패턴 찾기 (예: "Nov 25, 2025" 또는 "2025-11-25")
            date_match = re.search(
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}|\d{4}-\d{2}-\d{2}',
                parent.get_text()
            )
            if date_match:
                date_str = date_match.group(0)
            
            # 카테고리 찾기 (일반적인 카테고리 키워드)
            category_keywords = [
                'Announcements', 'Product', 'Policy', 'Research', 
                'Economic Research', 'News', 'Company', 'Engineering'
            ]
            parent_text = parent.get_text()
            for keyword in category_keywords:
                if keyword in parent_text:
                    category = keyword
                    break
        
        # 뉴스 항목 추가
        news_item = {
            'title': title,
            'url': full_url,
            'date': date_str,
            'category': category,
            'scraped_at': datetime.now().isoformat()
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    # 중복 제거 및 정렬 (URL 기준)
    unique_items = {item['url']: item for item in news_items}
    news_items = list(unique_items.values())
    
    # 날짜 기준으로 정렬 (최신순)
    news_items.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return news_items


def parse_article_content(html_content: str) -> Optional[Dict[str, str]]:
    """
    개별 기사 페이지에서 상세 내용을 추출합니다. (선택사항)
    
    Args:
        html_content: 기사 페이지의 HTML 문자열
        
    Returns:
        기사 내용 딕셔너리 (제목, 본문 등)
    """
    soup = BeautifulSoup(html_content, 'lxml')
    
    # 기사 제목
    title_tag = soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    # 기사 본문 (일반적인 패턴)
    content_sections = soup.find_all(['p', 'article'])
    content = "\n\n".join([section.get_text(strip=True) for section in content_sections if section.get_text(strip=True)])
    
    return {
        'title': title,
        'content': content[:1000],  # 처음 1000자만 저장
        'full_content_length': len(content)
    }


def clean_text(text: str) -> str:
    """
    텍스트를 정제합니다.
    
    Args:
        text: 원본 텍스트
        
    Returns:
        정제된 텍스트
    """
    # 연속된 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    text = text.strip()
    return text
