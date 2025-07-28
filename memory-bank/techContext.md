# Technical Context - Google Maps Scraper

## Technology Stack

### Core Technologies
- **Python**: 3.8-3.9 (3.10+ compatibility issues with dependencies)
- **Playwright**: 1.44.0 - Browser automation and web scraping
- **Pandas**: 2.2.2 - Data manipulation and CSV export
- **Dataclasses**: Built-in Python feature for structured data models

### Dependencies
```
playwright==1.44.0          # Browser automation
pandas==2.2.2               # Data processing
numpy==1.26.4               # Pandas dependency
openpyxl==3.1.2            # Excel file support
python-dateutil==2.9.0.post0  # Date parsing
pytz==2024.1               # Timezone support
greenlet==3.0.3            # Async support
pyee==11.1.0               # Event handling
typing_extensions==4.12.0  # Type hints
```

## Browser Requirements
- **Primary**: Google Chrome or Chromium browser
- **Cross-platform**: Automatic browser detection (Windows vs macOS/Linux)
- **Mode**: Non-headless operation for reliability

## Development Setup

### Installation Steps
1. Clone repository
2. Install Python dependencies: `pip install -r requirements.txt`
3. Install Playwright browsers: `playwright install`
4. Ready to run with `python main.py`

### Command Line Interface
```bash
python main.py [options]
  -s, --search: Search query for Google Maps
  -t, --total: Number of results to scrape
  -o, --output: Output CSV file path (default: result.csv)
  --append: Append to existing file instead of overwriting
```

## Technical Constraints

### Performance Considerations
- Non-headless browser required for Google Maps interaction
- Rate limiting awareness to avoid blocking
- DOM element waiting and timing considerations
- Memory usage scales with result count

### Platform Differences
- Windows: Explicit Chrome path handling
- macOS/Linux: Automatic browser discovery
- Shell differences handled by argparse

### Google Maps Limitations
- DOM structure can change (XPath brittleness)
- Anti-scraping measures require careful timing
- Result pagination and infinite scroll handling
- Varying data availability across listings

## Data Processing Pipeline
1. **Search Execution**: Navigate to Google Maps and perform search
2. **Result Discovery**: Scroll and collect all available listing links
3. **Data Extraction**: Click each listing and extract business details
4. **Data Cleaning**: Parse and normalize extracted text
5. **Export**: Convert to DataFrame and save as CSV

## Error Handling Strategy
- Comprehensive logging at INFO and WARNING levels
- Graceful degradation for missing data fields
- Exception handling for network and parsing errors
- Progress tracking with detailed feedback
