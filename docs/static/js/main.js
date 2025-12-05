/**
 * Hyeok Crawler 뉴스 포털 - GitHub Pages 정적 버전
 * JSON 파일을 직접 로드하여 표시
 */

// 현재 선택된 카테고리와 소스
let currentCategory = 'politics';
let currentSource = 'donga';
let tickerSwiper = null;

// 북마크 관리
let bookmarks = [];

/**
 * 페이지 로드 시 초기화
 */
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initBookmarks();
    initNavigation();
    initDatePicker();
    initTrendPanel();
    loadInitialTrendBadge();
    
    // 초기 카테고리 라벨 설정
    updateSourceTitle(currentSource, currentCategory);
});

/**
 * 초기 트렌드 배지 로드
 */
async function loadInitialTrendBadge() {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const todayStr = `${yyyy}-${mm}-${dd}`;
    
    try {
        const response = await fetch(`data/trends/trends_${todayStr}.json`);
        if (response.ok) {
            const trendData = await response.json();
            const trendBadge = document.getElementById('trend-badge');
            
            if (trendData.daily_top_keywords.length > 0) {
                trendBadge.textContent = trendData.daily_top_keywords[0].word;
                trendBadge.classList.add('visible');
            }
        }
    } catch (error) {
        console.log('초기 트렌드 배지 로드 실패:', error);
    }
}

/**
 * 날짜 선택기 초기화 (index.html에서 호출)
 */
function initDatePicker() {
    const dateInput = document.getElementById('date-select');
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const todayStr = `${yyyy}-${mm}-${dd}`;
    
    dateInput.value = todayStr;
    dateInput.max = todayStr;
    
    // 날짜 변경 시 뉴스 다시 로드
    dateInput.addEventListener('change', function() {
        loadNews(currentCategory, currentSource, this.value);
        initNewsTicker(this.value);
    });
    
    // 초기 뉴스 로드 (날짜 선택기 초기화 후)
    loadNews(currentCategory, currentSource, todayStr);
    initNewsTicker(todayStr);
}

/**
 * 다크모드 초기화 및 토글
 */
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // 저장된 테마 적용
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // 토글 버튼 클릭 이벤트
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

/**
 * 네비게이션 이벤트 리스너 설정
 */
function initNavigation() {
    let hoveredCategory = null;
    
    // 카테고리 호버 - 호버 상태 표시
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            hoveredCategory = this.dataset.category;
            this.classList.add('hover');
        });
        
        item.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });
        
        // 카테고리 클릭 - 카테고리 선택
        item.addEventListener('click', function(e) {
            const category = this.dataset.category;
            currentCategory = category;
            
            updateSourceTitle(currentSource, category);
            
            const selectedDate = document.getElementById('date-select').value;
            loadNews(category, currentSource, selectedDate);
        });
    });
    
    // 드롭다운 영역 호버 시에도 카테고리 호버 상태 유지
    const sharedDropdown = document.querySelector('.shared-dropdown');
    if (sharedDropdown) {
        sharedDropdown.addEventListener('mouseenter', function() {
            if (hoveredCategory) {
                const categoryItem = document.querySelector(`.category-item[data-category="${hoveredCategory}"]`);
                if (categoryItem) {
                    categoryItem.classList.add('hover');
                }
            }
        });
        
        sharedDropdown.addEventListener('mouseleave', function() {
            document.querySelectorAll('.category-item').forEach(cat => {
                cat.classList.remove('hover');
            });
            hoveredCategory = null;
        });
    }
    
    // 소스(언론사) 클릭
    document.querySelectorAll('.source-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const source = this.dataset.source;
            const targetCategory = hoveredCategory || currentCategory;
            
            document.querySelectorAll('.source-item').forEach(src => {
                src.classList.remove('active');
            });
            
            this.classList.add('active');
            
            currentCategory = targetCategory;
            currentSource = source;
            
            updateSourceTitle(source, targetCategory);
            
            const selectedDate = document.getElementById('date-select').value;
            loadNews(targetCategory, source, selectedDate);
        });
    });
}

/**
 * 신문사 제목과 로고 업데이트
 */
function updateSourceTitle(source, category = null) {
    const sourceNames = {
        'donga': '동아일보',
        'chosun': '조선일보',
        'joongang': '중앙일보'
    };
    
    const sourceLogos = {
        'donga': 'static/images/donga.png?v=2',
        'chosun': 'static/images/chosun.png?v=2',
        'joongang': 'static/images/joongang.png?v=2'
    };
    
    const categoryNames = {
        'politics': '정치',
        'sports': '스포츠',
        'economy': '경제',
        'society': '사회',
        'international': '국제',
        'culture': '문화'
    };
    
    const sourceLogoElement = document.getElementById('source-logo');
    const categoryLabelElement = document.getElementById('category-label');
    
    // 로고 업데이트
    if (sourceLogoElement && sourceLogos[source]) {
        sourceLogoElement.src = sourceLogos[source];
        sourceLogoElement.alt = sourceNames[source];
    }
    
    // 카테고리 라벨 업데이트
    if (categoryLabelElement) {
        const targetCategory = category || currentCategory;
        const sourceNameElement = document.getElementById('source-name');
        
        // HTML 구조: 카테고리 배지 > 로고 > 신문사 이름 순서
        if (sourceNameElement && sourceNames[source]) {
            sourceNameElement.innerHTML = `<span id="category-label" class="category-label ${targetCategory}">${categoryNames[targetCategory] || '정치'}</span><img id="source-logo" src="${sourceLogos[source]}" alt="${sourceNames[source]}">${sourceNames[source]}`;
        }
    }
}

/**
 * 최신 뉴스 관련 함수 제거 - 히어로 섹션으로 대체
 */

/**
 * 뉴스 데이터 로드 - JSON 파일에서 직접 로드
 */
async function loadNews(category, source, date) {
    const loadingEl = document.getElementById('loading-spinner');
    const errorEl = document.getElementById('error-message');
    const emptyEl = document.getElementById('empty-state');
    const gridEl = document.getElementById('news-grid');
    
    // 로딩 상태 표시
    loadingEl.style.display = 'flex';
    errorEl.style.display = 'none';
    emptyEl.style.display = 'none';
    gridEl.innerHTML = '';
    
    try {
        // JSON 파일 경로
        const response = await fetch(`data/${category}/${source}/news_${date}.json`);
        
        if (!response.ok) {
            throw new Error('Data not found');
        }
        
        const data = await response.json();
        
        loadingEl.style.display = 'none';
        
        if (data && data.length > 0) {
            renderNewsGrid(data);
            emptyEl.style.display = 'none';
        } else {
            gridEl.innerHTML = '';
            showEmptyState(date);
        }
    } catch (error) {
        console.error('Error loading news:', error);
        loadingEl.style.display = 'none';
        gridEl.innerHTML = '';
        showEmptyState(date);
    }
}

/**
 * 빈 상태 메시지 표시 (오늘/과거 날짜 구분)
 */
function showEmptyState(selectedDate) {
    const emptyEl = document.getElementById('empty-state');
    const titleEl = document.getElementById('empty-state-title');
    const descEl = document.getElementById('empty-state-description');
    
    // 오늘 날짜 확인
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const selected = new Date(selectedDate);
    selected.setHours(0, 0, 0, 0);
    
    // 오늘 날짜인 경우 크롤링 전 메시지 표시
    if (selected.getTime() === today.getTime()) {
        titleEl.textContent = '오늘의 기사가 아직 업데이트되지 않았습니다';
        descEl.textContent = '매일 오전 9시 20분에 업데이트됩니다';
    } else {
        // 과거 날짜인 경우 기본 메시지
        titleEl.textContent = '해당 날짜의 기사가 존재하지 않습니다';
        descEl.textContent = '다른 날짜를 선택해주세요';
    }
    
    emptyEl.style.display = 'block';
}

/**
 * 뉴스 그리드 렌더링
 */
function renderNewsGrid(newsItems) {
    const gridEl = document.getElementById('news-grid');
    
    gridEl.innerHTML = newsItems.map(item => {
        const categoryClass = getCategoryClass(item.category || item.main_category);
        const newsId = generateNewsId(item);
        const isBookmarked = checkIfBookmarked(newsId);
        const bookmarkClass = isBookmarked ? 'bookmarked' : '';
        
        return `
        <article class="news-card" data-news-id="${newsId}" data-news-data='${JSON.stringify(item).replace(/'/g, "&apos;")}'>
            <button class="bookmark-btn ${bookmarkClass}" 
                    data-news-id="${newsId}"
                    aria-label="북마크">
                <svg class="bookmark-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
            </button>
            <button class="share-btn" 
                    data-news-id="${newsId}"
                    aria-label="공유">
                <svg class="share-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="18" cy="5" r="3"></circle>
                    <circle cx="6" cy="12" r="3"></circle>
                    <circle cx="18" cy="19" r="3"></circle>
                    <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
                    <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
                </svg>
            </button>
            <div class="news-card-image-wrapper" onclick="window.open('${escapeHtml(item.url)}', '_blank')">
                <img src="${getNewsImage(item)}" 
                     alt="${escapeHtml(item.title)}" 
                     class="news-card-image"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                     loading="lazy">
                <div class="news-card-no-image" style="display: none;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                    </svg>
                    <span>이미지 준비중</span>
                </div>
            </div>
            <div class="news-card-content" onclick="window.open('${escapeHtml(item.url)}', '_blank')" style="cursor: pointer;">
                <div class="news-card-header">
                    <span class="news-card-category ${categoryClass}">${escapeHtml(item.category || item.main_category)}</span>
                    <span class="news-card-date">${formatDate(item.date)}</span>
                </div>
                <h3 class="news-card-title">${escapeHtml(item.title)}</h3>
                <div class="news-card-source">
                    <img src="${getSourceLogo(item.source)}" alt="${escapeHtml(item.source)}">
                    <span>${escapeHtml(item.source)}</span>
                </div>
            </div>
        </article>
        `;
    }).join('');
    
    // 북마크 버튼에 이벤트 리스너 추가
    attachBookmarkListeners();
    
    // 공유 버튼에 이벤트 리스너 추가
    attachShareListeners();
}

/**
 * 북마크 버튼에 이벤트 리스너 추가
 */
function attachBookmarkListeners() {
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const card = this.closest('.news-card');
            if (!card) return;
            
            const newsDataStr = card.getAttribute('data-news-data');
            if (!newsDataStr) return;
            
            try {
                const newsItem = JSON.parse(newsDataStr.replace(/&apos;/g, "'"));
                toggleBookmark(newsItem, this); // 버튼 요소 전달
            } catch (error) {
                console.error('북마크 데이터 파싱 오류:', error);
            }
        });
    });
}

/**
 * 공유 버튼에 이벤트 리스너 추가
 */
function attachShareListeners() {
    document.querySelectorAll('.share-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const card = this.closest('.news-card');
            if (!card) return;
            
            const newsDataStr = card.getAttribute('data-news-data');
            if (!newsDataStr) return;
            
            try {
                const newsItem = JSON.parse(newsDataStr.replace(/&apos;/g, "'"));
                shareNews(newsItem);
            } catch (error) {
                console.error('공유 데이터 파싱 오류:', error);
            }
        });
    });
}

/**
 * 뉴스 이미지 URL 가져오기
 */
function getNewsImage(item) {
    if (item.image_url) {
        return item.image_url;
    }
    
    // 카테고리별 기본 이미지
    const categoryImages = {
        '정치': 'static/images/politics-default.jpg',
        'politics': 'static/images/politics-default.jpg',
        '스포츠': 'static/images/sports-default.jpg',
        'sports': 'static/images/sports-default.jpg',
        '경제': 'static/images/economy-default.jpg',
        'economy': 'static/images/economy-default.jpg',
    };
    
    return categoryImages[item.category || item.main_category] || 'static/images/no-image.png';
}

/**
 * 신문사 로고 가져오기
 */
function getSourceLogo(source) {
    const sourceLogos = {
        '동아일보': 'static/images/donga.png?v=2',
        'donga': 'static/images/donga.png?v=2',
        '조선일보': 'static/images/chosun.png?v=2',
        'chosun': 'static/images/chosun.png?v=2',
        '중앙일보': 'static/images/joongang.png?v=2',
        'joongang': 'static/images/joongang.png?v=2',
    };
    
    return sourceLogos[source] || 'static/images/no-image.png';
}

/**
 * 날짜 포맷팅
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}.${month}.${day}`;
}

/**
 * HTML 이스케이프 (XSS 방지)
 */
function escapeHtml(text) {
    if (!text) return '';
    
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * ===== 북마크 기능 =====
 */

/**
 * 북마크 초기화
 */
function initBookmarks() {
    // LocalStorage에서 북마크 불러오기
    const savedBookmarks = localStorage.getItem('newsBookmarks');
    bookmarks = savedBookmarks ? JSON.parse(savedBookmarks) : [];
    
    // 북마크 카운터 업데이트
    updateBookmarkCount();
    
    // 북마크 페이지 버튼 이벤트
    const bookmarkPageBtn = document.getElementById('bookmark-page-btn');
    if (bookmarkPageBtn) {
        bookmarkPageBtn.addEventListener('click', openBookmarkModal);
    }
    
    // 모달 닫기 버튼
    const closeModalBtn = document.getElementById('close-bookmark-modal');
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeBookmarkModal);
    }
    
    // 모달 배경 클릭 시 닫기
    const modal = document.getElementById('bookmark-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeBookmarkModal();
            }
        });
    }
}

/**
 * 고유 ID 생성 (URL 기반 해시)
 */
function generateNewsId(newsItem) {
    // URL이 없으면 title과 date를 조합하여 ID 생성
    const uniqueString = newsItem.url || `${newsItem.title}_${newsItem.date}`;
    
    // 간단한 해시 함수 사용 (문자열을 숫자 해시로 변환)
    let hash = 0;
    for (let i = 0; i < uniqueString.length; i++) {
        const char = uniqueString.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // 32비트 정수로 변환
    }
    
    // 해시를 16진수 문자열로 변환하고 절대값 사용
    return 'news_' + Math.abs(hash).toString(36);
}

/**
 * 북마크 여부 확인
 */
function checkIfBookmarked(newsId) {
    return bookmarks.some(b => b.id === newsId);
}

/**
 * 북마크 토글 (추가/제거)
 */
function toggleBookmark(newsItem, buttonElement) {
    const newsId = generateNewsId(newsItem);
    const index = bookmarks.findIndex(b => b.id === newsId);
    
    if (index > -1) {
        // 북마크 제거
        bookmarks.splice(index, 1);
        showToast('북마크에서 제거되었습니다');
    } else {
        // 북마크 추가
        const bookmarkData = {
            id: newsId,
            title: newsItem.title,
            url: newsItem.url,
            image: newsItem.image_url || '',
            category: newsItem.category || newsItem.main_category,
            source: currentSource,
            date: newsItem.date,
            bookmarkedAt: Date.now()
        };
        
        bookmarks.unshift(bookmarkData);
        showToast('북마크에 추가되었습니다 ⭐');
        
        // 최대 100개로 제한
        if (bookmarks.length > 100) {
            bookmarks.pop();
        }
    }
    
    // LocalStorage에 저장
    localStorage.setItem('newsBookmarks', JSON.stringify(bookmarks));
    
    // UI 업데이트 - 버튼 요소 직접 업데이트
    if (buttonElement) {
        updateBookmarkButton(buttonElement, newsId);
    }
    updateBookmarkCount();
    
    // 모달이 열려있으면 북마크 그리드 갱신
    const modal = document.getElementById('bookmark-modal');
    if (modal && modal.classList.contains('active')) {
        renderBookmarkGrid();
    }
}

/**
 * 북마크 버튼 UI 업데이트
 */
function updateBookmarkButton(buttonElement, newsId) {
    const isBookmarked = checkIfBookmarked(newsId);
    
    if (isBookmarked) {
        buttonElement.classList.add('bookmarked');
    } else {
        buttonElement.classList.remove('bookmarked');
    }
}

/**
 * 북마크 카운터 업데이트
 */
function updateBookmarkCount() {
    const countEl = document.getElementById('bookmark-count');
    if (countEl) {
        countEl.textContent = bookmarks.length;
        countEl.style.display = bookmarks.length > 0 ? 'block' : 'none';
    }
}

/**
 * 북마크 모달 열기
 */
function openBookmarkModal() {
    const modal = document.getElementById('bookmark-modal');
    if (modal) {
        modal.classList.add('active');
        renderBookmarkGrid();
        document.body.style.overflow = 'hidden';
    }
}

/**
 * 북마크 모달 닫기
 */
function closeBookmarkModal() {
    const modal = document.getElementById('bookmark-modal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

/**
 * 북마크 그리드 렌더링
 */
function renderBookmarkGrid() {
    const gridEl = document.getElementById('bookmark-grid');
    const emptyEl = document.getElementById('bookmark-empty-state');
    
    if (!gridEl || !emptyEl) return;
    
    if (bookmarks.length === 0) {
        emptyEl.style.display = 'flex';
        gridEl.innerHTML = '';
        return;
    }
    
    emptyEl.style.display = 'none';
    
    gridEl.innerHTML = bookmarks.map(item => {
        const categoryClass = getCategoryClass(item.category);
        return `
        <article class="news-card" data-news-id="${item.id}">
            <button class="bookmark-btn bookmarked" 
                    onclick="event.stopPropagation(); removeBookmark('${item.id}')" 
                    aria-label="북마크 제거">
                <svg class="bookmark-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
            </button>
            <div class="news-card-image-wrapper" onclick="window.open('${escapeHtml(item.url)}', '_blank')" style="cursor: pointer;">
                <img src="${item.image || 'static/images/no-image.png'}" 
                     alt="${escapeHtml(item.title)}" 
                     class="news-card-image"
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                     loading="lazy">
                <div class="news-card-no-image" style="display: none;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                    </svg>
                    <span>이미지 준비중</span>
                </div>
            </div>
            <div class="news-card-content" onclick="window.open('${escapeHtml(item.url)}', '_blank')" style="cursor: pointer;">
                <div class="news-card-header">
                    <span class="news-card-category ${categoryClass}">${escapeHtml(item.category)}</span>
                    <span class="news-card-date">${formatDate(item.date)}</span>
                </div>
                <h3 class="news-card-title">${escapeHtml(item.title)}</h3>
            </div>
        </article>
        `;
    }).join('');
}

/**
 * 북마크 제거
 */
function removeBookmark(newsId) {
    const index = bookmarks.findIndex(b => b.id === newsId);
    if (index > -1) {
        bookmarks.splice(index, 1);
        localStorage.setItem('newsBookmarks', JSON.stringify(bookmarks));
        updateBookmarkCount();
        renderBookmarkGrid();
        showToast('북마크에서 제거되었습니다');
        
        // 메인 그리드의 모든 해당 버튼 업데이트
        updateAllBookmarkButtons(newsId);
    }
}

/**
 * 메인 그리드의 모든 북마크 버튼 업데이트
 */
function updateAllBookmarkButtons(newsId) {
    const cards = document.querySelectorAll(`[data-news-id="${newsId}"]`);
    cards.forEach(card => {
        const btn = card.querySelector('.bookmark-btn');
        if (btn) {
            const isBookmarked = checkIfBookmarked(newsId);
            if (isBookmarked) {
                btn.classList.add('bookmarked');
            } else {
                btn.classList.remove('bookmarked');
            }
        }
    });
}

/**
 * 토스트 메시지 표시
 */
function showToast(message) {
    // 기존 토스트 제거
    const existingToast = document.querySelector('.toast-message');
    if (existingToast) {
        existingToast.remove();
    }
    
    // 새 토스트 생성
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // 애니메이션
    setTimeout(() => toast.classList.add('show'), 100);
    
    // 3초 후 제거
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * ===== 공유 기능 =====
 */

/**
 * 뉴스 공유
 */
async function shareNews(newsItem) {
    const shareData = {
        title: newsItem.title,
        text: `${newsItem.title} - Hyeok Crawler`,
        url: newsItem.url
    };
    
    // Web Share API 지원 확인 (모바일 우선)
    if (navigator.share) {
        try {
            await navigator.share(shareData);
            showToast('공유되었습니다! 📤');
        } catch (err) {
            // 사용자가 취소한 경우 무시
            if (err.name !== 'AbortError') {
                console.error('공유 오류:', err);
            }
        }
    } else {
        // Fallback: URL 클립보드 복사
        try {
            await navigator.clipboard.writeText(newsItem.url);
            showToast('링크가 복사되었습니다! 📋');
        } catch (err) {
            console.error('클립보드 복사 오류:', err);
            showToast('링크 복사에 실패했습니다');
        }
    }
}

/**
 * 카테고리명을 CSS 클래스로 변환
 */
function getCategoryClass(category) {
    const categoryMap = {
        '정치': 'politics',
        'politics': 'politics',
        '스포츠': 'sports',
        'sports': 'sports',
        '경제': 'economy',
        'economy': 'economy',
        '사회': 'society',
        'society': 'society',
        '국제': 'international',
        'international': 'international',
        '문화': 'culture',
        'culture': 'culture'
    };
    
    return categoryMap[category] || 'politics';
}

/**
 * 스크롤 애니메이션 (Intersection Observer)
 */
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// 뉴스 카드에 애니메이션 적용
function observeNewsCards() {
    document.querySelectorAll('.news-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
}

// MutationObserver로 동적으로 추가된 카드 감지
const gridObserver = new MutationObserver(function() {
    observeNewsCards();
});

const newsGrid = document.getElementById('news-grid');
if (newsGrid) {
    gridObserver.observe(newsGrid, { childList: true });
}

/**
 * 뉴스 티커 초기화 및 로드 - 트렌드 없이 뉴스만
 */
async function initNewsTicker(date) {
    const categories = ['politics', 'sports', 'economy', 'society', 'international', 'culture'];
    const sources = ['donga', 'chosun', 'joongang'];
    const categoryLabels = {
        politics: '정치',
        sports: '스포츠',
        economy: '경제',
        society: '사회',
        international: '국제',
        culture: '문화'
    };
    
    let allNews = [];
    
    // 모든 카테고리와 소스에서 뉴스 수집
    for (const category of categories) {
        for (const source of sources) {
            try {
                const response = await fetch(`data/${category}/${source}/news_${date}.json`);
                if (response.ok) {
                    const data = await response.json();
                    const newsWithCategory = data.map(item => ({
                        ...item,
                        category: category,
                        categoryLabel: categoryLabels[category],
                        source: source
                    }));
                    allNews = allNews.concat(newsWithCategory);
                }
            } catch (error) {
                console.log(`티커 뉴스 로드 실패: ${category}/${source}`, error);
            }
        }
    }
    
    console.log('티커 뉴스 로드 완료:', allNews.length, '개');
    
    // 뉴스를 랜덤하게 섞기
    allNews = shuffleArray(allNews);
    
    // 티커에 뉴스만 표시
    displayTickerNews(allNews);
}

/**
 * 트렌드 패널 초기화
 */
function initTrendPanel() {
    const trendBtn = document.getElementById('trend-btn');
    const trendPanel = document.getElementById('trend-panel');
    const trendOverlay = document.getElementById('trend-overlay');
    const trendCloseBtn = document.getElementById('trend-close-btn');
    const trendTabs = document.querySelectorAll('.trend-tab');
    
    // 트렌드 버튼 클릭
    trendBtn.addEventListener('click', async function() {
        const dateInput = document.getElementById('date-select');
        const selectedDate = dateInput.value;
        
        await loadTrendPanelData(selectedDate);
        trendPanel.classList.add('active');
        trendOverlay.classList.add('active');
    });
    
    // 닫기 버튼 클릭
    trendCloseBtn.addEventListener('click', function() {
        trendPanel.classList.remove('active');
        trendOverlay.classList.remove('active');
    });
    
    // 오버레이 클릭
    trendOverlay.addEventListener('click', function() {
        trendPanel.classList.remove('active');
        trendOverlay.classList.remove('active');
    });
    
    // 탭 전환 이벤트
    trendTabs.forEach(tab => {
        tab.addEventListener('click', async function() {
            const tabType = this.getAttribute('data-tab');
            
            // 탭 활성화 상태 변경
            trendTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // 콘텐츠 전환
            const trendsContent = document.getElementById('trends-content');
            const statisticsContent = document.getElementById('statistics-content');
            
            if (tabType === 'trends') {
                trendsContent.style.display = 'block';
                statisticsContent.style.display = 'none';
                document.getElementById('trend-panel-title').textContent = '🔥 오늘의 트렌드';
            } else if (tabType === 'statistics') {
                trendsContent.style.display = 'none';
                statisticsContent.style.display = 'block';
                document.getElementById('trend-panel-title').textContent = '📊 통계 대시보드';
                
                // 통계 데이터 로드
                const dateInput = document.getElementById('date-select');
                const selectedDate = dateInput.value;
                await loadStatisticsData(selectedDate);
            }
        });
    });
}

/**
 * 트렌드 패널 데이터 로드
 */
async function loadTrendPanelData(date) {
    try {
        const response = await fetch(`data/trends/trends_${date}.json`);
        if (response.ok) {
            const trendData = await response.json();
            
            // Top 키워드 배지 업데이트
            const trendBadge = document.getElementById('trend-badge');
            if (trendData.daily_top_keywords.length > 0) {
                trendBadge.textContent = trendData.daily_top_keywords[0].word;
                trendBadge.classList.add('visible');
            } else {
                trendBadge.classList.remove('visible');
            }
            
            // 전체 키워드 리스트 표시
            displayTrendKeywords(trendData.daily_top_keywords);
            
            // 카테고리별 키워드 표시
            displayCategoryKeywords(trendData.category_keywords);
        }
    } catch (error) {
        console.log('트렌드 데이터 로드 실패:', error);
        
        // 에러 메시지 표시
        const keywordsList = document.getElementById('trend-keywords-list');
        keywordsList.innerHTML = '<p class="trend-error">트렌드 데이터를 불러올 수 없습니다.</p>';
    }
}

/**
 * 전체 키워드 리스트 표시
 */
function displayTrendKeywords(keywords) {
    const keywordsList = document.getElementById('trend-keywords-list');
    
    if (!keywords || keywords.length === 0) {
        keywordsList.innerHTML = '<p class="trend-empty">키워드가 없습니다.</p>';
        return;
    }
    
    keywordsList.innerHTML = keywords.map((kw, index) => `
        <div class="trend-keyword-item">
            <span class="trend-rank">${index + 1}</span>
            <span class="trend-word">${kw.word}</span>
            <span class="trend-count-badge">${kw.count}회</span>
        </div>
    `).join('');
}

/**
 * 카테고리별 키워드 표시
 */
function displayCategoryKeywords(categoryKeywords) {
    const categoriesDiv = document.getElementById('trend-categories');
    
    const categoryNames = {
        politics: '정치',
        sports: '스포츠',
        economy: '경제',
        society: '사회',
        international: '국제',
        culture: '문화'
    };
    
    categoriesDiv.innerHTML = Object.entries(categoryKeywords).map(([category, keywords]) => {
        const keywordsHTML = keywords.slice(0, 5).map(kw => 
            `<span class="category-keyword">${kw.word} <small>(${kw.count})</small></span>`
        ).join('');
        
        return `
            <div class="trend-category-box">
                <h4 class="category-badge ${category}">${categoryNames[category]}</h4>
                <div class="category-keywords-list">
                    ${keywordsHTML || '<span class="trend-empty">키워드 없음</span>'}
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 트렌드 키워드 로드 (사용 안 함 - 옵션1용)
 */
async function loadTrendKeywords(date) {
    try {
        const response = await fetch(`data/trends/trends_${date}.json`);
        if (response.ok) {
            const trendData = await response.json();
            console.log('트렌드 키워드 로드 완료:', trendData.daily_top_keywords.length, '개');
            return trendData.daily_top_keywords.slice(0, 5); // 상위 5개만
        }
    } catch (error) {
        console.log('트렌드 키워드 로드 실패 (파일 없음):', error);
    }
    return [];
}

/**
 * 배열 섞기 (Fisher-Yates shuffle)
 */
function shuffleArray(array) {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
}

/**
 * 티커에 뉴스 표시 - 트렌드 제거
 */
function displayTickerNews(newsItems) {
    const tickerWrapper = document.getElementById('ticker-wrapper');
    if (!tickerWrapper) {
        console.error('티커 래퍼를 찾을 수 없습니다');
        return;
    }
    
    if (!newsItems || newsItems.length === 0) {
        console.warn('표시할 뉴스가 없습니다');
        return;
    }
    
    tickerWrapper.innerHTML = '';
    
    console.log('티커에 표시할 뉴스:', newsItems.length, '개');
    
    // 뉴스 슬라이드만 추가
    newsItems.forEach((item, index) => {
        const slide = document.createElement('div');
        slide.className = 'swiper-slide';
        
        slide.innerHTML = `
            <div class="ticker-item" data-url="${item.url}">
                <span class="ticker-category ${item.category}">${item.categoryLabel}</span>
                <span class="ticker-title">${item.title}</span>
            </div>
        `;
        
        tickerWrapper.appendChild(slide);
    });
    
    console.log('슬라이드 생성 완료:', tickerWrapper.children.length, '개');
    
    // Swiper 초기화 또는 재초기화
    if (tickerSwiper) {
        tickerSwiper.destroy(true, true);
    }
    
    const totalSlides = tickerWrapper.children.length;
    
    tickerSwiper = new Swiper('.news-ticker-swiper', {
        direction: 'vertical',
        slidesPerView: 1,
        spaceBetween: 0,
        loop: totalSlides >= 3,
        loopedSlides: totalSlides,
        autoplay: {
            delay: 4500,
            disableOnInteraction: false,
        },
        speed: 1200,
        allowTouchMove: true,
    });
    
    console.log('Swiper 초기화 완료');
    
    // 티커 아이템 클릭 이벤트
    document.querySelectorAll('.ticker-item').forEach(item => {
        item.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            if (url) {
                window.open(url, '_blank');
            }
        });
    });
}

/* =============================================================================
   통계 대시보드 함수
============================================================================= */

let categoryPieChart = null;
let sourceBarChart = null;
let weeklyLineChart = null;

/**
 * 통계 데이터 로드 및 차트 렌더링
 */
async function loadStatisticsData(date) {
    try {
        // 카테고리별 및 신문사별 통계 수집
        const dailyStats = await collectDailyStats(date);
        
        // 요약 통계 표시
        document.getElementById('total-articles').textContent = dailyStats.totalArticles;
        
        // 차트 렌더링
        renderCategoryPieChart(dailyStats.categoryData);
        renderSourceBarChart(dailyStats.sourceData);
        
        // 주간 트렌드 데이터 수집 및 렌더링
        const weeklyStats = await collectWeeklyStats(date);
        renderWeeklyLineChart(weeklyStats);
        
    } catch (error) {
        console.error('통계 데이터 로드 실패:', error);
    }
}

/**
 * 일간 통계 데이터 수집
 */
async function collectDailyStats(date) {
    const categories = ['politics', 'sports', 'economy', 'society', 'international', 'culture'];
    const sources = ['donga', 'chosun', 'joongang'];
    
    const categoryData = {};
    const sourceData = {};
    let totalArticles = 0;
    
    // 카테고리별 데이터 수집
    for (const category of categories) {
        let categoryCount = 0;
        
        for (const source of sources) {
            try {
                const response = await fetch(`data/${category}/${source}/news_${date}.json`);
                if (response.ok) {
                    const newsData = await response.json();
                    const articleCount = newsData.length;
                    
                    categoryCount += articleCount;
                    sourceData[source] = (sourceData[source] || 0) + articleCount;
                    totalArticles += articleCount;
                }
                // 404는 정상 - 해당 날짜 데이터가 없는 경우
            } catch (error) {
                // 네트워크 오류만 로깅
            }
        }
        
        if (categoryCount > 0) {
            categoryData[category] = categoryCount;
        }
    }
    
    return {
        totalArticles,
        categoryData,
        sourceData
    };
}

/**
 * 주간 통계 데이터 수집 (선택된 날짜 기준 과거 데이터)
 */
async function collectWeeklyStats(endDate) {
    const labels = [];
    const dateCounts = [];
    
    const end = new Date(endDate);
    
    // 선택된 날짜부터 과거 6일까지 (총 7개 포인트)
    // 단, 미래 날짜는 제외
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    for (let i = 6; i >= 0; i--) {
        const date = new Date(end);
        date.setDate(date.getDate() - i);
        
        // 미래 날짜는 건너뜀
        if (date > today) {
            continue;
        }
        
        const dateStr = date.toISOString().split('T')[0];
        
        // 데이터 수집 (없으면 0으로 처리)
        const dailyStats = await collectDailyStats(dateStr);
        if (dailyStats.totalArticles > 0) {
            labels.push(dateStr.substring(5)); // MM-DD 형식
            dateCounts.push(dailyStats.totalArticles);
        }
    }
    
    return {
        labels: labels,
        data: dateCounts
    };
}

/**
 * 카테고리별 파이 차트 렌더링
 */
function renderCategoryPieChart(categoryData) {
    const categoryNames = {
        politics: '정치',
        sports: '스포츠',
        economy: '경제',
        society: '사회',
        international: '국제',
        culture: '문화'
    };
    
    const labels = Object.keys(categoryData).map(key => categoryNames[key] || key);
    const data = Object.values(categoryData);
    
    const ctx = document.getElementById('category-pie-chart').getContext('2d');
    
    // 기존 차트 파괴
    if (categoryPieChart) {
        categoryPieChart.destroy();
    }
    
    categoryPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',   // 정치
                    'rgba(75, 192, 192, 0.8)',   // 스포츠
                    'rgba(255, 206, 86, 0.8)',   // 경제
                    'rgba(153, 102, 255, 0.8)',  // 사회
                    'rgba(255, 159, 64, 0.8)',   // 국제
                    'rgba(255, 99, 132, 0.8)'    // 문화
                ],
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim(),
                        padding: 15,
                        font: {
                            size: 12,
                            family: "'Noto Sans KR', sans-serif"
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value}개 (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 신문사별 바 차트 렌더링
 */
function renderSourceBarChart(sourceData) {
    const sourceNames = {
        donga: '동아일보',
        chosun: '조선일보',
        joongang: '중앙일보'
    };
    
    const labels = Object.keys(sourceData).map(key => sourceNames[key] || key);
    const data = Object.values(sourceData);
    
    const ctx = document.getElementById('source-bar-chart').getContext('2d');
    
    // 기존 차트 파괴
    if (sourceBarChart) {
        sourceBarChart.destroy();
    }
    
    sourceBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '기사 수',
                data: data,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(75, 192, 192, 0.8)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5,
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim(),
                        font: {
                            family: "'Noto Sans KR', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(128, 128, 128, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim(),
                        font: {
                            family: "'Noto Sans KR', sans-serif"
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y}개`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 주간 트렌드 라인 차트 렌더링
 */
function renderWeeklyLineChart(weeklyStats) {
    const ctx = document.getElementById('weekly-line-chart').getContext('2d');
    
    // 기존 차트 파괴
    if (weeklyLineChart) {
        weeklyLineChart.destroy();
    }
    
    weeklyLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeklyStats.labels,
            datasets: [{
                label: '기사 수',
                data: weeklyStats.data,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 10,
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim(),
                        font: {
                            family: "'Noto Sans KR', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(128, 128, 128, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim(),
                        font: {
                            family: "'Noto Sans KR', sans-serif"
                        }
                    },
                    grid: {
                        color: 'rgba(128, 128, 128, 0.05)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return `${context[0].label}`;
                        },
                        label: function(context) {
                            return `${context.parsed.y}개`;
                        }
                    }
                }
            }
        }
    });
}
