# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hyeok News Crawler is a multi-source Korean news aggregation system that:
- Crawls 6 categories × 3 newspapers = 90 articles per session, 3 times daily (270 articles/day)
- Analyzes trends using keyword extraction from article titles
- Serves a static website via GitHub Pages with interactive data visualization
- Fully automated through GitHub Actions (no manual intervention required)

**Tech Stack**: Python 3.11 (BeautifulSoup4, requests), Vanilla JavaScript, GitHub Actions, GitHub Pages

## Core Architecture

### Data Flow Pipeline

```
1. CRAWL (crawler.py)
   → HTTP requests to news websites
   → HTML parsing via BeautifulSoup4 (parser.py - 18 parser functions)
   → Image extraction (Open Graph → Twitter Card → first img tag)
   → Save to data/{category}/{source}/news_{date}_{time}.json

2. ANALYZE (analyzer.py)
   → Load all 3 time periods: 09-20, 15-00, 19-00
   → Extract Korean keywords from titles (regex-based)
   → Remove stopwords, count frequencies
   → Save to docs/data/trends/trends_{date}.json

3. DEPLOY (GitHub Actions)
   → Copy data/* to docs/data/*
   → Commit and push to main branch
   → GitHub Pages auto-deploys from /docs folder

4. DISPLAY (docs/index.html + main.js)
   → Fetch JSON files via browser
   → Home: 1 article per category/source (latest time period)
   → Category pages: All 3 time periods merged, URL-based deduplication
   → Trend panel: Top 10 keywords + category breakdown
   → Statistics: Chart.js visualizations
```

### Critical Technical Decisions

**1. Timestamped File System (v7.0 change)**
- Files named: `news_2025-12-09_09-20.json` (date + time)
- 3 crawl times: 09:20, 15:00, 19:00 KST
- Frontend loads all 3 files and deduplicates by URL

**2. Korean Standard Time (KST)**
- All datetime operations use `KST = timezone(timedelta(hours=9))`
- Functions: `get_kst_now()` in crawler.py, parser.py, analyzer.py, report_generator.py
- GitHub Actions cron uses UTC (subtract 9 hours)

**3. Deduplication Strategy**
- JavaScript: `removeDuplicateNews()` uses URL as unique key (Map)
- Python: No deduplication during crawl (preserves all data)
- Applied in: category pages, news ticker, statistics aggregation

**4. Configuration as Code**
- `config.py` is the single source of truth (SSOT)
- Maps Korean → English: `CATEGORY_EN_MAP`, `SOURCE_EN_MAP`
- Defines 18 parser functions: `NEWS_SOURCES` dictionary
- Template strings: `NEWS_JSON_TEMPLATE`, `REPORT_TEMPLATE`

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run crawler (creates 90 JSON files in data/)
python crawler.py

# Generate trend analysis (creates docs/data/trends/trends_{date}.json)
python analyzer.py

# Generate markdown reports (creates reports/combined/report_{date}.md)
python report_generator.py

# Test website locally
cd docs
python -m http.server 8000
# Visit: http://localhost:8000
```

### Testing
```bash
# No formal test suite yet
# Manual testing: Run crawler, check data/ folder for JSON files
# Check logs: logs/crawler.log

# GitHub Actions E2E tests (Playwright)
# Runs automatically on push to main
# Tests: page load, navigation, date picker, JavaScript errors
```

### Git Workflow
```bash
# After code changes
git add <files>
git commit -m "descriptive message

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
git push

# If remote has new commits (common during automated crawls)
git pull --rebase
git push
```

## GitHub Actions Workflows

### daily-crawl.yml (Production)
- **Schedule**: 3x daily (09:20, 15:00, 19:00 KST via cron)
- **Steps**:
  1. Checkout code
  2. Install Python dependencies
  3. Run crawler.py → analyzer.py
  4. Copy data/ to docs/data/
  5. Auto-commit and push
- **Permissions**: Requires "Read and write permissions" in repo settings

### test-website.yml (CI)
- **Trigger**: Push to main, changes in docs/** or workflow file
- **Tests**:
  - HTML structure validation (BeautifulSoup4)
  - JavaScript function checks (8 required functions)
  - Playwright E2E tests (navigation, date picker, JS errors)
  - HTTP server endpoints
  - Broken link detection
- **Note**: Tests expect home dashboard visible on load (not news-section)

### manual-crawl.yml
- **Trigger**: Manual dispatch button in GitHub Actions tab
- Same steps as daily-crawl.yml but on-demand

## File Structure & Responsibilities

```
crawler.py          # HTTP fetching, image extraction, JSON saving
parser.py           # 18 parser functions (donga/chosun/joongang × 6 categories)
                    # get_crawl_time_str() - returns "HH-MM" format
analyzer.py         # Keyword extraction, trend analysis
                    # analyze_daily_keywords() - aggregates all categories
                    # analyze_category_keywords() - per-category trends
report_generator.py # Markdown report generation (source + combined)
config.py           # SSOT: URLs, file paths, retry settings, mappings

docs/index.html     # Main page structure
docs/static/js/main.js  # Frontend logic
  - loadHomeDashboard()     # Skeleton UI → data loading
  - tryLoadNewsData()       # Fetches latest crawl time file
  - loadNews()              # Loads all 3 time periods for category view
  - initNewsTicker()        # Swiper.js vertical slider
  - removeDuplicateNews()   # URL-based deduplication
  - displayTrendKeywords()  # Top 10 keywords (sliced from 20)

docs/static/css/style.css
  - Skeleton loading UI (shimmer animation)
  - Dark mode via CSS variables
  - Category badges (6 colors)
```

## Adding New Features

### Add a New News Source
1. Update `config.py`:
   ```python
   NEWS_SOURCES = {
       '카테고리': [
           {
               'name': '소스명',
               'url': 'https://...',
               'parser': 'source_category',  # Function name
               'max_articles': 5
           }
       ]
   }
   SOURCE_EN_MAP['소스명'] = 'source_slug'
   ```
2. Add parser function to `parser.py`:
   ```python
   def parse_source_category(html_content: str, max_articles: int = 5) -> List[Dict]:
       # Use BeautifulSoup4 to extract title, url, date
       # Return list of dicts with keys: title, url, date
   ```
3. Test locally: `python crawler.py`

### Modify Crawl Schedule
- Edit `.github/workflows/daily-crawl.yml`
- Cron format (UTC): `'0 6 * * *'` = 15:00 KST
- Remember: UTC = KST - 9 hours

### Change Trend Analysis Parameters
- `analyzer.py`:
  - `STOPWORDS`: Add/remove Korean words to filter
  - `top_n` parameter in `analyze_daily_keywords()`: Currently 20
  - `extract_korean_nouns()`: Adjust min_length/max_length for keyword size

## Known Patterns & Conventions

### Error Handling
- Crawlers retry 3 times with 5-second delay (`MAX_RETRIES`, `RETRY_DELAY`)
- Image extraction failures are logged but don't stop crawling
- Missing JSON files return empty arrays (frontend handles gracefully)

### Performance Optimizations
- Skeleton UI displays immediately (< 100ms perceived load time)
- JavaScript uses `Promise.all()` for parallel fetch requests
- GitHub Actions caches pip dependencies (`cache: 'pip'`)

### Data Integrity
- `scraped_at` field stores ISO 8601 timestamp with timezone
- URL is the primary key for deduplication
- No database - all data in JSON files (static site requirement)

### Debugging Tips
- Check `logs/crawler.log` for scraping errors
- Use browser DevTools → Network tab to inspect JSON fetch failures
- Verify file naming: Must be `news_YYYY-MM-DD_HH-MM.json` format
- Check GitHub Actions → Jobs → Step logs for deployment issues

## Important Notes

- **Never commit secrets**: No API keys in code (project is fully client-side)
- **Timezone consistency**: Always use `get_kst_now()`, never `datetime.now()`
- **File naming**: Time format is `HH-MM` (hyphen), not `HH:MM` (filesystem-safe)
- **GitHub Pages**: Changes take 1-2 minutes to deploy after push
- **Deduplication**: Applied in frontend (main.js), NOT during crawling
- **E2E tests**: Expect home dashboard visible, not news-section (check line 332 in test-website.yml)
