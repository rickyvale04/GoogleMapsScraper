import logging
import glob as globmod
from typing import List, Optional
from playwright.sync_api import sync_playwright, Page
from dataclasses import dataclass, asdict
import pandas as pd
import platform
import time
import os
import random

from config import (
    XPATHS, BROWSER_ARGS, HEADLESS_BROWSER_ARGS,
    DEFAULT_VIEWPORT, DEFAULT_LOCALE,
    DEFAULT_PAGE_TIMEOUT, NAVIGATION_TIMEOUT, PLACE_DETAIL_TIMEOUT,
    PLACE_DETAIL_FALLBACK_TIMEOUT, MAX_NO_CHANGE_SCROLLS,
    SCROLL_WAIT_MS, DETAIL_LOAD_WAIT_SEC, MAPS_START_URL,
    USER_AGENTS, DEFAULT_PROXY, DEFAULT_HEADLESS,
    EXTRACT_RETRY_COUNT, EXTRACT_RETRY_DELAY_SEC, NAVIGATION_RETRY_COUNT,
)

@dataclass
class Place:
    name: str = ""
    address: str = ""
    website: str = ""
    phone_number: str = ""
    reviews_count: Optional[int] = None
    reviews_average: Optional[float] = None
    store_shopping: str = "No"
    in_store_pickup: str = "No"
    store_delivery: str = "No"
    place_type: str = ""
    opens_at: str = ""
    introduction: str = ""

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

def find_chromium() -> Optional[str]:
    """Find an available Chromium executable from Playwright cache."""
    if platform.system() == "Windows":
        cache_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")
        sub_path = os.path.join("chrome-win", "chrome.exe")
    else:
        cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "ms-playwright")
        sub_path = os.path.join("chrome-linux", "chrome")

    if os.path.isdir(cache_dir):
        pattern = os.path.join(cache_dir, "chromium-*", sub_path)
        matches = sorted(globmod.glob(pattern), reverse=True)
        for path in matches:
            if os.path.isfile(path):
                return path
    return None


def extract_text(page: Page, xpath: str) -> str:
    try:
        if page.locator(xpath).count() > 0:
            return page.locator(xpath).inner_text()
    except Exception as e:
        logging.warning(f"Failed to extract text for xpath {xpath}: {e}")
    return ""

def extract_place(page: Page, listing=None) -> Place:
    """Extract place details from the current page. Retries if name is empty."""
    for attempt in range(1 + EXTRACT_RETRY_COUNT):
        place = _do_extract_place(page)
        if place.name:
            return place
        if attempt < EXTRACT_RETRY_COUNT:
            logging.warning(f"Empty name on attempt {attempt+1}, retrying...")
            time.sleep(EXTRACT_RETRY_DELAY_SEC)
            if listing is not None:
                try:
                    listing.click()
                    page.wait_for_selector(XPATHS["name"], timeout=PLACE_DETAIL_TIMEOUT)
                except Exception:
                    pass
    return place


def _do_extract_place(page: Page) -> Place:
    """Single extraction attempt."""
    place = Place()
    place.name = extract_text(page, XPATHS["name"])
    place.address = extract_text(page, XPATHS["address"])
    place.website = extract_text(page, XPATHS["website"])
    place.phone_number = extract_text(page, XPATHS["phone_number"])
    place.place_type = extract_text(page, XPATHS["place_type"])
    place.introduction = extract_text(page, XPATHS["introduction"]) or "None Found"

    # Reviews Count
    reviews_count_raw = extract_text(page, XPATHS["reviews_count"])
    if reviews_count_raw:
        try:
            temp = reviews_count_raw.replace('\xa0', '').replace('(','').replace(')','').replace(',','')
            place.reviews_count = int(temp)
        except Exception as e:
            logging.warning(f"Failed to parse reviews count: {e}")
    # Reviews Average
    reviews_avg_raw = extract_text(page, XPATHS["reviews_average"])
    if reviews_avg_raw:
        try:
            temp = reviews_avg_raw.replace(' ','').replace(',','.')
            place.reviews_average = float(temp)
        except Exception as e:
            logging.warning(f"Failed to parse reviews average: {e}")
    # Store Info
    for info_xpath in [XPATHS["info1"], XPATHS["info2"], XPATHS["info3"]]:
        info_raw = extract_text(page, info_xpath)
        if info_raw:
            temp = info_raw.split('·')
            if len(temp) > 1:
                check = temp[1].replace("\n", "").lower()
                if 'shop' in check:
                    place.store_shopping = "Yes"
                if 'pickup' in check:
                    place.in_store_pickup = "Yes"
                if 'delivery' in check:
                    place.store_delivery = "Yes"
    # Opens At
    opens_at_raw = extract_text(page, XPATHS["opens_at"])
    if opens_at_raw:
        opens = opens_at_raw.split('⋅')
        if len(opens) > 1:
            place.opens_at = opens[1].replace("\u202f","")
        else:
            place.opens_at = opens_at_raw.replace("\u202f","")
    else:
        opens_at2_raw = extract_text(page, XPATHS["opens_at2"])
        if opens_at2_raw:
            opens = opens_at2_raw.split('⋅')
            if len(opens) > 1:
                place.opens_at = opens[1].replace("\u202f","")
            else:
                place.opens_at = opens_at2_raw.replace("\u202f","")
    return place

def scrape_places(
    search_for: str,
    total: int,
    headless: bool = DEFAULT_HEADLESS,
    proxy: Optional[str] = DEFAULT_PROXY,
) -> List[Place]:
    setup_logging()
    places: List[Place] = []
    seen: set = set()  # (name, address) deduplication

    with sync_playwright() as p:
        browser_args = list(BROWSER_ARGS)
        if headless:
            browser_args.extend(HEADLESS_BROWSER_ARGS)

        launch_kwargs = {
            "headless": headless,
            "args": browser_args,
        }

        # Auto-detect Chromium binary for cross-version compatibility
        chromium_path = find_chromium()
        if chromium_path:
            launch_kwargs["executable_path"] = chromium_path
            logging.info(f"Using Chromium: {chromium_path}")

        if proxy:
            launch_kwargs["proxy"] = {"server": proxy}

        browser = p.chromium.launch(**launch_kwargs)

        user_agent = random.choice(USER_AGENTS)
        context = browser.new_context(
            user_agent=user_agent,
            viewport=DEFAULT_VIEWPORT,
            locale=DEFAULT_LOCALE,
        )
        page = context.new_page()
        page.set_default_timeout(DEFAULT_PAGE_TIMEOUT)

        try:
            # Navigate and search with retry
            for nav_attempt in range(NAVIGATION_RETRY_COUNT):
                try:
                    page.goto(MAPS_START_URL, timeout=NAVIGATION_TIMEOUT)
                    page.wait_for_load_state("domcontentloaded")
                    page.locator('//input[@id="searchboxinput"]').fill(search_for)
                    page.keyboard.press("Enter")
                    page.wait_for_selector('//a[contains(@href, "https://www.google.com/maps/place")]')
                    page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')
                    break
                except Exception as e:
                    if nav_attempt < NAVIGATION_RETRY_COUNT - 1:
                        logging.warning(f"Navigation attempt {nav_attempt+1} failed: {e}, retrying...")
                        time.sleep(2)
                    else:
                        raise

            previously_counted = 0
            no_change_count = 0

            # Try to get at least the minimum requested results, but aim higher for buffer
            target_results = max(total * 2, 100)

            while True:
                page.mouse.wheel(0, 15000)
                page.wait_for_timeout(SCROLL_WAIT_MS)
                page.wait_for_selector('//a[contains(@href, "https://www.google.com/maps/place")]')
                found = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                logging.info(f"Currently Found: {found} (Target: {target_results})")

                if found >= target_results:
                    logging.info(f"Reached target of {target_results} results")
                    break

                if found == previously_counted:
                    no_change_count += 1
                    logging.info(f"No new results found, attempt {no_change_count}/{MAX_NO_CHANGE_SCROLLS}")
                    if no_change_count >= MAX_NO_CHANGE_SCROLLS:
                        logging.info("Reached maximum attempts with no new results")
                        break
                    page.mouse.wheel(0, 20000)
                    page.wait_for_timeout(2000)
                    page.mouse.wheel(0, -5000)
                    page.wait_for_timeout(1000)
                else:
                    no_change_count = 0

                previously_counted = found

                random_scroll = random.randint(8000, 12000)
                page.mouse.wheel(0, random_scroll)
                page.wait_for_timeout(random.randint(1000, 2000))

            all_listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
            listings = [listing.locator("xpath=..") for listing in all_listings]

            logging.info(f"Total Found: {len(listings)}, Processing all to ensure minimum {total} valid results")

            for idx, listing in enumerate(listings):
                try:
                    page.wait_for_timeout(500)
                    listing.click()

                    try:
                        page.wait_for_selector(XPATHS["name"], timeout=PLACE_DETAIL_TIMEOUT)
                    except:
                        try:
                            page.wait_for_selector('//h1[contains(@class, "DUwDvf")]', timeout=PLACE_DETAIL_FALLBACK_TIMEOUT)
                        except:
                            logging.warning(f"Could not load details for listing {idx+1}, skipping")
                            continue

                    page.wait_for_load_state("domcontentloaded")
                    place = extract_place(page, listing=listing)
                    if place.name:
                        dedup_key = (place.name.strip().lower(), place.address.strip().lower())
                        if dedup_key in seen:
                            logging.info(f"Skipping duplicate: {place.name}")
                        else:
                            seen.add(dedup_key)
                            places.append(place)
                            logging.info(f"Extracted place {len(places)}: {place.name}")
                            if len(places) >= total * 1.5:
                                logging.info(f"Exceeded target significantly: {len(places)} >= {total * 1.5}")
                                break
                    else:
                        logging.warning(f"No name found for listing {idx+1}, skipping.")
                except Exception as e:
                    logging.warning(f"Failed to extract listing {idx+1}: {e}")
                    page.wait_for_timeout(1000)
                    continue

        finally:
            context.close()
            browser.close()

    logging.info(f"Final result: {len(places)} places extracted")
    return places

def save_places_to_csv(places: List[Place], output_path: str = "result.csv", append: bool = False):
    df = pd.DataFrame([asdict(place) for place in places])
    if not df.empty:
        for column in df.columns:
            if df[column].nunique() == 1:
                df.drop(column, axis=1, inplace=True)
        file_exists = os.path.isfile(output_path)
        mode = "a" if append else "w"
        header = not (append and file_exists)
        df.to_csv(output_path, index=False, mode=mode, header=header)
        logging.info(f"Saved {len(df)} places to {output_path} (append={append})")
    else:
        logging.warning("No data to save. DataFrame is empty.")
