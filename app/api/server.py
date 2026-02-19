#!/usr/bin/env python3
"""
API Server for Google Maps Scraper.
Uses direct Python imports instead of subprocess calls.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dataclasses import asdict
import os
import threading
import time
from datetime import datetime

from scraper.core import scrape_places, Place
from config import SERVER_HOST, SERVER_PORT, MIN_RESULTS_PER_CITY

app = Flask(__name__)
CORS(app)

# Store for active search results
active_searches = {}

# Path to the static directory (relative to project root)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')


@app.route('/')
def serve_interface():
    """Serve the web interface."""
    return send_from_directory(STATIC_DIR, 'web-interface.html')


@app.route('/api/search', methods=['POST'])
def start_search():
    """
    Start a Google Maps search.
    Body: {
        "query": "travel agency Milan",
        "maxResults": 20,
        "filters": "optional filters",
        "cities": "Milan, Rome"
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        max_results = int(data.get('maxResults', 20))
        filters = data.get('filters', '').strip()
        cities = data.get('cities', '').strip()

        if not query:
            return jsonify({'error': 'Search query required'}), 400

        if not cities:
            return jsonify({'error': 'At least one city must be specified'}), 400

        city_list = [city.strip() for city in cities.split(',') if city.strip()]
        if not city_list:
            return jsonify({'error': 'Invalid city format. Use comma-separated city names.'}), 400

        min_per_city = max_results          # target per city
        total_target = max_results * len(city_list)   # total across all cities

        search_id = f"search_{int(time.time() * 1000)}"

        active_searches[search_id] = {
            'status': 'running',
            'query': query,
            'full_query': f"{query} {filters}".strip(),
            'max_results': max_results,
            'min_per_city': min_per_city,
            'total_target': total_target,
            'cities': city_list,
            'start_time': datetime.now(),
            'results': []
        }

        thread = threading.Thread(
            target=_run_scraper_multi_city,
            args=(search_id, query, filters, city_list, min_per_city, max_results, total_target)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'search_id': search_id,
            'status': 'started',
            'message': f'Search started for: {query} across {len(city_list)} cities ({min_per_city} results per city, {total_target} total)'
        })

    except Exception as e:
        return jsonify({'error': f'Error starting search: {str(e)}'}), 500


@app.route('/api/search/<search_id>/status', methods=['GET'])
def get_search_status(search_id):
    """Check search status."""
    try:
        if search_id not in active_searches:
            return jsonify({'error': 'Search not found'}), 404

        search_info = active_searches[search_id]

        status_response = {
            'search_id': search_id,
            'status': search_info['status'],
            'query': search_info['query'],
            'results_count': len(search_info['results']),
            'elapsed_time': str(datetime.now() - search_info['start_time'])
        }

        if 'cities' in search_info and search_info['status'] == 'running':
            current_city = search_info.get('current_city', 'Starting...')
            total_target = search_info.get('total_target', search_info.get('max_results', 0))
            status_response['current_city'] = current_city
            status_response['target_total'] = total_target
            status_response['progress'] = f"{len(search_info['results'])}/{total_target}"

        return jsonify(status_response)

    except Exception as e:
        return jsonify({'error': f'Error checking status: {str(e)}'}), 500


@app.route('/api/search/<search_id>/results', methods=['GET'])
def get_search_results(search_id):
    """Get search results."""
    try:
        if search_id not in active_searches:
            return jsonify({'error': 'Search not found'}), 404

        search_info = active_searches[search_id]

        if search_info['status'] == 'running':
            return jsonify({
                'search_id': search_id,
                'status': 'running',
                'message': 'Search still in progress...',
                'results': []
            })

        return jsonify({
            'search_id': search_id,
            'status': search_info['status'],
            'query': search_info['query'],
            'results': search_info['results'],
            'total_results': len(search_info['results'])
        })

    except Exception as e:
        return jsonify({'error': f'Error retrieving results: {str(e)}'}), 500


def _place_to_result_dict(place: Place, city: str) -> dict:
    """Convert a Place dataclass to the API result dict format."""
    return {
        'name': place.name,
        'address': place.address,
        'phone': place.phone_number,
        'website': place.website,
        'type': place.place_type,
        'reviews': f"{place.reviews_count or 0} reviews",
        'hours': place.opens_at,
        'city': city,
    }


def _run_scraper_multi_city(search_id, query, filters, cities, min_per_city, max_results, total_target):
    """Run the scraper across multiple cities using direct function calls."""
    try:
        print(f"Starting multi-city scraping for: {query}")
        print(f"Target cities: {', '.join(cities)}")
        print(f"Target: {total_target} total results, ~{min_per_city} per city")

        all_results = []

        for city_idx, city in enumerate(cities):
            try:
                print(f"Processing city {city_idx + 1}/{len(cities)}: {city}")

                city_query = f"{query} {city}"
                if filters:
                    city_query += f" {filters}"

                # Each city gets exactly min_per_city results
                city_target = min_per_city

                print(f"Target for this city: {city_target} results")

                # Direct function call instead of subprocess
                places = scrape_places(city_query, city_target)

                city_results = [_place_to_result_dict(place, city) for place in places if place.name]
                all_results.extend(city_results)

                print(f"City {city} completed: {len(city_results)} results (total so far: {len(all_results)})")

                active_searches[search_id]['results'] = all_results
                active_searches[search_id]['current_city'] = f"{city_idx + 1}/{len(cities)} - {city}"

            except Exception as e:
                print(f"Error during scraping city {city}: {str(e)}")
                continue

        # If we don't have enough results, do additional scraping on first few cities
        if len(all_results) < total_target:
            print(f"Insufficient results: {len(all_results)}/{total_target}. Running additional scraping...")

            for city in cities[:2]:
                try:
                    needed = total_target - len(all_results)
                    if needed <= 0:
                        break

                    print(f"Additional scraping for {city}: target {needed} additional results")

                    city_query = f"{query} {city}"
                    if filters:
                        city_query += f" {filters}"

                    places = scrape_places(city_query, needed + 10)

                    for place in places:
                        if not place.name:
                            continue
                        # Simple duplicate check
                        is_duplicate = any(
                            r['name'] == place.name and r['address'] == place.address
                            for r in all_results
                        )
                        if not is_duplicate:
                            all_results.append(_place_to_result_dict(place, city))

                    print(f"Additional scraping {city} complete")

                except Exception as e:
                    print(f"Error in additional scraping for {city}: {str(e)}")
                    continue

        active_searches[search_id]['status'] = 'completed'
        active_searches[search_id]['results'] = all_results

        total_found = len(all_results)
        if total_found >= total_target:
            print(f"Multi-city scraping completed: {total_found} total results. Target reached ({total_target})")
        else:
            print(f"Multi-city scraping completed: {total_found} total results. Partial target ({total_found}/{total_target})")

    except Exception as e:
        active_searches[search_id]['status'] = 'error'
        active_searches[search_id]['error'] = str(e)
        print(f"General error during multi-city scraping: {str(e)}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_searches': len(active_searches)
    })


def run_server():
    """Start the API server."""
    print("Starting API Server for Google Maps Scraper")
    print(f"Server available at: http://localhost:{SERVER_PORT}")
    print(f"Web interface at: http://localhost:{SERVER_PORT}")
    print("API endpoints:")
    print("   POST /api/search - Start search")
    print("   GET /api/search/<id>/status - Search status")
    print("   GET /api/search/<id>/results - Search results")
    print("   GET /health - Health check")
    print("\n" + "=" * 50)

    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False, use_reloader=False)


if __name__ == '__main__':
    run_server()
