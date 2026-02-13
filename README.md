# 🗺️ Google-Maps-Scraper

Un potente strumento di web scraping per estrarre dati aziendali da Google Maps con interfaccia web moderna e API REST.

## ✨ Caratteristiche

- 🔍 **Scraping reale di Google Maps** con Playwright
- 🌐 **Interfaccia web moderna** in stile terminale
- ⚡ **API REST** per integrazioni
- 📊 **Export CSV automatico** dei risultati
- 🎯 **Ricerca personalizzabile** con filtri
- 🔄 **Monitoraggio tempo reale** delle ricerche
- 📱 **Design responsive** per tutti i dispositivi

## 🚀 Demo

![Google Maps Scraper Interface](https://img.shields.io/badge/Interface-Web%20Based-brightgreen)
![API](https://img.shields.io/badge/API-REST-blue)
![Browser](https://img.shields.io/badge/Browser-Playwright-orange)

## 📦 Installazione

### Prerequisiti
- Python 3.8-3.9 (raccomandato 3.9)
- pip3
- Git

### 1. Clona il repository
```bash
git clone https://github.com/rickyvale04/GoogleMapsScraper.git
cd GoogleMapsScraper
```

### 2. Installa le dipendenze
```bash
pip3 install -r requirements.txt
playwright install chromium
```

### 3. Avvia il server
```bash
python3 api_server.py
```

### 4. Apri l'interfaccia
Vai su: `http://localhost:5001`

## 🎯 Utilizzo

### Interfaccia Web
1. **Inserisci query**: Es. "agenzia di viaggi cinesi Milano"
2. **Imposta filtri** (opzionale): Es. "zona centro"
3. **Scegli numero risultati**: Da 1 a 100
4. **Clicca "Avvia Ricerca"**
5. **Attendi i risultati** (lo scraping avviene in background, senza aprire il browser)
6. **Scarica CSV** con i dati estratti

### Linea di Comando
```bash
# Scraping in background (headless - default)
python3 main.py -s "agenzia di viaggi cinesi Milano" -t 20 -o risultati.csv

# Scraping con browser visibile (per debug)
python3 main.py -s "agenzia di viaggi cinesi Milano" -t 20 -o risultati.csv --visible
```

### API REST

#### Avvia ricerca
```bash
curl -X POST http://localhost:5001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "agenzia di viaggi cinesi Milano", "maxResults": 20}'
```

#### Controlla stato
```bash
curl http://localhost:5001/api/search/{search_id}/status
```

#### Ottieni risultati
```bash
curl http://localhost:5001/api/search/{search_id}/results
```

## 📊 Dati Estratti

Per ogni attività commerciale il tool estrae:
- 📍 **Nome** dell'attività
- 🏠 **Indirizzo** completo
- 📞 **Numero di telefono**
- 🌐 **Sito web**
- 🏷️ **Tipo di attività**
- ⭐ **Numero recensioni**
- 🕒 **Orari di apertura**

## 🔧 Configurazione

### Parametri principali
- `query`: Termine di ricerca (es. "ristoranti Milano")
- `maxResults`: Numero massimo risultati (1-100)
- `filters`: Filtri aggiuntivi (opzionale)
- `--visible`: Mostra il browser durante lo scraping (utile per debug)
- `--proxy`: URL del proxy server (es. `http://user:pass@host:port`)

### Personalizzazione
Modifica `config.py` per:
- Cambiare porta del server
- Configurare XPath selectors
- Personalizzare timeout, User-Agent, proxy

## 📁 Struttura Progetto

```
GoogleMapsScraper/
├── 📄 main.py              # CLI entry point
├── 🌐 api_server.py        # Server entry point (backward compat)
├── ⚙️ config.py            # Configurazione centralizzata
├── 📋 requirements.txt     # Dipendenze Python
├── 📁 scraper/             # Package scraping
│   ├── __init__.py
│   └── core.py             # Logica di scraping (Place, extract, scrape)
├── 📁 api/                 # Package API server
│   ├── __init__.py
│   └── server.py           # Flask API con import diretti
├── 📁 static/              # File statici
│   └── web-interface.html  # Interfaccia web
├── 📁 tests/               # Test suite (pytest)
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_extract.py
│   ├── test_scrape.py
│   └── test_api.py
└── 📖 README.md
```

## 🛠️ Sviluppo

### Architettura
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Backend**: Flask + Python
- **Scraping**: Playwright + Chromium
- **Data**: CSV export

### API Endpoints
- `GET /` - Interfaccia web
- `POST /api/search` - Avvia ricerca
- `GET /api/search/<id>/status` - Stato ricerca
- `GET /api/search/<id>/results` - Risultati
- `GET /health` - Health check

## 🔒 Considerazioni Legali

⚠️ **Importante**: Questo tool è per scopi educativi e di ricerca. Assicurati di:
- Rispettare i Terms of Service di Google Maps
- Non sovraccaricare i server con troppe richieste
- Utilizzare i dati nel rispetto della privacy

## 🤝 Contributi

I contributi sono benvenuti! Per contribuire:

1. Fai fork del progetto
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Committa le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Pusha sul branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📋 TODO

- [ ] Aggiungere supporto per più lingue
- [ ] Implementare caching dei risultati
- [ ] Aggiungere filtri geografici avanzati
- [ ] Supporto per batch processing
- [ ] Dashboard analytics

## 📧 Supporto

Se hai problemi o domande:
- 🐛 Apri una [Issue](https://github.com/rickyvale04/GoogleMapsScraper/issues)
- 💬 Contattami su GitHub: [@rickyvale04](https://github.com/rickyvale04)

## 📜 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

## 🌟 Caratteristiche Avanzate

- **Interfaccia terminale retrò** con tema cyberpunk
- **Polling automatico** per aggiornamenti stato
- **Gestione errori robusta** con retry automatico
- **Export CSV personalizzabile** con encoding UTF-8
- **Responsive design** per mobile e desktop
- **API REST completa** per integrazioni

---

⭐ **Se questo progetto ti è utile, lascia una stella!** ⭐