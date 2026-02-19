import argparse
from scraper.core import scrape_places, save_places_to_csv
from config import DEFAULT_SEARCH_QUERY, DEFAULT_TOTAL_RESULTS, DEFAULT_HEADLESS, DEFAULT_PROXY


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str, help="Search query for Google Maps")
    parser.add_argument("-t", "--total", type=int, help="Minimum number of results to scrape")
    parser.add_argument("-o", "--output", type=str, default="result.csv", help="Output CSV file path")
    parser.add_argument("--append", action="store_true", help="Append results to the output file instead of overwriting")
    parser.add_argument("--headless", action="store_true", dest="headless", default=DEFAULT_HEADLESS,
                        help="Run browser in headless mode (no visible window)")
    parser.add_argument("--no-headless", "--visible", action="store_false", dest="headless",
                        help="Show browser window (visible mode, useful for debug)")
    parser.add_argument("--proxy", type=str, default=DEFAULT_PROXY,
                        help="Proxy server URL (e.g. http://user:pass@host:port)")
    args = parser.parse_args()
    search_for = args.search or DEFAULT_SEARCH_QUERY
    total = args.total or DEFAULT_TOTAL_RESULTS
    output_path = args.output
    append = args.append
    places = scrape_places(search_for, total, headless=args.headless, proxy=args.proxy)
    save_places_to_csv(places, output_path, append=append)


if __name__ == "__main__":
    main()
