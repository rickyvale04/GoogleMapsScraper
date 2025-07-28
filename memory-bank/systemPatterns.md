# System Patterns - Google Maps Scraper

## Architecture Overview

### Core Components
```
main.py
├── Place (dataclass) - Business data model
├── extract_text() - XPath-based text extraction
├── extract_place() - Complete business data extraction
├── scrape_places() - Main scraping orchestration
└── save_places_to_csv() - Data export functionality
```

## Design Patterns

### Data Model Pattern
- **Place Dataclass**: Structured representation of business information
- **Optional Fields**: Handles missing data with Optional[int] and Optional[float]
- **Default Values**: Sensible defaults for missing information
- **Asdict Conversion**: Seamless pandas DataFrame integration

### XPath Strategy Pattern
Multiple XPath selectors per data field to handle DOM variations:
```python
# Primary and fallback selectors
opens_at_xpath = '//button[contains(@data-item-id, "oh")]//div[contains(@class, "fontBodyMedium")]'
opens_at_xpath2 = '//div[@class="MkV9"]//span[@class="ZDu9vd"]//span[2]'
```

### Error Handling Pattern
- **Graceful Degradation**: Missing data doesn't break extraction
- **Comprehensive Logging**: Warning-level logs for debugging
- **Exception Isolation**: Individual field extraction failures don't stop process

### Browser Automation Pattern
- **Page Object Model**: Single page instance for all operations
- **Wait Strategies**: Explicit waits for dynamic content loading
- **Scroll-to-Load**: Handle infinite scroll pagination
- **Element Counting**: Progress tracking through DOM element counts

## Critical Implementation Paths

### Search and Navigation Flow
1. Navigate to Google Maps base URL
2. Fill search input with query
3. Submit search and wait for results
4. Hover over first result to initialize list

### Result Collection Flow
1. Infinite scroll until target count or end reached
2. Collect all listing element references
3. Limit to requested total count
4. Convert to parent elements for clicking

### Data Extraction Flow
1. Click individual listing
2. Wait for detail page to load
3. Extract all available data fields
4. Handle missing or malformed data
5. Return structured Place object

### Export Flow
1. Convert Place objects to DataFrame
2. Remove columns with single unique value (data cleaning)
3. Handle file existence for append mode
4. Export with appropriate headers

## Component Relationships

### Data Flow
```
Search Query → Google Maps → Listing Elements → Individual Business Pages → Place Objects → CSV Export
```

### Error Recovery
- Network timeouts: Continue with remaining listings
- Missing elements: Log warning and use empty defaults
- Parsing errors: Skip problematic data points
- Browser crashes: Handled by context manager cleanup

## Key Technical Decisions

### Browser Strategy
- **Non-headless**: Required for Google Maps interaction reliability
- **Chromium**: Cross-platform compatibility with explicit Windows path handling
- **Single Page**: Reuse page instance for performance

### Data Extraction Strategy
- **XPath Selectors**: Direct DOM targeting for reliability
- **Multiple Fallbacks**: Handle Google Maps layout variations
- **Text Processing**: Normalize data formats (reviews, ratings, hours)

### Performance Optimizations
- **Element Counting**: Efficient progress tracking
- **Batch Processing**: Process all found listings before extraction
- **Timing Controls**: Strategic waits to balance speed and reliability
