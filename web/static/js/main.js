/**
 * Hyeok Crawler 뉴스 포털 - 메인 JavaScript
 * 배너 슬라이더, 카테고리/소스 선택, 뉴스 로딩 등의 기능
 */

// API Base URL
const API_BASE_URL = '';

// 현재 선택된 카테고리와 소스
let currentCategory = 'politics';
let currentSource = 'donga';

// Swiper 인스턴스
let bannerSwiper = null;

/**
 * 페이지 로드 시 초기화
 */
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    loadLatestNews();
    
    // 기본 카테고리와 소스로 뉴스 로드
    const today = new Date().toISOString().split('T')[0];
    loadNews(currentCategory, currentSource, today);
});

/**
 * 배너 Swiper 초기화
 */
function initBannerSwiper() {
    // 기존 Swiper 인스턴스 제거
    if (bannerSwiper) {
        bannerSwiper.destroy(true, true);
    }
    
    bannerSwiper = new Swiper('.banner-swiper', {
        loop: true,
        slidesPerView: 1,
        spaceBetween: 0,
        speed: 800,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
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
            // 호버 중인 카테고리에 hover 클래스 추가
            this.classList.add('hover');
        });
        
        item.addEventListener('mouseleave', function() {
            // 호버 클래스 제거
            this.classList.remove('hover');
        });
        
        // 카테고리 클릭 - 카테고리 선택
        item.addEventListener('click', function(e) {
            const category = this.dataset.category;
            
            currentCategory = category;
            
            // 선택된 날짜로 뉴스 로드
            const selectedDate = document.getElementById('date-select').value;
            loadNews(category, currentSource, selectedDate);
        });
    });
    
    // 드롭다운 영역 호버 시에도 카테고리 호버 상태 유지
    const sharedDropdown = document.querySelector('.shared-dropdown');
    if (sharedDropdown) {
        sharedDropdown.addEventListener('mouseenter', function() {
            // 마지막으로 호버된 카테고리 유지
            if (hoveredCategory) {
                const categoryItem = document.querySelector(`.category-item[data-category="${hoveredCategory}"]`);
                if (categoryItem) {
                    categoryItem.classList.add('hover');
                }
            }
        });
        
        sharedDropdown.addEventListener('mouseleave', function() {
            // 모든 hover 클래스 제거
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
            
            // 현재 호버된 카테고리가 있으면 그것을 사용, 없으면 현재 선택된 카테고리 사용
            const targetCategory = hoveredCategory || currentCategory;
            
            // 모든 소스에서 active 제거
            document.querySelectorAll('.source-item').forEach(src => {
                src.classList.remove('active');
            });
            
            // 현재 소스에 active 추가
            this.classList.add('active');
            
            currentCategory = targetCategory;
            currentSource = source;
            
            // 신문사 제목과 로고 업데이트
            updateSourceTitle(source);
            
            // 선택된 날짜로 뉴스 로드
            const selectedDate = document.getElementById('date-select').value;
            loadNews(targetCategory, source, selectedDate);
        });
    });
}

/**
 * 신문사 제목과 로고 업데이트
 */
function updateSourceTitle(source) {
    const sourceNames = {
        'donga': '동아일보',
        'chosun': '조선일보',
        'joongang': '중앙일보'
    };
    
    const sourceLogos = {
        'donga': `${API_BASE_URL}/static/images/donga1.png`,
        'chosun': `${API_BASE_URL}/static/images/chosun.png`,
        'joongang': `${API_BASE_URL}/static/images/joongang.png`
    };
    
    const sourceNameElement = document.getElementById('source-name');
    const sourceLogoElement = document.getElementById('source-logo');
    
    if (sourceNameElement && sourceNames[source]) {
        sourceNameElement.textContent = sourceNames[source];
    }
    
    if (sourceLogoElement && sourceLogos[source]) {
        sourceLogoElement.src = sourceLogos[source];
        sourceLogoElement.alt = sourceNames[source];
    }
}

/**
 * 최신 뉴스 로드 (배너용)
 */
async function loadLatestNews() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/latest?limit=4`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            renderBannerSlides(result.data);
        }
    } catch (error) {
        console.error('Error loading latest news:', error);
    }
}

/**
 * 배너 슬라이드 렌더링
 */
function renderBannerSlides(newsItems) {
    const wrapper = document.getElementById('banner-wrapper');
    
    if (!wrapper) return;
    
    wrapper.innerHTML = newsItems.map(item => `
        <div class="swiper-slide banner-slide">
            <img src="${getNewsImage(item)}" 
                 alt="${escapeHtml(item.title)}" 
                 class="banner-image"
                 onerror="this.src='${API_BASE_URL}/static/images/no-image.png'">
            <div class="banner-overlay">
                <span class="banner-category">${escapeHtml(item.category_ko || item.category)}</span>
                <h2 class="banner-title">${escapeHtml(item.title)}</h2>
                <p class="banner-source">${escapeHtml(item.source_ko || item.source)} · ${formatDate(item.date)}</p>
            </div>
        </div>
    `).join('');
    
    // Swiper 재초기화
    setTimeout(() => {
        initBannerSwiper();
    }, 100);
}

/**
 * 뉴스 데이터 로드
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
        const response = await fetch(`${API_BASE_URL}/api/news/${category}/${source}?date=${date}`);
        const result = await response.json();
        
        loadingEl.style.display = 'none';
        
        if (result.success && result.data && result.data.length > 0) {
            renderNewsGrid(result.data);
            emptyEl.style.display = 'none';
        } else {
            // 데이터가 없는 경우
            gridEl.innerHTML = '';
            emptyEl.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading news:', error);
        loadingEl.style.display = 'none';
        gridEl.innerHTML = '';
        errorEl.style.display = 'block';
    }
}

/**
 * 뉴스 그리드 렌더링
 */
function renderNewsGrid(newsItems) {
    const gridEl = document.getElementById('news-grid');
    
    gridEl.innerHTML = newsItems.map(item => `
        <article class="news-card" onclick="window.open('${escapeHtml(item.url)}', '_blank')">
            <div class="news-card-image-wrapper">
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
            <div class="news-card-content">
                <div class="news-card-header">
                    <span class="news-card-category">${escapeHtml(item.category || item.main_category)}</span>
                    <span class="news-card-date">${formatDate(item.date)}</span>
                </div>
                <h3 class="news-card-title">${escapeHtml(item.title)}</h3>
                <div class="news-card-source">
                    <img src="${getSourceLogo(item.source)}" alt="${escapeHtml(item.source)}">
                    <span>${escapeHtml(item.source)}</span>
                </div>
            </div>
        </article>
    `).join('');
}

/**
 * 뉴스 이미지 URL 가져오기 (향후 확장용)
 */
function getNewsImage(item) {
    // 현재는 기본 이미지 사용, 향후 크롤링 시 이미지 URL 추가 가능
    if (item.image_url) {
        return item.image_url;
    }
    
    // 카테고리별 기본 이미지
    const categoryImages = {
        '정치': `${API_BASE_URL}/static/images/politics-default.jpg`,
        'politics': `${API_BASE_URL}/static/images/politics-default.jpg`,
        '스포츠': `${API_BASE_URL}/static/images/sports-default.jpg`,
        'sports': `${API_BASE_URL}/static/images/sports-default.jpg`,
        '경제': `${API_BASE_URL}/static/images/economy-default.jpg`,
        'economy': `${API_BASE_URL}/static/images/economy-default.jpg`,
    };
    
    return categoryImages[item.category || item.main_category] || `${API_BASE_URL}/static/images/no-image.png`;
}

/**
 * 신문사 로고 가져오기
 */
function getSourceLogo(source) {
    const sourceLogos = {
        '동아일보': `${API_BASE_URL}/static/images/donga1.png`,
        'donga': `${API_BASE_URL}/static/images/donga1.png`,
        '조선일보': `${API_BASE_URL}/static/images/chosun.png`,
        'chosun': `${API_BASE_URL}/static/images/chosun.png`,
        '중앙일보': `${API_BASE_URL}/static/images/joongang.png`,
        'joongang': `${API_BASE_URL}/static/images/joongang.png`,
    };
    
    return sourceLogos[source] || `${API_BASE_URL}/static/images/no-image.png`;
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
