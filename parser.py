"""
HTML 파싱 모듈
다양한 뉴스 소스에서 뉴스 항목을 추출합니다.
"""

from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
import re

# 한국 시간대 (KST = UTC+9)
KST = timezone(timedelta(hours=9))

def get_kst_now():
    """한국 시간(KST)으로 현재 시간을 반환합니다."""
    return datetime.now(KST)


def get_crawl_time_str():
    """
    예정된 크롤링 시간대를 반환합니다.
    파일명에 사용되는 형식: HH-MM

    크롤링 시간대:
    - 09:00 KST (GitHub Actions cron: '0 0 * * *')
    - 15:00 KST (GitHub Actions cron: '0 6 * * *')
    - 19:00 KST (GitHub Actions cron: '0 10 * * *')

    Returns:
        시간 문자열 (예: "09-00", "15-00", "19-00")
    """
    now = get_kst_now()
    hour = now.hour

    # 크롤링 시간대에 따라 고정된 시간 반환
    if hour < 9:
        # 9:00 이전: 전날 19:00 시간대 (별도 처리 필요)
        return '19-00'
    elif hour < 15:
        # 9:00 ~ 15:00: 오전 시간대
        return '09-00'
    elif hour < 19:
        # 15:00 ~ 19:00: 오후 시간대
        return '15-00'
    else:
        # 19:00 이후: 저녁 시간대
        return '19-00'


def extract_image_url(link_element, base_url: str = "") -> str:
    """
    링크 요소에서 이미지 URL을 추출합니다.
    
    Args:
        link_element: BeautifulSoup 링크 요소
        base_url: 기본 URL (상대 경로를 절대 경로로 변환)
        
    Returns:
        이미지 URL 문자열
    """
    image_url = ""
    
    # 1. 링크 내부의 img 태그 찾기
    img_tag = link_element.find('img')
    if img_tag:
        image_url = img_tag.get('src', '') or img_tag.get('data-src', '') or img_tag.get('data-lazy-src', '')
    
    # 2. 링크 부모 요소에서 이미지 찾기
    if not image_url:
        parent_elem = link_element.find_parent(['li', 'div', 'article'])
        if parent_elem:
            img_tag = parent_elem.find('img')
            if img_tag:
                image_url = img_tag.get('src', '') or img_tag.get('data-src', '') or img_tag.get('data-lazy-src', '')
    
    # 상대 URL을 절대 URL로 변환
    if image_url and base_url and image_url.startswith('/'):
        image_url = f"{base_url}{image_url}"
    
    return image_url


def parse_anthropic_news(html_content: str) -> List[Dict[str, str]]:
    """
    Anthropic 뉴스 페이지 HTML을 파싱하여 뉴스 항목 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        
    Returns:
        뉴스 항목 딕셔너리 리스트 (날짜, 카테고리, 제목, URL 포함)
    """
    BASE_URL = "https://www.anthropic.com"
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
            'scraped_at': get_kst_now().isoformat()
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    # 중복 제거 및 정렬 (URL 기준)
    unique_items = {item['url']: item for item in news_items}
    news_items = list(unique_items.values())
    
    # 날짜 기준으로 정렬 (최신순)
    news_items.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    return news_items


def parse_donga_politics(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    동아일보 '많이 본 정치 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 동아일보 '많이 본 정치 뉴스' 섹션 찾기 (<h2 class="sec_tit">)
    trending_section = soup.find('h2', class_='sec_tit', string=re.compile(r'많이 본 정치 뉴스'))
    
    # fallback: h2 태그를 못 찾으면 일반 text 검색
    if not trending_section:
        trending_section = soup.find(string=re.compile(r'많이 본 정치 뉴스'))
    
    if trending_section:
        # 많이 본 뉴스 섹션 컨테이너 찾기
        section_parent = trending_section.find_parent(['div', 'section', 'article'])
        if section_parent:
            # 해당 섹션 내의 뉴스 링크 찾기
            news_links = section_parent.find_all('a', href=re.compile(r'/news/Politics/article/all/\d+/\d+/\d+'))
            
            for link in news_links:
                if len(news_items) >= max_articles:
                    break
                    
                url = link.get('href', '')
                
                if not url or url in processed_urls:
                    continue
                
                # 상대 URL을 절대 URL로 변환
                if url.startswith('/'):
                    full_url = f"https://www.donga.com{url}"
                else:
                    full_url = url
                
                # 제목 추출
                title = link.get_text(strip=True)
                
                # 제목이 너무 짧으면 다음 링크로
                if not title or len(title) < 10:
                    continue
                
                # 이미지 URL 추출
                image_url = extract_image_url(link, "https://www.donga.com")
                
                # URL에서 날짜 추출
                date_str = ""
                date_match = re.search(r'/(\d{8})/', url)
                if date_match:
                    date_num = date_match.group(1)
                    date_str = f"{date_num[:4]}-{date_num[4:6]}-{date_num[6:8]}"
                
                if not date_str:
                    date_str = get_kst_now().strftime('%Y-%m-%d')
                
                news_item = {
                    'title': clean_text(title),
                    'url': full_url,
                    'date': date_str,
                    'category': '정치',
                    'source': '동아일보',
                    'image_url': image_url,
                    'scraped_at': get_kst_now().isoformat()
                }
                
                news_items.append(news_item)
                processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_chosun_politics(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    조선일보 '정치 많이 본 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 조선일보 '정치 많이 본 뉴스' 섹션 찾기
    trending_section = soup.find('div', class_='flex-chain__heading-title', string=re.compile(r'정치\s*많이\s*본\s*뉴스'))
    
    news_links = []
    if trending_section:
        # 2단계 상위 요소까지 탐색
        section_container = trending_section.find_parent()
        if section_container:
            section_container = section_container.find_parent()
        
        if section_container:
            news_links = section_container.find_all('a', href=re.compile(r'/politics/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    # fallback: 섹션을 못 찾으면 전체 페이지에서 검색
    if not news_links:
        news_links = soup.find_all('a', href=re.compile(r'/politics/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    for link in news_links:
        if len(news_items) >= max_articles:
            break
            
        url = link.get('href', '')
        
        if not url or url in processed_urls:
            continue
        
        # 상대 URL을 절대 URL로 변환
        if url.startswith('/'):
            full_url = f"https://www.chosun.com{url}"
        else:
            full_url = url
        
        # 제목 추출
        title = link.get_text(strip=True)
        
        # 제목이 너무 짧으면 다음 링크로
        if not title or len(title) < 10:
            continue
        
        # 이미지 URL 추출
        image_url = extract_image_url(link, "https://www.chosun.com")
        
        # URL에서 날짜 추출 (패턴: /2025/12/01/...)
        date_str = ""
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f"{year}-{month}-{day}"
        
        if not date_str:
            date_str = get_kst_now().strftime('%Y-%m-%d')
        
        # 뉴스 항목 추가
        news_item = {
            'title': clean_text(title),
            'url': full_url,
            'date': date_str,
            'category': '정치',
            'source': '조선일보',
            'image_url': image_url,
            'scraped_at': get_kst_now().isoformat()
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_joongang_politics(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    중앙일보 정치 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 중앙일보 "정치 많이 본 기사" 섹션 찾기
    # <strong class="title"> 태그 안에서 섹션 제목 찾기
    section_title = soup.find('strong', class_='title', string=re.compile(r'정치\s*많이\s*본\s*기사'))
    
    if section_title:
        # 섹션 컨테이너 찾기 (3단계 상위 요소 = section 태그)
        section_container = section_title.find_parent()  # div
        if section_container:
            section_container = section_container.find_parent()  # header
        if section_container:
            section_container = section_container.find_parent()  # section
        
        if section_container:
            # 섹션 내의 순위가 있는 링크 찾기 (1, 2, 3, 4, 5 순위)
            for rank in range(1, max_articles + 1):
                # 순위 번호 찾기
                rank_elem = section_container.find(text=str(rank))
                if rank_elem:
                    # 순위 근처의 링크 찾기
                    parent = rank_elem.find_parent(['li', 'div', 'article'])
                    if parent:
                        link = parent.find('a', href=re.compile(r'/article/\d+'))
                        if link:
                            url = link.get('href', '')
                            if url and url not in processed_urls:
                                # 상대 URL을 절대 URL로 변환
                                if url.startswith('/'):
                                    full_url = f"https://www.joongang.co.kr{url}"
                                else:
                                    full_url = url
                                
                                # 제목 추출
                                title = link.get_text(strip=True)
                                
                                if title and len(title) >= 10 and not title.isdigit():
                                    # 이미지 URL 추출
                                    image_url = extract_image_url(link, "https://www.joongang.co.kr")
                                    
                                    news_item = {
                                        'title': clean_text(title),
                                        'url': full_url,
                                        'date': get_kst_now().strftime('%Y-%m-%d'),
                                        'category': '정치',
                                        'source': '중앙일보',
                                        'image_url': image_url,
                                        'scraped_at': get_kst_now().isoformat()
                                    }
                                    news_items.append(news_item)
                                    processed_urls.add(url)
    
    # 5개가 안 되면 일반 정치 기사로 보충
    if len(news_items) < max_articles:
        all_links = soup.find_all('a', href=re.compile(r'/article/\d+'))
        for link in all_links:
            if len(news_items) >= max_articles:
                break
                
            url = link.get('href', '')
            if not url or url in processed_urls:
                continue
            
            # 링크가 정치 컨텍스트에 있는지 확인
            parent = link.find_parent(['article', 'div', 'section', 'li'])
            is_politics = False
            
            if parent:
                parent_text = str(parent)
                if 'politics' in parent_text.lower():
                    is_politics = True
            
            if not is_politics:
                nearby_text = link.find_parent(['div', 'li'])
                if nearby_text:
                    text_content = nearby_text.get_text()
                    if '정치' in text_content and not any(word in text_content for word in ['경제', '스포츠', '문화', '연예', '사회', '국제']):
                        is_politics = True
            
            if not is_politics:
                continue
            
            # 상대 URL을 절대 URL로 변환
            if url.startswith('/'):
                full_url = f"https://www.joongang.co.kr{url}"
            else:
                full_url = url
            
            # 제목 추출
            title = link.get_text(strip=True)
            
            if not title or len(title) < 10 or title.isdigit():
                continue
            
            # 이미지 URL 추출
            image_url = extract_image_url(link, "https://www.joongang.co.kr")
            
            news_item = {
                'title': clean_text(title),
                'url': full_url,
                'date': get_kst_now().strftime('%Y-%m-%d'),
                'category': '정치',
                'source': '중앙일보',
                'image_url': image_url,
                'scraped_at': get_kst_now().isoformat()
            }
            
            news_items.append(news_item)
            processed_urls.add(url)
    
    return news_items[:max_articles]


# 하위 호환성을 위한 별칭
def parse_news_page(html_content: str) -> List[Dict[str, str]]:
    """
    parse_anthropic_news의 별칭 (하위 호환성)
    """
    return parse_anthropic_news(html_content)


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


def parse_joongang_sports(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    중앙일보 '스포츠 많이 본 기사' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 중앙일보 "스포츠 많이 본 기사" 섹션 찾기
    section_title = soup.find('strong', class_='title', string=re.compile(r'스포츠\s*많이\s*본\s*기사'))
    
    if section_title:
        # 3단계 상위 요소까지 탐색 (section 태그)
        section_container = section_title.find_parent()  # div
        if section_container:
            section_container = section_container.find_parent()  # header
        if section_container:
            section_container = section_container.find_parent()  # section
        
        if section_container:
            # 순위 번호로 기사 찾기 (1, 2, 3, 4, 5)
            for rank in range(1, max_articles + 1):
                rank_elem = section_container.find(string=str(rank))
                if rank_elem:
                    parent = rank_elem.find_parent(['li', 'div', 'article'])
                    if parent:
                        link = parent.find('a', href=re.compile(r'/article/\d+'))
                        if link:
                            url = link.get('href', '')
                            if url and url not in processed_urls:
                                if url.startswith('/'):
                                    full_url = f"https://www.joongang.co.kr{url}"
                                else:
                                    full_url = url
                                
                                title = link.get_text(strip=True)
                                
                                if title and len(title) >= 10 and not title.isdigit():
                                    news_item = {
                                        'title': clean_text(title),
                                        'url': full_url,
                                        'date': get_kst_now().strftime('%Y-%m-%d'),
                                        'category': '스포츠',
                                        'source': '중앙일보',
                                        'scraped_at': get_kst_now().isoformat()
                                    }
                                    news_items.append(news_item)
                                    processed_urls.add(url)
    
    # fallback: 섹션을 못 찾으면 스포츠 관련 링크 검색
    if len(news_items) < max_articles:
        all_links = soup.find_all('a', href=re.compile(r'/article/\d+'))
        for link in all_links:
            if len(news_items) >= max_articles:
                break
                
            url = link.get('href', '')
            if not url or url in processed_urls:
                continue
            
            # 스포츠 컨텍스트 확인
            parent = link.find_parent(['article', 'div', 'section', 'li'])
            is_sports = False
            
            if parent:
                parent_text = str(parent)
                if 'sports' in parent_text.lower() or 'sport' in parent_text.lower():
                    is_sports = True
            
            if not is_sports:
                nearby_text = link.find_parent(['div', 'li'])
                if nearby_text:
                    text_content = nearby_text.get_text()
                    if '스포츠' in text_content:
                        is_sports = True
            
            if not is_sports:
                continue
            
            if url.startswith('/'):
                full_url = f"https://www.joongang.co.kr{url}"
            else:
                full_url = url
            
            title = link.get_text(strip=True)
            
            if not title or len(title) < 10 or title.isdigit():
                continue
            
            news_item = {
                'title': clean_text(title),
                'url': full_url,
                'date': get_kst_now().strftime('%Y-%m-%d'),
                'category': '스포츠',
                'source': '중앙일보',
                'scraped_at': get_kst_now().isoformat()
            }
            news_items.append(news_item)
            processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_donga_sports(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    동아일보 '많이 본 스포츠 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 동아일보 '많이 본 스포츠 뉴스' 섹션 찾기
    trending_section = soup.find('h2', class_='sec_tit', string=re.compile(r'많이 본 스포츠 뉴스'))
    
    # fallback
    if not trending_section:
        trending_section = soup.find(string=re.compile(r'많이 본 스포츠 뉴스'))
    
    if trending_section:
        section_parent = trending_section.find_parent(['div', 'section', 'article'])
        if section_parent:
            news_links = section_parent.find_all('a', href=re.compile(r'/news/Sports/article/all/\d+/\d+/\d+'))
            
            for link in news_links:
                if len(news_items) >= max_articles:
                    break
                    
                url = link.get('href', '')
                
                if not url or url in processed_urls:
                    continue
                
                if url.startswith('/'):
                    full_url = f"https://www.donga.com{url}"
                else:
                    full_url = url
                
                title = link.get_text(strip=True)
                
                if not title or len(title) < 10:
                    continue
                
                # 이미지 URL 추출
                image_url = extract_image_url(link, "https://www.donga.com")
                
                # URL에서 날짜 추출
                date_str = ""
                date_match = re.search(r'/(\d{8})/', url)
                if date_match:
                    date_num = date_match.group(1)
                    date_str = f"{date_num[:4]}-{date_num[4:6]}-{date_num[6:8]}"
                
                if not date_str:
                    date_str = get_kst_now().strftime('%Y-%m-%d')
                
                news_item = {
                    'title': clean_text(title),
                    'url': full_url,
                    'date': date_str,
                    'category': '스포츠',
                    'source': '동아일보',
                    'image_url': image_url,
                    'scraped_at': get_kst_now().isoformat()
                }
                
                news_items.append(news_item)
                processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_chosun_sports(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    조선일보 '스포츠 많이 본 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 조선일보 '스포츠 많이 본 뉴스' 섹션 찾기
    trending_section = soup.find('div', class_='flex-chain__heading-title', string=re.compile(r'스포츠\s*많이\s*본\s*뉴스'))
    
    news_links = []
    if trending_section:
        # 2단계 상위 요소까지 탐색
        section_container = trending_section.find_parent()
        if section_container:
            section_container = section_container.find_parent()
        
        if section_container:
            news_links = section_container.find_all('a', href=re.compile(r'/sports/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    # fallback
    if not news_links:
        news_links = soup.find_all('a', href=re.compile(r'/sports/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    for link in news_links:
        if len(news_items) >= max_articles:
            break
            
        url = link.get('href', '')
        
        if not url or url in processed_urls:
            continue
        
        if url.startswith('/'):
            full_url = f"https://www.chosun.com{url}"
        else:
            full_url = url
        
        title = link.get_text(strip=True)
        
        if not title or len(title) < 10:
            continue
        
        # URL에서 날짜 추출
        date_str = ""
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f"{year}-{month}-{day}"
        
        if not date_str:
            date_str = get_kst_now().strftime('%Y-%m-%d')
        
        news_item = {
            'title': clean_text(title),
            'url': full_url,
            'date': date_str,
            'category': '스포츠',
            'source': '조선일보',
            'scraped_at': get_kst_now().isoformat()
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_joongang_economy(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    중앙일보 '경제 많이 본 기사' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 중앙일보 "경제 많이 본 기사" 섹션 찾기
    section_title = soup.find('strong', class_='title', string=re.compile(r'경제\s*많이\s*본\s*기사'))
    
    if section_title:
        # 3단계 상위 요소까지 탐색 (section 태그)
        section_container = section_title.find_parent()  # div
        if section_container:
            section_container = section_container.find_parent()  # header
        if section_container:
            section_container = section_container.find_parent()  # section
        
        if section_container:
            # 순위 번호로 기사 찾기 (1, 2, 3, 4, 5)
            for rank in range(1, max_articles + 1):
                rank_elem = section_container.find(string=str(rank))
                if rank_elem:
                    parent = rank_elem.find_parent(['li', 'div', 'article'])
                    if parent:
                        link = parent.find('a', href=re.compile(r'/article/\d+'))
                        if link:
                            url = link.get('href', '')
                            if url and url not in processed_urls:
                                if url.startswith('/'):
                                    full_url = f"https://www.joongang.co.kr{url}"
                                else:
                                    full_url = url
                                
                                title = link.get_text(strip=True)
                                
                                if title and len(title) >= 10 and not title.isdigit():
                                    news_item = {
                                        'title': clean_text(title),
                                        'url': full_url,
                                        'date': get_kst_now().strftime('%Y-%m-%d'),
                                        'category': '경제',
                                        'source': '중앙일보',
                                        'scraped_at': get_kst_now().isoformat(),
                                        'main_category': '경제'
                                    }
                                    news_items.append(news_item)
                                    processed_urls.add(url)
    
    # fallback: 섹션을 못 찾으면 경제 관련 링크 검색
    if len(news_items) < max_articles:
        all_links = soup.find_all('a', href=re.compile(r'/article/\d+'))
        for link in all_links:
            if len(news_items) >= max_articles:
                break
                
            url = link.get('href', '')
            if not url or url in processed_urls:
                continue
            
            # 경제 컨텍스트 확인
            parent = link.find_parent(['article', 'div', 'section', 'li'])
            is_economy = False
            
            if parent:
                parent_text = str(parent)
                if 'economy' in parent_text.lower():
                    is_economy = True
            
            if not is_economy:
                nearby_text = link.find_parent(['div', 'li'])
                if nearby_text:
                    text_content = nearby_text.get_text()
                    if '경제' in text_content:
                        is_economy = True
            
            if not is_economy:
                continue
            
            if url.startswith('/'):
                full_url = f"https://www.joongang.co.kr{url}"
            else:
                full_url = url
            
            title = link.get_text(strip=True)
            
            if not title or len(title) < 10 or title.isdigit():
                continue
            
            news_item = {
                'title': clean_text(title),
                'url': full_url,
                'date': get_kst_now().strftime('%Y-%m-%d'),
                'category': '경제',
                'source': '중앙일보',
                'scraped_at': get_kst_now().isoformat(),
                'main_category': '경제'
            }
            news_items.append(news_item)
            processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_donga_economy(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    동아일보 '많이 본 경제 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 동아일보 '많이 본 경제 뉴스' 섹션 찾기
    trending_section = soup.find('h2', class_='sec_tit', string=re.compile(r'많이 본 경제 뉴스'))
    
    # fallback
    if not trending_section:
        trending_section = soup.find(string=re.compile(r'많이 본 경제 뉴스'))
    
    if trending_section:
        section_parent = trending_section.find_parent(['div', 'section', 'article'])
        if section_parent:
            news_links = section_parent.find_all('a', href=re.compile(r'/news/Economy/article/all/\d+/\d+/\d+'))
            
            for link in news_links:
                if len(news_items) >= max_articles:
                    break
                    
                url = link.get('href', '')
                
                if not url or url in processed_urls:
                    continue
                
                if url.startswith('/'):
                    full_url = f"https://www.donga.com{url}"
                else:
                    full_url = url
                
                title = link.get_text(strip=True)
                
                if not title or len(title) < 10:
                    continue
                
                # URL에서 날짜 추출
                date_str = ""
                date_match = re.search(r'/(\d{8})/', url)
                if date_match:
                    date_num = date_match.group(1)
                    date_str = f"{date_num[:4]}-{date_num[4:6]}-{date_num[6:8]}"
                
                if not date_str:
                    date_str = get_kst_now().strftime('%Y-%m-%d')
                
                news_item = {
                    'title': clean_text(title),
                    'url': full_url,
                    'date': date_str,
                    'category': '경제',
                    'source': '동아일보',
                    'scraped_at': get_kst_now().isoformat(),
                    'main_category': '경제'
                }
                
                news_items.append(news_item)
                processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_chosun_economy(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    조선일보 '조선경제 많이 본 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 조선일보 '조선경제 많이 본 뉴스' 섹션 찾기
    trending_section = soup.find('div', class_='flex-chain__heading-title', string=re.compile(r'조선경제\s*많이\s*본\s*뉴스'))
    
    news_links = []
    if trending_section:
        # 2단계 상위 요소까지 탐색
        section_container = trending_section.find_parent()
        if section_container:
            section_container = section_container.find_parent()
        
        if section_container:
            news_links = section_container.find_all('a', href=re.compile(r'/economy/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    # fallback
    if not news_links:
        news_links = soup.find_all('a', href=re.compile(r'/economy/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    for link in news_links:
        if len(news_items) >= max_articles:
            break
            
        url = link.get('href', '')
        
        if not url or url in processed_urls:
            continue
        
        if url.startswith('/'):
            full_url = f"https://www.chosun.com{url}"
        else:
            full_url = url
        
        title = link.get_text(strip=True)
        
        if not title or len(title) < 10:
            continue
        
        # URL에서 날짜 추출
        date_str = ""
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f"{year}-{month}-{day}"
        
        if not date_str:
            date_str = get_kst_now().strftime('%Y-%m-%d')
        
        news_item = {
            'title': clean_text(title),
            'url': full_url,
            'date': date_str,
            'category': '경제',
            'source': '조선일보',
            'scraped_at': get_kst_now().isoformat(),
            'main_category': '경제'
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    return news_items[:max_articles]


# ===========================================
# 사회 뉴스 파서 함수들
# ===========================================

def parse_chosun_society(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    조선일보 '사회 많이 본 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 조선일보 '사회 많이 본 뉴스' 섹션 찾기
    trending_section = soup.find('div', class_='flex-chain__heading-title', string=re.compile(r'사회\s*많이\s*본\s*뉴스'))
    
    news_links = []
    if trending_section:
        # 2단계 상위 요소까지 탐색
        section_container = trending_section.find_parent()
        if section_container:
            section_container = section_container.find_parent()
        
        if section_container:
            news_links = section_container.find_all('a', href=re.compile(r'/national/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    # fallback: 섹션을 못 찾으면 전체 페이지에서 검색
    if not news_links:
        news_links = soup.find_all('a', href=re.compile(r'/national/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    for link in news_links:
        if len(news_items) >= max_articles:
            break
            
        url = link.get('href', '')
        
        if not url or url in processed_urls:
            continue
        
        # 상대 URL을 절대 URL로 변환
        if url.startswith('/'):
            full_url = f"https://www.chosun.com{url}"
        else:
            full_url = url
        
        # 제목 추출
        title = link.get_text(strip=True)
        
        # 제목이 너무 짧으면 다음 링크로
        if not title or len(title) < 10:
            continue
        
        # 이미지 URL 추출
        image_url = extract_image_url(link, "https://www.chosun.com")
        
        # URL에서 날짜 추출 (패턴: /2025/12/01/...)
        date_str = ""
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f"{year}-{month}-{day}"
        
        if not date_str:
            date_str = get_kst_now().strftime('%Y-%m-%d')
        
        news_item = {
            'title': clean_text(title),
            'url': full_url,
            'date': date_str,
            'category': '사회',
            'source': '조선일보',
            'image_url': image_url,
            'scraped_at': get_kst_now().isoformat()
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_joongang_society(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    중앙일보 사회 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 중앙일보 "사회 많이 본 기사" 섹션 찾기
    section_title = soup.find('strong', class_='title', string=re.compile(r'사회\s*많이\s*본\s*기사'))
    
    if section_title:
        # 섹션 컨테이너 찾기 (3단계 상위 요소 = section 태그)
        section_container = section_title.find_parent()  # div
        if section_container:
            section_container = section_container.find_parent()  # header
        if section_container:
            section_container = section_container.find_parent()  # section
        
        if section_container:
            # 섹션 내의 순위가 있는 링크 찾기 (1, 2, 3, 4, 5 순위)
            for rank in range(1, max_articles + 1):
                # 순위 번호 찾기
                rank_elem = section_container.find(text=str(rank))
                if rank_elem:
                    # 순위 근처의 링크 찾기
                    parent = rank_elem.find_parent(['li', 'div', 'article'])
                    if parent:
                        link = parent.find('a', href=re.compile(r'/article/\d+'))
                        if link:
                            url = link.get('href', '')
                            if url and url not in processed_urls:
                                # 상대 URL을 절대 URL로 변환
                                if url.startswith('/'):
                                    full_url = f"https://www.joongang.co.kr{url}"
                                else:
                                    full_url = url
                                
                                # 제목 추출
                                title = link.get_text(strip=True)
                                
                                if title and len(title) >= 10 and not title.isdigit():
                                    # 이미지 URL 추출
                                    image_url = extract_image_url(link, "https://www.joongang.co.kr")
                                    
                                    news_item = {
                                        'title': clean_text(title),
                                        'url': full_url,
                                        'date': get_kst_now().strftime('%Y-%m-%d'),
                                        'category': '사회',
                                        'source': '중앙일보',
                                        'image_url': image_url,
                                        'scraped_at': get_kst_now().isoformat()
                                    }
                                    news_items.append(news_item)
                                    processed_urls.add(url)
    
    # 5개가 안 되면 일반 사회 기사로 보충
    if len(news_items) < max_articles:
        all_links = soup.find_all('a', href=re.compile(r'/article/\d+'))
        for link in all_links:
            if len(news_items) >= max_articles:
                break
                
            url = link.get('href', '')
            if not url or url in processed_urls:
                continue
            
            # 상대 URL을 절대 URL로 변환
            if url.startswith('/'):
                full_url = f"https://www.joongang.co.kr{url}"
            else:
                full_url = url
            
            # 제목 추출
            title = link.get_text(strip=True)
            
            if not title or len(title) < 10 or title.isdigit():
                continue
            
            # 이미지 URL 추출
            image_url = extract_image_url(link, "https://www.joongang.co.kr")
            
            news_item = {
                'title': clean_text(title),
                'url': full_url,
                'date': get_kst_now().strftime('%Y-%m-%d'),
                'category': '사회',
                'source': '중앙일보',
                'image_url': image_url,
                'scraped_at': get_kst_now().isoformat()
            }
            
            news_items.append(news_item)
            processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_donga_society(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    동아일보 '많이 본 사회 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 동아일보 '많이 본 사회 뉴스' 섹션 찾기
    trending_section = soup.find('h2', class_='sec_tit', string=re.compile(r'많이 본 사회 뉴스'))
    
    # fallback: h2 태그를 못 찾으면 일반 text 검색
    if not trending_section:
        trending_section = soup.find(string=re.compile(r'많이 본 사회 뉴스'))
    
    if trending_section:
        # 많이 본 뉴스 섹션 컨테이너 찾기
        section_parent = trending_section.find_parent(['div', 'section', 'article'])
        if section_parent:
            # 해당 섹션 내의 뉴스 링크 찾기
            news_links = section_parent.find_all('a', href=re.compile(r'/news/Society/article/all/\d+/\d+/\d+'))
            
            for link in news_links:
                if len(news_items) >= max_articles:
                    break
                    
                url = link.get('href', '')
                
                if not url or url in processed_urls:
                    continue
                
                # 상대 URL을 절대 URL로 변환
                if url.startswith('/'):
                    full_url = f"https://www.donga.com{url}"
                else:
                    full_url = url
                
                # 제목 추출
                title = link.get_text(strip=True)
                
                # 제목이 너무 짧으면 다음 링크로
                if not title or len(title) < 10:
                    continue
                
                # 이미지 URL 추출
                image_url = extract_image_url(link, "https://www.donga.com")
                
                # URL에서 날짜 추출
                date_str = ""
                date_match = re.search(r'/(\d{8})/', url)
                if date_match:
                    date_num = date_match.group(1)
                    date_str = f"{date_num[:4]}-{date_num[4:6]}-{date_num[6:8]}"
                
                if not date_str:
                    date_str = get_kst_now().strftime('%Y-%m-%d')
                
                news_item = {
                    'title': clean_text(title),
                    'url': full_url,
                    'date': date_str,
                    'category': '사회',
                    'source': '동아일보',
                    'image_url': image_url,
                    'scraped_at': get_kst_now().isoformat()
                }
                
                news_items.append(news_item)
                processed_urls.add(url)
    
    return news_items[:max_articles]


# ===========================================
# 국제 뉴스 파서 함수들
# ===========================================

def parse_chosun_international(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    조선일보 '국제 많이 본 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 조선일보 '국제 많이 본 뉴스' 섹션 찾기
    trending_section = soup.find('div', class_='flex-chain__heading-title', string=re.compile(r'국제\s*많이\s*본\s*뉴스'))
    
    news_links = []
    if trending_section:
        # 2단계 상위 요소까지 탐색
        section_container = trending_section.find_parent()
        if section_container:
            section_container = section_container.find_parent()
        
        if section_container:
            news_links = section_container.find_all('a', href=re.compile(r'/international/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    # fallback: 섹션을 못 찾으면 전체 페이지에서 검색
    if not news_links:
        news_links = soup.find_all('a', href=re.compile(r'/international/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
    
    for link in news_links:
        if len(news_items) >= max_articles:
            break
            
        url = link.get('href', '')
        
        if not url or url in processed_urls:
            continue
        
        # 상대 URL을 절대 URL로 변환
        if url.startswith('/'):
            full_url = f"https://www.chosun.com{url}"
        else:
            full_url = url
        
        # 제목 추출
        title = link.get_text(strip=True)
        
        # 제목이 너무 짧으면 다음 링크로
        if not title or len(title) < 10:
            continue
        
        # 이미지 URL 추출
        image_url = extract_image_url(link, "https://www.chosun.com")
        
        # URL에서 날짜 추출 (패턴: /2025/12/01/...)
        date_str = ""
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f"{year}-{month}-{day}"
        
        if not date_str:
            date_str = get_kst_now().strftime('%Y-%m-%d')
        
        news_item = {
            'title': clean_text(title),
            'url': full_url,
            'date': date_str,
            'category': '국제',
            'source': '조선일보',
            'image_url': image_url,
            'scraped_at': get_kst_now().isoformat()
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_joongang_international(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    중앙일보 국제 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 중앙일보 "국제 많이 본 기사" 섹션 찾기
    section_title = soup.find('strong', class_='title', string=re.compile(r'국제\s*많이\s*본\s*기사'))
    
    if section_title:
        # 섹션 컨테이너 찾기 (3단계 상위 요소 = section 태그)
        section_container = section_title.find_parent()  # div
        if section_container:
            section_container = section_container.find_parent()  # header
        if section_container:
            section_container = section_container.find_parent()  # section
        
        if section_container:
            # 섹션 내의 순위가 있는 링크 찾기 (1, 2, 3, 4, 5 순위)
            for rank in range(1, max_articles + 1):
                # 순위 번호 찾기
                rank_elem = section_container.find(text=str(rank))
                if rank_elem:
                    # 순위 근처의 링크 찾기
                    parent = rank_elem.find_parent(['li', 'div', 'article'])
                    if parent:
                        link = parent.find('a', href=re.compile(r'/article/\d+'))
                        if link:
                            url = link.get('href', '')
                            if url and url not in processed_urls:
                                # 상대 URL을 절대 URL로 변환
                                if url.startswith('/'):
                                    full_url = f"https://www.joongang.co.kr{url}"
                                else:
                                    full_url = url
                                
                                # 제목 추출
                                title = link.get_text(strip=True)
                                
                                if title and len(title) >= 10 and not title.isdigit():
                                    # 이미지 URL 추출
                                    image_url = extract_image_url(link, "https://www.joongang.co.kr")
                                    
                                    news_item = {
                                        'title': clean_text(title),
                                        'url': full_url,
                                        'date': get_kst_now().strftime('%Y-%m-%d'),
                                        'category': '국제',
                                        'source': '중앙일보',
                                        'image_url': image_url,
                                        'scraped_at': get_kst_now().isoformat()
                                    }
                                    news_items.append(news_item)
                                    processed_urls.add(url)
    
    # 5개가 안 되면 일반 국제 기사로 보충
    if len(news_items) < max_articles:
        all_links = soup.find_all('a', href=re.compile(r'/article/\d+'))
        for link in all_links:
            if len(news_items) >= max_articles:
                break
                
            url = link.get('href', '')
            if not url or url in processed_urls:
                continue
            
            # 상대 URL을 절대 URL로 변환
            if url.startswith('/'):
                full_url = f"https://www.joongang.co.kr{url}"
            else:
                full_url = url
            
            # 제목 추출
            title = link.get_text(strip=True)
            
            if not title or len(title) < 10 or title.isdigit():
                continue
            
            # 이미지 URL 추출
            image_url = extract_image_url(link, "https://www.joongang.co.kr")
            
            news_item = {
                'title': clean_text(title),
                'url': full_url,
                'date': get_kst_now().strftime('%Y-%m-%d'),
                'category': '국제',
                'source': '중앙일보',
                'image_url': image_url,
                'scraped_at': get_kst_now().isoformat()
            }
            
            news_items.append(news_item)
            processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_donga_international(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    동아일보 '많이 본 국제 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 동아일보 '많이 본 국제 뉴스' 섹션 찾기
    trending_section = soup.find('h2', class_='sec_tit', string=re.compile(r'많이 본 국제 뉴스'))
    
    # fallback: h2 태그를 못 찾으면 일반 text 검색
    if not trending_section:
        trending_section = soup.find(string=re.compile(r'많이 본 국제 뉴스'))
    
    if trending_section:
        # 많이 본 뉴스 섹션 컨테이너 찾기
        section_parent = trending_section.find_parent(['div', 'section', 'article'])
        if section_parent:
            # 해당 섹션 내의 뉴스 링크 찾기
            news_links = section_parent.find_all('a', href=re.compile(r'/news/Inter/article/all/\d+/\d+/\d+'))
            
            for link in news_links:
                if len(news_items) >= max_articles:
                    break
                    
                url = link.get('href', '')
                
                if not url or url in processed_urls:
                    continue
                
                # 상대 URL을 절대 URL로 변환
                if url.startswith('/'):
                    full_url = f"https://www.donga.com{url}"
                else:
                    full_url = url
                
                # 제목 추출
                title = link.get_text(strip=True)
                
                # 제목이 너무 짧으면 다음 링크로
                if not title or len(title) < 10:
                    continue
                
                # 이미지 URL 추출
                image_url = extract_image_url(link, "https://www.donga.com")
                
                # URL에서 날짜 추출
                date_str = ""
                date_match = re.search(r'/(\d{8})/', url)
                if date_match:
                    date_num = date_match.group(1)
                    date_str = f"{date_num[:4]}-{date_num[4:6]}-{date_num[6:8]}"
                
                if not date_str:
                    date_str = get_kst_now().strftime('%Y-%m-%d')
                
                news_item = {
                    'title': clean_text(title),
                    'url': full_url,
                    'date': date_str,
                    'category': '국제',
                    'source': '동아일보',
                    'image_url': image_url,
                    'scraped_at': get_kst_now().isoformat()
                }
                
                news_items.append(news_item)
                processed_urls.add(url)
    
    return news_items[:max_articles]


# ===========================================
# 문화 뉴스 파서 함수들
# ===========================================

def parse_chosun_culture(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    조선일보 '문화·라이프 많이 본 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 방법 1: "문화·라이프 많이 본 뉴스" 섹션 찾기
    headings = soup.find_all('div', class_='flex-chain__heading-title')
    culture_section = None
    
    for heading in headings:
        heading_text = heading.get_text(strip=True)
        if '문화' in heading_text and '라이프' in heading_text and '많이' in heading_text:
            culture_section = heading.find_parent('section', class_='flex-chain')
            break
    
    news_links = []
    if culture_section:
        # 섹션 내의 모든 링크 찾기
        all_links = culture_section.find_all('a', href=True)
        for link in all_links:
            url = link.get('href', '')
            # 문화/연예 카테고리 URL 패턴 확인
            if re.match(r'/(culture-life|entertainments)/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?', url):
                news_links.append(link)
    
    # 방법 2: 충분한 링크를 못 찾으면 전체 페이지에서 culture-life와 entertainments 검색
    if len(news_links) < max_articles:
        # 두 카테고리 모두 검색
        additional_links = soup.find_all('a', href=re.compile(r'/(culture-life|entertainments)/[^/]+/\d{4}/\d{2}/\d{2}/[A-Z0-9]+/?'))
        
        # 이미 추가한 URL 확인
        existing_urls = set(link.get('href', '') for link in news_links)
        
        for link in additional_links:
            if len(news_links) >= max_articles:
                break
            url = link.get('href', '')
            if url and url not in existing_urls:
                news_links.append(link)
                existing_urls.add(url)
    
    for link in news_links:
        if len(news_items) >= max_articles:
            break
            
        url = link.get('href', '')
        
        if not url or url in processed_urls:
            continue
        
        # 상대 URL을 절대 URL로 변환
        if url.startswith('/'):
            full_url = f"https://www.chosun.com{url}"
        else:
            full_url = url
        
        # 제목 추출 (h2, h3, h4, h5 태그에서)
        title_elem = link.find(['h2', 'h3', 'h4', 'h5', 'h6'])
        if title_elem:
            title = title_elem.get_text(strip=True)
        else:
            title = link.get_text(strip=True)
        
        # 제목이 너무 짧으면 다음 링크로
        if not title or len(title) < 10:
            continue
        
        # 이미지 URL 추출
        image_url = extract_image_url(link, "https://www.chosun.com")
        
        # URL에서 날짜 추출 (패턴: /2025/12/01/...)
        date_str = ""
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f"{year}-{month}-{day}"
        
        if not date_str:
            date_str = get_kst_now().strftime('%Y-%m-%d')
        
        news_item = {
            'title': clean_text(title),
            'url': full_url,
            'date': date_str,
            'category': '문화',
            'source': '조선일보',
            'image_url': image_url,
            'scraped_at': get_kst_now().isoformat()
        }
        
        news_items.append(news_item)
        processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_joongang_culture(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    중앙일보 문화 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 중앙일보 "문화 많이 본 기사" 섹션 찾기
    section_title = soup.find('strong', class_='title', string=re.compile(r'문화\s*많이\s*본\s*기사'))
    
    if section_title:
        # 섹션 컨테이너 찾기 (3단계 상위 요소 = section 태그)
        section_container = section_title.find_parent()  # div
        if section_container:
            section_container = section_container.find_parent()  # header
        if section_container:
            section_container = section_container.find_parent()  # section
        
        if section_container:
            # 섹션 내의 순위가 있는 링크 찾기 (1, 2, 3, 4, 5 순위)
            for rank in range(1, max_articles + 1):
                # 순위 번호 찾기
                rank_elem = section_container.find(text=str(rank))
                if rank_elem:
                    # 순위 근처의 링크 찾기
                    parent = rank_elem.find_parent(['li', 'div', 'article'])
                    if parent:
                        link = parent.find('a', href=re.compile(r'/article/\d+'))
                        if link:
                            url = link.get('href', '')
                            if url and url not in processed_urls:
                                # 상대 URL을 절대 URL로 변환
                                if url.startswith('/'):
                                    full_url = f"https://www.joongang.co.kr{url}"
                                else:
                                    full_url = url
                                
                                # 제목 추출
                                title = link.get_text(strip=True)
                                
                                if title and len(title) >= 10 and not title.isdigit():
                                    # 이미지 URL 추출
                                    image_url = extract_image_url(link, "https://www.joongang.co.kr")
                                    
                                    news_item = {
                                        'title': clean_text(title),
                                        'url': full_url,
                                        'date': get_kst_now().strftime('%Y-%m-%d'),
                                        'category': '문화',
                                        'source': '중앙일보',
                                        'image_url': image_url,
                                        'scraped_at': get_kst_now().isoformat()
                                    }
                                    news_items.append(news_item)
                                    processed_urls.add(url)
    
    # 5개가 안 되면 일반 문화 기사로 보충
    if len(news_items) < max_articles:
        all_links = soup.find_all('a', href=re.compile(r'/article/\d+'))
        for link in all_links:
            if len(news_items) >= max_articles:
                break
                
            url = link.get('href', '')
            if not url or url in processed_urls:
                continue
            
            # 상대 URL을 절대 URL로 변환
            if url.startswith('/'):
                full_url = f"https://www.joongang.co.kr{url}"
            else:
                full_url = url
            
            # 제목 추출
            title = link.get_text(strip=True)
            
            if not title or len(title) < 10 or title.isdigit():
                continue
            
            # 이미지 URL 추출
            image_url = extract_image_url(link, "https://www.joongang.co.kr")
            
            news_item = {
                'title': clean_text(title),
                'url': full_url,
                'date': get_kst_now().strftime('%Y-%m-%d'),
                'category': '문화',
                'source': '중앙일보',
                'image_url': image_url,
                'scraped_at': get_kst_now().isoformat()
            }
            
            news_items.append(news_item)
            processed_urls.add(url)
    
    return news_items[:max_articles]


def parse_donga_culture(html_content: str, max_articles: int = 5) -> List[Dict[str, str]]:
    """
    동아일보 '많이 본 문화 뉴스' 섹션에서 상위 기사 리스트를 반환합니다.
    
    Args:
        html_content: 뉴스 페이지의 HTML 문자열
        max_articles: 최대 기사 수 (기본값: 5)
        
    Returns:
        뉴스 항목 딕셔너리 리스트
    """
    soup = BeautifulSoup(html_content, 'lxml')
    news_items = []
    processed_urls = set()
    
    # 동아일보 '많이 본 문화 뉴스' 섹션 찾기
    trending_section = soup.find('h2', class_='sec_tit', string=re.compile(r'많이 본 문화 뉴스'))
    
    # fallback: h2 태그를 못 찾으면 일반 text 검색
    if not trending_section:
        trending_section = soup.find(string=re.compile(r'많이 본 문화 뉴스'))
    
    if trending_section:
        # 많이 본 뉴스 섹션 컨테이너 찾기
        section_parent = trending_section.find_parent(['div', 'section', 'article'])
        if section_parent:
            # 해당 섹션 내의 뉴스 링크 찾기
            news_links = section_parent.find_all('a', href=re.compile(r'/news/Culture/article/all/\d+/\d+/\d+'))
            
            for link in news_links:
                if len(news_items) >= max_articles:
                    break
                    
                url = link.get('href', '')
                
                if not url or url in processed_urls:
                    continue
                
                # 상대 URL을 절대 URL로 변환
                if url.startswith('/'):
                    full_url = f"https://www.donga.com{url}"
                else:
                    full_url = url
                
                # 제목 추출
                title = link.get_text(strip=True)
                
                # 제목이 너무 짧으면 다음 링크로
                if not title or len(title) < 10:
                    continue
                
                # 이미지 URL 추출
                image_url = extract_image_url(link, "https://www.donga.com")
                
                # URL에서 날짜 추출
                date_str = ""
                date_match = re.search(r'/(\d{8})/', url)
                if date_match:
                    date_num = date_match.group(1)
                    date_str = f"{date_num[:4]}-{date_num[4:6]}-{date_num[6:8]}"
                
                if not date_str:
                    date_str = get_kst_now().strftime('%Y-%m-%d')
                
                news_item = {
                    'title': clean_text(title),
                    'url': full_url,
                    'date': date_str,
                    'category': '문화',
                    'source': '동아일보',
                    'image_url': image_url,
                    'scraped_at': get_kst_now().isoformat()
                }
                
                news_items.append(news_item)
                processed_urls.add(url)
    
    return news_items[:max_articles]


