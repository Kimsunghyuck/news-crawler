/**
 * Hyeok Crawler 뉴스 포털 - GitHub Pages 정적 버전
 * JSON 파일을 직접 로드하여 표시
 */

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
            this.classList.add('hover');
        });
        
        item.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });
        
        // 카테고리 클릭 - 카테고리 선택
        item.addEventListener('click', function(e) {
            const category = this.dataset.category;
            currentCategory = category;
            
            // 배너도 해당 카테고리로 업데이트
            loadLatestNews(category);
            
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
            
            updateSourceTitle(source);
            
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
        'donga': 'static/images/donga1.png',
        'chosun': 'static/images/chosun.png',
        'joongang': 'static/images/joongang.png'
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
 * 최신 뉴스 로드 (배너용) - 현재 선택된 카테고리의 기사만 표시
 */
async function loadLatestNews(category = currentCategory) {
    try {
        const today = new Date().toISOString().split('T')[0];
        const sources = ['donga', 'chosun', 'joongang'];
        
        let allNews = [];
        
        // 현재 카테고리의 모든 소스에서 뉴스 수집
        for (const source of sources) {
            try {
                const response = await fetch(`data/${category}/${source}/news_${today}.json`);
                if (response.ok) {
                    const data = await response.json();
                    allNews = allNews.concat(data.slice(0, 2)); // 각 소스에서 2개씩
                }
            } catch (e) {
                console.log(`No data for ${category}/${source}`);
            }
        }
        
        // 최신 4개만 선택
        const latestNews = allNews.slice(0, 4);
        
        if (latestNews.length > 0) {
            renderBannerSlides(latestNews);
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
    
    wrapper.innerHTML = newsItems.map(item => {
        const categoryClass = getCategoryClass(item.category || item.main_category);
        return `
        <div class="swiper-slide banner-slide">
            <img src="${getNewsImage(item)}" 
                 alt="${escapeHtml(item.title)}" 
                 class="banner-image"
                 onerror="this.src='static/images/no-image.png'">
            <div class="banner-overlay">
                <span class="banner-category ${categoryClass}">${escapeHtml(item.category || item.main_category)}</span>
                <h2 class="banner-title">${escapeHtml(item.title)}</h2>
                <p class="banner-source">${escapeHtml(item.source)} · ${formatDate(item.date)}</p>
            </div>
        </div>
        `;
    }).join('');
    
    // Swiper 재초기화
    setTimeout(() => {
        initBannerSwiper();
    }, 100);
}

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
            emptyEl.style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading news:', error);
        loadingEl.style.display = 'none';
        gridEl.innerHTML = '';
        emptyEl.style.display = 'block';
    }
}

/**
 * 뉴스 그리드 렌더링
 */
function renderNewsGrid(newsItems) {
    const gridEl = document.getElementById('news-grid');
    
    gridEl.innerHTML = newsItems.map(item => {
        const categoryClass = getCategoryClass(item.category || item.main_category);
        return `
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
        '동아일보': 'static/images/donga1.png',
        'donga': 'static/images/donga1.png',
        '조선일보': 'static/images/chosun.png',
        'chosun': 'static/images/chosun.png',
        '중앙일보': 'static/images/joongang.png',
        'joongang': 'static/images/joongang.png',
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
 * 카테고리명을 CSS 클래스로 변환
 */
function getCategoryClass(category) {
    const categoryMap = {
        '정치': 'politics',
        'politics': 'politics',
        '스포츠': 'sports',
        'sports': 'sports',
        '경제': 'economy',
        'economy': 'economy'
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
