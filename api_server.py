#!/usr/bin/env python3
"""
API Server per Google Maps Scraper
Questo server Flask espone endpoints per l'interfaccia web
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import csv
import tempfile
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Abilita CORS per permettere richieste dall'interfaccia web

# Store per i risultati delle ricerche attive
active_searches = {}

@app.route('/')
def serve_interface():
    """Serve l'interfaccia web"""
    return send_from_directory('.', 'web-interface.html')

@app.route('/api/search', methods=['POST'])
def start_search():
    """
    Avvia una ricerca Google Maps
    Body: {
        "query": "travel agency cinesi Milano",
        "maxResults": 20,
        "filters": "optional filters"
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
        
        # Parse cities
        city_list = [city.strip() for city in cities.split(',') if city.strip()]
        if not city_list:
            return jsonify({'error': 'Invalid city format. Use comma-separated city names.'}), 400
        
        # Calculate results per city to ensure we meet the minimum total
        # We want at least max_results total, so distribute across cities
        # Add buffer to ensure we get enough results even if some cities have fewer
        min_per_city = max(max_results // len(city_list), 15)  # At least 15 per city
        total_target = max_results + (len(city_list) * 5)  # Add buffer for better coverage
        
        # Genera un ID unico per questa ricerca
        search_id = f"search_{int(time.time() * 1000)}"
        
        # Crea file temporaneo per i risultati
        temp_file = f"temp_results_{search_id}.csv"
        
        # Costruisci query completa con filtri
        full_query = query
        if filters:
            full_query += f" {filters}"
        
        # Store info sulla ricerca
        active_searches[search_id] = {
            'status': 'running',
            'query': query,
            'full_query': full_query,
            'max_results': max_results,
            'min_per_city': min_per_city,
            'total_target': total_target,
            'cities': city_list,
            'temp_file': temp_file,
            'start_time': datetime.now(),
            'results': []
        }
        
        # Avvia scraping in background
        thread = threading.Thread(
            target=run_scraper_multi_city,
            args=(search_id, query, filters, city_list, min_per_city, max_results, temp_file)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'search_id': search_id,
            'status': 'started',
            'message': f'Search started for: {query} across {len(city_list)} cities (targeting {total_target} total results, ~{min_per_city} per city)'
        })
        
    except Exception as e:
        return jsonify({'error': f'Errore durante l\'avvio della ricerca: {str(e)}'}), 500

@app.route('/api/search/<search_id>/status', methods=['GET'])
def get_search_status(search_id):
    """Controlla lo stato di una ricerca"""
    try:
        if search_id not in active_searches:
            return jsonify({'error': 'Ricerca non trovata'}), 404
        
        search_info = active_searches[search_id]
        
        status_response = {
            'search_id': search_id,
            'status': search_info['status'],
            'query': search_info['query'],
            'results_count': len(search_info['results']),
            'elapsed_time': str(datetime.now() - search_info['start_time'])
        }
        
        # Add progress info for multi-city searches
        if 'cities' in search_info and search_info['status'] == 'running':
            current_city = search_info.get('current_city', 'Starting...')
            total_target = search_info.get('total_target', search_info.get('max_results', 0))
            status_response['current_city'] = current_city
            status_response['target_total'] = total_target
            status_response['progress'] = f"{len(search_info['results'])}/{total_target}"
        
        return jsonify(status_response)
        
    except Exception as e:
        return jsonify({'error': f'Errore nel controllo stato: {str(e)}'}), 500

@app.route('/api/search/<search_id>/results', methods=['GET'])
def get_search_results(search_id):
    """Ottieni i risultati di una ricerca"""
    try:
        if search_id not in active_searches:
            return jsonify({'error': 'Ricerca non trovata'}), 404
        
        search_info = active_searches[search_id]
        
        if search_info['status'] == 'running':
            return jsonify({
                'search_id': search_id,
                'status': 'running',
                'message': 'Ricerca ancora in corso...',
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
        return jsonify({'error': f'Errore nel recupero risultati: {str(e)}'}), 500

def run_scraper_multi_city(search_id, query, filters, cities, min_per_city, target_total, temp_file):
    """
    Esegue lo scraper Google Maps per multiple città in background
    """
    try:
        print(f"🔍 Avvio scraping multi-città per: {query}")
        print(f"🏙️ Città target: {', '.join(cities)}")
        print(f"🎯 Target: {target_total} risultati totali, ~{min_per_city} per città")
        
        all_results = []
        
        for city_idx, city in enumerate(cities):
            try:
                print(f"📍 Elaborando città {city_idx + 1}/{len(cities)}: {city}")
                
                # Costruisci query specifica per la città
                city_query = f"{query} {city}"
                if filters:
                    city_query += f" {filters}"
                
                # File temporaneo per questa città
                city_temp_file = f"temp_{search_id}_{city_idx}.csv"
                
                # Calculate how many more results we need
                results_so_far = len(all_results)
                remaining_cities = len(cities) - city_idx
                
                # If we're running low on results, increase the target for remaining cities
                if results_so_far < (target_total * (city_idx / len(cities))):
                    # We're behind target, increase the requirement for this city
                    city_target = max(min_per_city, (target_total - results_so_far) // remaining_cities + 10)
                else:
                    city_target = min_per_city
                
                print(f"🎯 Target per questa città: {city_target} risultati")
                
                # Comando per eseguire main.py per questa città
                cmd = [
                    'python3', 'main.py',
                    '-s', city_query,
                    '-t', str(city_target),
                    '-o', city_temp_file
                ]
                
                print(f"🔧 Comando: {' '.join(cmd)}")
                
                # Esegui il comando
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minuti per città
                )
                
                if result.returncode == 0:
                    # Successo - leggi i risultati dal CSV
                    if os.path.exists(city_temp_file):
                        city_results = []
                        with open(city_temp_file, 'r', encoding='utf-8') as csvfile:
                            reader = csv.DictReader(csvfile)
                            for row in reader:
                                result_data = {
                                    'name': row.get('name', ''),
                                    'address': row.get('address', ''),
                                    'phone': row.get('phone_number', ''),
                                    'website': row.get('website', ''),
                                    'type': row.get('place_type', ''),
                                    'reviews': f"{row.get('reviews_count', '0')} reviews",
                                    'hours': row.get('opens_at', ''),
                                    'city': city  # Add city information
                                }
                                city_results.append(result_data)
                                all_results.append(result_data)
                        
                        # Pulisci file temporaneo della città
                        try:
                            os.remove(city_temp_file)
                        except:
                            pass
                        
                        print(f"✅ Città {city} completata: {len(city_results)} risultati (totale fino ad ora: {len(all_results)})")
                        
                        # Update progress in active_searches
                        active_searches[search_id]['results'] = all_results
                        active_searches[search_id]['current_city'] = f"{city_idx + 1}/{len(cities)} - {city}"
                    else:
                        print(f"⚠️ Nessun file risultati per città: {city}")
                        
                else:
                    # Errore durante lo scraping di questa città
                    error_msg = result.stderr or f"Errore durante scraping di {city}"
                    print(f"❌ Errore per città {city}: {error_msg}")
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout per città: {city}")
                continue
            except Exception as e:
                print(f"💥 Errore durante scraping città {city}: {str(e)}")
                continue
        
        # Check if we have enough results, if not, do additional scraping on first few cities
        if len(all_results) < target_total:
            print(f"⚠️ Risultati insufficienti: {len(all_results)}/{target_total}. Eseguendo scraping aggiuntivo...")
            
            # Do additional scraping on the first 2 cities with higher targets
            for city in cities[:2]:
                try:
                    needed = target_total - len(all_results)
                    if needed <= 0:
                        break
                        
                    print(f"🔄 Scraping aggiuntivo per {city}: target {needed} risultati aggiuntivi")
                    
                    city_query = f"{query} {city}"
                    if filters:
                        city_query += f" {filters}"
                    
                    additional_temp_file = f"temp_{search_id}_additional_{city}.csv"
                    
                    cmd = [
                        'python3', 'main.py',
                        '-s', city_query,
                        '-t', str(needed + 10),  # Extra buffer
                        '-o', additional_temp_file
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=600
                    )
                    
                    if result.returncode == 0 and os.path.exists(additional_temp_file):
                        with open(additional_temp_file, 'r', encoding='utf-8') as csvfile:
                            reader = csv.DictReader(csvfile)
                            new_results = []
                            for row in reader:
                                # Avoid duplicates by checking if we already have this business
                                name = row.get('name', '')
                                address = row.get('address', '')
                                
                                # Simple duplicate check
                                is_duplicate = any(
                                    r['name'] == name and r['address'] == address 
                                    for r in all_results
                                )
                                
                                if not is_duplicate:
                                    result_data = {
                                        'name': name,
                                        'address': address,
                                        'phone': row.get('phone_number', ''),
                                        'website': row.get('website', ''),
                                        'type': row.get('place_type', ''),
                                        'reviews': f"{row.get('reviews_count', '0')} reviews",
                                        'hours': row.get('opens_at', ''),
                                        'city': city
                                    }
                                    new_results.append(result_data)
                                    all_results.append(result_data)
                        
                        print(f"✅ Scraping aggiuntivo {city}: {len(new_results)} nuovi risultati")
                        
                        try:
                            os.remove(additional_temp_file)
                        except:
                            pass
                            
                except Exception as e:
                    print(f"❌ Errore scraping aggiuntivo per {city}: {str(e)}")
                    continue
        
        # Salva tutti i risultati in un file CSV finale
        if all_results:
            with open(temp_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'address', 'phone', 'website', 'type', 'reviews', 'hours', 'city']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
        
        # Aggiorna lo stato della ricerca
        active_searches[search_id]['status'] = 'completed'
        active_searches[search_id]['results'] = all_results
        
        total_found = len(all_results)
        success_msg = f"🎉 Scraping multi-città completato: {total_found} risultati totali da {len(cities)} città"
        
        if total_found >= target_total:
            success_msg += f" ✅ Target raggiunto ({target_total})"
        else:
            success_msg += f" ⚠️ Target parziale ({total_found}/{target_total})"
            
        print(success_msg)
        
    except Exception as e:
        active_searches[search_id]['status'] = 'error'
        active_searches[search_id]['error'] = str(e)
        print(f"💥 Errore generale durante scraping multi-città: {str(e)}")

def run_scraper(search_id, query, max_results, temp_file):
    """
    Esegue lo scraper Google Maps in background
    """
    try:
        print(f"🔍 Avvio scraping per: {query}")
        
        # Comando per eseguire main.py
        cmd = [
            'python3', 'main.py',
            '-s', query,
            '-t', str(max_results),
            '-o', temp_file
        ]
        
        # Esegui il comando
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # Increased timeout to 10 minutes for more thorough scraping
        )
        
        if result.returncode == 0:
            # Successo - leggi i risultati dal CSV
            results = []
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        results.append({
                            'name': row.get('name', ''),
                            'address': row.get('address', ''),
                            'phone': row.get('phone_number', ''),
                            'website': row.get('website', ''),
                            'type': row.get('place_type', ''),
                            'reviews': f"{row.get('reviews_count', '0')} reviews",
                            'hours': row.get('opens_at', ''),
                            'city': row.get('city', 'Unknown')  # Handle city column for backward compatibility
                        })
                
                # Pulisci file temporaneo
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            # Aggiorna lo stato della ricerca
            active_searches[search_id]['status'] = 'completed'
            active_searches[search_id]['results'] = results
            
            print(f"✅ Scraping completato: {len(results)} risultati trovati")
            
        else:
            # Errore durante lo scraping
            error_msg = result.stderr or "Errore sconosciuto durante lo scraping"
            active_searches[search_id]['status'] = 'error'
            active_searches[search_id]['error'] = error_msg
            
            print(f"❌ Errore scraping: {error_msg}")
    
    except subprocess.TimeoutExpired:
        active_searches[search_id]['status'] = 'timeout'
        active_searches[search_id]['error'] = 'Timeout durante la ricerca'
        print(f"⏰ Timeout per ricerca: {query}")
    
    except Exception as e:
        active_searches[search_id]['status'] = 'error'
        active_searches[search_id]['error'] = str(e)
        print(f"💥 Errore durante scraping: {str(e)}")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_searches': len(active_searches)
    })

if __name__ == '__main__':
    print("🚀 Avvio API Server per Google Maps Scraper")
    print("📍 Server disponibile su: http://localhost:5000")
    print("🌐 Interfaccia web su: http://localhost:5000")
    print("🔧 API endpoints:")
    print("   POST /api/search - Avvia ricerca")
    print("   GET /api/search/<id>/status - Stato ricerca")
    print("   GET /api/search/<id>/results - Risultati ricerca")
    print("   GET /health - Health check")
    print("\n" + "="*50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
