"""Centralized configuration for Google Maps Scraper."""

# XPath selectors for Google Maps place extraction
XPATHS = {
    "name": '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]',
    "address": '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]',
    "website": '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]',
    "phone_number": '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]',
    "reviews_count": '//div[contains(@class, "F7nice")]//span[contains(text(), "(")]',
    "reviews_count_aria": '//div[contains(@class, "F7nice")]//span[@role="img"][@aria-label]',
    "reviews_average": '//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span[@aria-hidden]',
    "info1": '//div[@class="LTs0Rc"][1]',
    "info2": '//div[@class="LTs0Rc"][2]',
    "info3": '//div[@class="LTs0Rc"][3]',
    "opens_at": '//button[contains(@data-item-id, "oh")]//div[contains(@class, "fontBodyMedium")]',
    "opens_at2": '//div[@class="MkV9"]//span[@class="ZDu9vd"]//span[2]',
    "place_type": '//div[@class="LBgpqf"]//button[@class="DkEaL "]',
    "introduction": '//div[@class="WeS02d fontBodyMedium"]//div[@class="PYvSYb "]',
}

# Search input selectors (tried in order; Google Maps changes these periodically)
SEARCH_INPUT_SELECTORS = [
    '#searchboxinput',
    'input[name="q"]',
    'input[aria-label*="Search"]',
    'input[aria-label*="Cerca"]',
    'input[aria-label*="Rechercher"]',
]

# Browser launch arguments
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-blink-features=AutomationControlled',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
]

# Additional browser args for headless mode (stability + anti-detection)
HEADLESS_BROWSER_ARGS = [
    '--disable-gpu',
    '--window-size=1920,1080',
]

# Default browser viewport and locale
DEFAULT_VIEWPORT = {'width': 1920, 'height': 1080}
DEFAULT_LOCALE = 'en-US'

# Timeouts (in milliseconds)
DEFAULT_PAGE_TIMEOUT = 30000
NAVIGATION_TIMEOUT = 60000
PLACE_DETAIL_TIMEOUT = 15000
PLACE_DETAIL_FALLBACK_TIMEOUT = 5000

# Scraping defaults
DEFAULT_SEARCH_QUERY = "turkish stores in toronto Canada"
DEFAULT_TOTAL_RESULTS = 20
MAX_NO_CHANGE_SCROLLS = 8
SCROLL_WAIT_MS = 3000
DETAIL_LOAD_WAIT_SEC = 3

# Google Maps start URL
MAPS_START_URL = "https://www.google.com/maps/@32.9817464,70.1930781,3.67z?"

# User-Agent strings for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
]

# Proxy settings (None = no proxy)
DEFAULT_PROXY = None  # e.g. "http://user:pass@host:port"

# Headless mode (True = no visible browser window)
DEFAULT_HEADLESS = True

# Retry settings
EXTRACT_RETRY_COUNT = 2
EXTRACT_RETRY_DELAY_SEC = 1
NAVIGATION_RETRY_COUNT = 3

# API server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
SCRAPER_TIMEOUT_SEC = 600
MIN_RESULTS_PER_CITY = 15
