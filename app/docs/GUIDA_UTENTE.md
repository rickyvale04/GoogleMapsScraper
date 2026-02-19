# Google Maps Scraper -- Guida Utente

Guida completa in italiano per l'installazione, l'utilizzo e la risoluzione dei problemi.

## Requisiti di sistema

- **Python 3.8 o superiore** (raccomandato 3.9+)
- **pip** (incluso con Python)
- **Git**
- **Connessione a Internet** (necessaria per scaricare Chromium e per lo scraping)

Sistemi operativi supportati: macOS, Windows, Linux.

## Avvio rapido

### 1. Clona il repository

```bash
git clone https://github.com/rickyvale04/GoogleMapsScraper.git
cd GoogleMapsScraper
```

### 2. Avvia lo script

- **macOS / Linux:** fai doppio clic su `start.command`
- **Windows:** fai doppio clic su `startWindows.bat`

Lo script controlla automaticamente che Python sia installato, crea un ambiente virtuale, installa le dipendenze e scarica Chromium. Al termine avvia il server.

### 3. Apri l'interfaccia web

Il browser si apre su `http://localhost:5001`. Se non si apre automaticamente, copia l'indirizzo nella barra del browser.

## Come usare l'interfaccia web

L'interfaccia web ha un tema terminale scuro e presenta quattro campi di input e tre pulsanti.

### Campi di input

| Campo | Descrizione | Esempio |
|---|---|---|
| **Search query** | Tipo di attivita da cercare | `ristoranti sushi`, `farmacie`, `agenzie di viaggio` |
| **Target cities** | Lista di citta separate da virgola | `Milano, Roma, Napoli` |
| **Additional filters** | Parole chiave aggiuntive (facoltativo) | `zona centro`, `aperto la domenica` |
| **Minimum number of results** | Quanti risultati raccogliere per citta (1--200) | `20` |

### Pulsanti

| Pulsante | Funzione |
|---|---|
| **Start Search** | Avvia la ricerca su Google Maps |
| **Download CSV** | Scarica i risultati in formato CSV (attivo dopo il completamento) |
| **Clear Results** | Pulisce i risultati e resetta il modulo |

### Procedura

1. Inserisci la query di ricerca (es. "ristoranti giapponesi").
2. Inserisci una o piu citta separate da virgola.
3. (Facoltativo) Aggiungi filtri aggiuntivi.
4. Imposta il numero minimo di risultati.
5. Clicca **Start Search**.
6. Attendi il completamento. La barra di stato mostra la citta in elaborazione e il numero di risultati trovati.
7. Clicca **Download CSV** per scaricare i dati.

## Tempi di attesa stimati

| Scenario | Tempo stimato |
|---|---|
| 20 risultati in 1 citta | 2--5 minuti |
| 20 risultati in 3 citta | 5--15 minuti |
| 100 risultati in 1 citta | 10--25 minuti |

I tempi dipendono dalla velocita della connessione e dal carico dei server Google.

## Dati estratti

Per ogni attivita commerciale vengono estratti:

- **Nome** dell'attivita
- **Indirizzo** completo
- **Numero di telefono**
- **Sito web**
- **Tipo di attivita** (es. "Ristorante", "Farmacia")
- **Numero di recensioni**
- **Orari di apertura**

I risultati vengono esportati come file CSV con codifica UTF-8.

## Uso da riga di comando

Puoi eseguire lo scraper senza interfaccia web:

```bash
# Ricerca base (browser nascosto)
python3 main.py -s "ristoranti sushi Milano" -t 20 -o risultati.csv

# Browser visibile (utile per debug)
python3 main.py -s "ristoranti sushi Milano" -t 20 --visible

# Aggiungere risultati a un file esistente
python3 main.py -s "farmacie Roma" -t 10 -o risultati.csv --append

# Usare un proxy
python3 main.py -s "hotel Firenze" -t 15 --proxy http://user:pass@host:port
```

### Opzioni CLI

| Opzione | Descrizione | Default |
|---|---|---|
| `-s`, `--search` | Query di ricerca | `"turkish stores in toronto Canada"` |
| `-t`, `--total` | Numero minimo di risultati | `20` |
| `-o`, `--output` | Percorso del file CSV | `result.csv` |
| `--append` | Aggiunge i risultati al file esistente | disattivo |
| `--headless` | Esegue il browser senza finestra visibile | attivo |
| `--no-headless`, `--visible` | Mostra la finestra del browser | disattivo |
| `--proxy` | URL del server proxy | nessuno |

## API REST

Avvia il server con `python3 api_server.py`, poi usa gli endpoint seguenti.

### Avviare una ricerca

```bash
curl -X POST http://localhost:5001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ristoranti sushi", "maxResults": 20, "cities": "Milano, Roma"}'
```

**Parametri del body:**

| Parametro | Tipo | Descrizione |
|---|---|---|
| `query` | string | Query di ricerca (obbligatorio) |
| `maxResults` | integer | Numero minimo di risultati |
| `filters` | string | Filtri aggiuntivi |
| `cities` | string | Citta separate da virgola |

**Risposta:**
```json
{"search_id": "abc123", "status": "started"}
```

### Controllare lo stato

```bash
curl http://localhost:5001/api/search/{search_id}/status
```

Restituisce `status` (`running`, `completed`, `error`, `timeout`), `elapsed_time`, `current_city` e `progress`.

### Ottenere i risultati

```bash
curl http://localhost:5001/api/search/{search_id}/results
```

Restituisce `results` (array di oggetti) e `query`.

### Altri endpoint

| Metodo | Percorso | Descrizione |
|---|---|---|
| `GET` | `/` | Interfaccia web |
| `GET` | `/health` | Controllo di stato del server |

## Configurazione

Modifica il file `config.py` per personalizzare:

- **Porta del server** (`SERVER_PORT`, default `5001`)
- **Selettori XPath** (`XPATHS`) -- da aggiornare se Google Maps cambia la struttura della pagina
- **Timeout** (`DEFAULT_PAGE_TIMEOUT`, `NAVIGATION_TIMEOUT`, ecc.)
- **Rotazione User-Agent** (`USER_AGENTS`)
- **Proxy** (`DEFAULT_PROXY`)
- **Modalita headless** (`DEFAULT_HEADLESS`)

## Risoluzione problemi

### Python non trovato

Gli script di avvio cercano prima `python3`, poi `python`. Se nessuno dei due viene trovato:

- **macOS:** `brew install python3`
- **Ubuntu/Debian:** `sudo apt install python3 python3-pip python3-venv`
- **Windows:** scarica da <https://www.python.org/downloads/> e assicurati di selezionare **"Add Python to PATH"** durante l'installazione.

### Porta 5001 occupata

Su macOS, **AirPlay Receiver** usa la porta 5001 per default. Per liberarla:

1. Apri **Impostazioni di Sistema > Generali > AirDrop e Handoff**
2. Disattiva **Ricevitore AirPlay**

In alternativa, cambia `SERVER_PORT` in `config.py`.

### Chromium non si installa

Se `playwright install chromium` fallisce:

- Verifica di avere una connessione a Internet funzionante.
- Su Linux, installa le librerie di sistema necessarie: `sudo npx playwright install-deps chromium` oppure consulta la [documentazione di Playwright](https://playwright.dev/python/docs/intro).
- Su reti aziendali, configura il proxy in `config.py` o usa `--proxy` da riga di comando.

### 0 risultati

- Google Maps puo mostrare risultati diversi in base alla lingua e all'indirizzo IP. Prova una query piu specifica (es. aggiungi il nome della citta).
- Se lo scraping non funziona per nessuna query, i selettori XPath in `config.py` potrebbero dover essere aggiornati.
- Esegui con `--visible` per vedere cosa fa il browser.

### La ricerca e molto lenta

- Ogni risultato richiede il caricamento di una pagina di dettaglio, quindi numeri alti richiedono piu tempo.
- Se usi un proxy lento, prova senza.
- Controlla la velocita della connessione Internet.
