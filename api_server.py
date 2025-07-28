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
        
        if not query:
            return jsonify({'error': 'Query di ricerca richiesta'}), 400
        
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
            'temp_file': temp_file,
            'start_time': datetime.now(),
            'results': []
        }
        
        # Avvia scraping in background
        thread = threading.Thread(
            target=run_scraper,
            args=(search_id, full_query, max_results, temp_file)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'search_id': search_id,
            'status': 'started',
            'message': f'Ricerca avviata per: {query}'
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
        
        return jsonify({
            'search_id': search_id,
            'status': search_info['status'],
            'query': search_info['query'],
            'results_count': len(search_info['results']),
            'elapsed_time': str(datetime.now() - search_info['start_time'])
        })
        
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
            timeout=300  # Timeout di 5 minuti
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
                            'type': row.get('business_type', ''),
                            'reviews': f"{row.get('reviews_count', '0')} recensioni",
                            'hours': row.get('opening_hours', '')
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
    
    app.run(host='0.0.0.0', port=5000, debug=True)
