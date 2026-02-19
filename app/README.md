# Google Maps Scraper

![Interface](https://img.shields.io/badge/Interface-Web%20Based-brightgreen)
![API](https://img.shields.io/badge/API-REST-blue)
![Browser](https://img.shields.io/badge/Browser-Playwright-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

A web scraping tool that extracts business data from Google Maps. It provides a modern web interface, a command-line interface, and a REST API. Built with Playwright and Flask.

## What It Does

Google Maps Scraper searches Google Maps for businesses matching your query and extracts structured data for each result, including name, address, phone number, website, business type, review count, and opening hours. It runs a headless Chromium browser behind the scenes, scrolls through Google Maps listings, visits each place's detail page, and exports everything to CSV. You can use it through a point-and-click web interface, the command line, or the REST API.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/rickyvale04/GoogleMapsScraper.git
   cd GoogleMapsScraper
   ```

2. **Double-click the start script**
   - **macOS / Linux:** `start.command`
   - **Windows:** `startWindows.bat`

   The script automatically installs Python dependencies, downloads Chromium, and starts the server.

3. **Open the web interface**

   Your browser opens to `http://localhost:5001`. Enter a search query, choose your cities, and click **Start Search**.

> If you prefer manual setup, see [Manual Installation](#manual-installation) below.

## Web Interface Fields

| Field | Description | Example |
|---|---|---|
| **Search query** | What type of business to find | `sushi restaurants`, `pharmacies`, `travel agencies` |
| **Target cities** | Comma-separated list of cities to search in | `Milan, Rome, Naples` |
| **Additional filters** | Optional keywords appended to the query | `downtown area`, `open on Sunday` |
| **Minimum number of results** | How many results to collect per city (1--200) | `20` |

## Expected Search Times

Scraping speed depends on network conditions and the number of results requested. As a rough guide:

- **20 results in 1 city** -- 2 to 5 minutes
- **20 results in 3 cities** -- 5 to 15 minutes
- **100 results in 1 city** -- 10 to 25 minutes

The web interface shows live progress while the search runs.

## Data Extracted

For each business the scraper collects:

| Field | Description |
|---|---|
| Name | Business name |
| Address | Full street address |
| Phone | Phone number |
| Website | Website URL |
| Type | Business category (e.g. "Restaurant", "Pharmacy") |
| Reviews | Number of reviews |
| Hours | Opening hours summary |

Results are exported as a UTF-8 CSV file.

## CLI Usage

Run the scraper directly from the terminal:

```bash
# Basic search (headless by default)
python3 main.py -s "sushi restaurants Toronto" -t 20 -o results.csv

# Show the browser window for debugging
python3 main.py -s "sushi restaurants Toronto" -t 20 --visible

# Append to an existing CSV instead of overwriting
python3 main.py -s "pharmacies Montreal" -t 10 -o results.csv --append

# Use a proxy
python3 main.py -s "hotels Vancouver" -t 15 --proxy http://user:pass@host:port
```

### CLI Flags

| Flag | Description | Default |
|---|---|---|
| `-s`, `--search` | Search query | `"turkish stores in toronto Canada"` |
| `-t`, `--total` | Minimum number of results | `20` |
| `-o`, `--output` | Output CSV file path | `result.csv` |
| `--append` | Append results instead of overwriting | off |
| `--headless` | Run browser without a visible window | on |
| `--no-headless`, `--visible` | Show the browser window (useful for debugging) | off |
| `--proxy` | Proxy server URL | none |

## REST API

Start the server with `python3 api_server.py`, then use the endpoints below.

### Start a search

```bash
curl -X POST http://localhost:5001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "sushi restaurants", "maxResults": 20, "cities": "Toronto, Vancouver"}'
```

**Request body:**

| Parameter | Type | Description |
|---|---|---|
| `query` | string | Search query (required) |
| `maxResults` | integer | Minimum results to collect |
| `filters` | string | Additional search filters |
| `cities` | string | Comma-separated city names |

**Response:**
```json
{"search_id": "abc123", "status": "started"}
```

### Check search status

```bash
curl http://localhost:5001/api/search/{search_id}/status
```

Returns `status` (`running`, `completed`, `error`, `timeout`), `elapsed_time`, `current_city`, and `progress`.

### Get results

```bash
curl http://localhost:5001/api/search/{search_id}/results
```

Returns `results` (array of business objects) and `query`.

### Other endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Web interface |
| `GET` | `/health` | Health check |

## Configuration

Edit `config.py` to change:

- **Server port** (`SERVER_PORT`, default `5001`)
- **XPath selectors** (`XPATHS`) -- update these if Google Maps changes its markup
- **Timeouts** (`DEFAULT_PAGE_TIMEOUT`, `NAVIGATION_TIMEOUT`, etc.)
- **User-Agent rotation** (`USER_AGENTS`)
- **Proxy** (`DEFAULT_PROXY`)
- **Headless mode** (`DEFAULT_HEADLESS`)

## Manual Installation

If you prefer not to use the start scripts:

```bash
git clone https://github.com/rickyvale04/GoogleMapsScraper.git
cd GoogleMapsScraper
pip3 install -r requirements.txt
python3 -m playwright install chromium
python3 api_server.py
```

Then open `http://localhost:5001` in your browser.

## Troubleshooting

### Python not found

The start scripts look for `python3` first, then `python`. If neither is found:

- **macOS:** `brew install python3`
- **Ubuntu/Debian:** `sudo apt install python3 python3-pip python3-venv`
- **Windows:** Download from <https://www.python.org/downloads/> and make sure to check **"Add Python to PATH"** during installation.

### Port 5001 is already in use

On macOS, **AirPlay Receiver** listens on port 5001 by default. To free it:

1. Open **System Settings > General > AirDrop & Handoff**
2. Turn off **AirPlay Receiver**

Alternatively, change `SERVER_PORT` in `config.py` to a different port.

### Chromium fails to install

If `playwright install chromium` fails:

- Make sure you have a working internet connection.
- On Linux, install the required system libraries: `sudo npx playwright install-deps chromium` or check the [Playwright docs](https://playwright.dev/python/docs/intro).
- On corporate networks, configure your proxy in `config.py` or pass `--proxy` on the CLI.

### 0 results returned

- Google Maps may show different results depending on your locale and IP address. Try a more specific query (e.g. add a city name).
- Google occasionally changes its page structure. If scraping breaks across all queries, the XPath selectors in `config.py` may need updating.
- Try running with `--visible` to see what the browser is doing.

### Search is very slow

- Each result requires loading a detail page, so large result counts take longer.
- If you are behind a slow proxy, try without one.
- Check your internet connection speed.

## Project Structure

```
GoogleMapsScraper/
├── main.py                # CLI entry point
├── api_server.py          # Server entry point
├── config.py              # Centralized configuration
├── requirements.txt       # Python dependencies
├── start.command           # macOS/Linux start script (double-click)
├── startWindows.bat       # Windows start script (double-click)
├── scraper/
│   ├── __init__.py
│   └── core.py            # Scraping logic (Place, extract, scrape)
├── api/
│   ├── __init__.py
│   └── server.py          # Flask REST API
├── static/
│   └── web-interface.html # Web interface
├── tests/
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_extract.py
│   ├── test_scrape.py
│   └── test_api.py
└── docs/
    └── GUIDA_UTENTE.md    # Guida utente in italiano
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Legal Notice

This tool is intended for educational and research purposes. Make sure to:

- Respect Google Maps Terms of Service
- Avoid overloading servers with excessive requests
- Handle collected data in compliance with applicable privacy laws

## License

This project is released under the MIT license. See the `LICENSE` file for details.

## Support

- Open an [Issue](https://github.com/rickyvale04/GoogleMapsScraper/issues) for bug reports or questions
- Contact on GitHub: [@rickyvale04](https://github.com/rickyvale04)

---

## Italiano

La documentazione completa in italiano e disponibile in [docs/GUIDA_UTENTE.md](docs/GUIDA_UTENTE.md).
