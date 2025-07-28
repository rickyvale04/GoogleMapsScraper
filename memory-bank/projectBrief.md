# Google Maps Scraper - Project Brief

## Overview
A Python-based web scraping tool that extracts business information from Google Maps search results using Playwright automation. The tool systematically searches Google Maps, scrolls through results, and extracts detailed business data into CSV format.

## Core Requirements
- **Primary Goal**: Extract comprehensive business data from Google Maps listings
- **Data Points**: Name, address, website, phone number, reviews (count & average), business type, operating hours, service types (shopping/pickup/delivery), introductory descriptions
- **Output Format**: CSV files with options for appending or overwriting
- **Browser Automation**: Non-headless browser operation for reliable scraping
- **Scalability**: Handle variable result counts (1 to hundreds of listings)

## Key Constraints
- Must handle Google Maps DOM structure and potential changes
- Rate limiting awareness to avoid Google blocking
- Cross-platform compatibility (Windows vs macOS/Linux browser paths)
- Python 3.8-3.9 compatibility (3.10+ may have dependency issues)

## Success Criteria
- Successfully extract all specified data fields from Google Maps listings
- Export clean, structured data to CSV format
- Handle errors gracefully with proper logging
- Maintain reliability across different search queries and result counts
- Support both new file creation and data appending workflows

## Target Use Cases
- Market research for business analysis
- Competitor analysis in specific geographic areas
- Lead generation for sales and marketing
- Business directory creation
- Local business data aggregation

## Project Scope
This is a focused web scraping tool with clear boundaries:
- **In Scope**: Google Maps business data extraction, CSV export, error handling
- **Out of Scope**: Real-time data updates, web interface, database integration, advanced analytics
