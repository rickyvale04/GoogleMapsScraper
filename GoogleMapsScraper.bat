@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Google Maps Scraper
color 0A

cls
echo.
echo  =============================================
echo    GOOGLE MAPS SCRAPER
echo  =============================================
echo.

:: ---- Cartella del progetto (dove si trova questo file) ----
set "REPO_DIR=%~dp0"
if "!REPO_DIR:~-1!"=="\" set "REPO_DIR=!REPO_DIR:~0,-1!"
set "APP_DIR=!REPO_DIR!\app"
set "LOG_FILE=!REPO_DIR!\.server.log"
echo  Cartella: !REPO_DIR!
echo.

:: ============================================================
:: STEP 1/5 — TROVA O INSTALLA PYTHON
:: ============================================================
echo  [1/5] Controllo Python...

set "PYTHON="

:: 1a) Controlla python nel PATH corrente
python --version >nul 2>&1
if !errorlevel! equ 0 ( set "PYTHON=python" & goto :python_found )
python3 --version >nul 2>&1
if !errorlevel! equ 0 ( set "PYTHON=python3" & goto :python_found )

:: 1b) Controlla cartelle di installazione comuni (user-level e system-level)
for %%V in (313 312 311 310 39 38) do (
    if "!PYTHON!"=="" (
        if exist "!LOCALAPPDATA!\Programs\Python\Python%%V\python.exe" (
            set "PYTHON=!LOCALAPPDATA!\Programs\Python\Python%%V\python.exe"
            set "PATH=!LOCALAPPDATA!\Programs\Python\Python%%V;!LOCALAPPDATA!\Programs\Python\Python%%V\Scripts;!PATH!"
        )
    )
)
for %%V in (313 312 311 310 39 38) do (
    if "!PYTHON!"=="" (
        if exist "C:\Python%%V\python.exe" (
            set "PYTHON=C:\Python%%V\python.exe"
            set "PATH=C:\Python%%V;C:\Python%%V\Scripts;!PATH!"
        )
    )
)
for %%V in (313 312 311 310 39 38) do (
    if "!PYTHON!"=="" (
        if exist "!ProgramFiles!\Python%%V\python.exe" (
            set "PYTHON=!ProgramFiles!\Python%%V\python.exe"
        )
    )
)
if not "!PYTHON!"=="" goto :python_found

:: ============================================================
:: PYTHON NON TROVATO — INSTALLAZIONE AUTOMATICA
:: ============================================================
color 0E
echo.
echo  Python non trovato sul sistema.
echo  Installazione automatica in corso...
echo.
color 0A

:: Tentativo 1: winget (disponibile su Windows 10 1709+ e Windows 11)
winget --version >nul 2>&1
if !errorlevel! equ 0 (
    echo  [winget] Installo Python 3.12 tramite Windows Package Manager...
    winget install Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements

    :: Aggiorna PATH dalla registry (necessario nella sessione corrente)
    for /f "delims=" %%i in ('powershell -NoProfile -Command ^
        "[Environment]::GetEnvironmentVariable('PATH','Machine')+';'+[Environment]::GetEnvironmentVariable('PATH','User')"') do (
        set "PATH=%%i"
    )
    :: Aggiunge anche il path noto di Python 3.12
    set "PATH=!LOCALAPPDATA!\Programs\Python\Python312;!LOCALAPPDATA!\Programs\Python\Python312\Scripts;!PATH!"

    if exist "!LOCALAPPDATA!\Programs\Python\Python312\python.exe" (
        set "PYTHON=!LOCALAPPDATA!\Programs\Python\Python312\python.exe"
        goto :python_found
    )
    python --version >nul 2>&1
    if !errorlevel! equ 0 ( set "PYTHON=python" & goto :python_found )
)

:: Tentativo 2: scarica installer direttamente da python.org
echo  [download] Scaricamento Python 3.12.8 da python.org (~25 MB)...
set "PY_INSTALLER=!TEMP!\python-3.12.8-amd64.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe','!PY_INSTALLER!')"

if not exist "!PY_INSTALLER!" goto :python_error

echo  [install] Installazione Python 3.12 (utente locale — nessun admin richiesto)...
"!PY_INSTALLER!" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1 SimpleInstall=1
del "!PY_INSTALLER!" >nul 2>&1

:: Aggiorna PATH dalla registry dopo l'installazione
for /f "delims=" %%i in ('powershell -NoProfile -Command ^
    "[Environment]::GetEnvironmentVariable('PATH','Machine')+';'+[Environment]::GetEnvironmentVariable('PATH','User')"') do (
    set "PATH=%%i"
)
set "PATH=!LOCALAPPDATA!\Programs\Python\Python312;!LOCALAPPDATA!\Programs\Python\Python312\Scripts;!PATH!"

if exist "!LOCALAPPDATA!\Programs\Python\Python312\python.exe" (
    set "PYTHON=!LOCALAPPDATA!\Programs\Python\Python312\python.exe"
    goto :python_found
)
python --version >nul 2>&1
if !errorlevel! equ 0 ( set "PYTHON=python" & goto :python_found )

:python_error
color 0C
echo.
echo  [ERRORE] Impossibile installare Python automaticamente.
echo.
echo  Soluzione manuale:
echo    1. Vai su:  https://www.python.org/downloads/
echo    2. Scarica e installa Python 3.12 (Windows 64-bit)
echo    3. IMPORTANTE: seleziona "Add Python to PATH"
echo    4. Riavvia il computer, poi riapri questo file
echo.
pause
exit /b 1

:: ============================================================
:: PYTHON TROVATO
:: ============================================================
:python_found
for /f "tokens=*" %%v in ('"!PYTHON!" --version 2^>^&1') do set "PY_VERSION=%%v"
echo  [OK] !PY_VERSION!

:: ============================================================
:: STEP 2/5 — VIRTUAL ENVIRONMENT
:: ============================================================
echo.
echo  [2/5] Ambiente virtuale...

if not exist "!APP_DIR!\.venv" (
    echo  Creazione ambiente virtuale...
    "!PYTHON!" -m venv "!APP_DIR!\.venv"
    if !errorlevel! neq 0 (
        echo  [WARN] venv non creato, continuo senza...
        goto :skip_venv
    )
    echo  [OK] Creato
) else (
    echo  [OK] Gia esistente
)

if exist "!APP_DIR!\.venv\Scripts\activate.bat" (
    call "!APP_DIR!\.venv\Scripts\activate.bat"
)

:skip_venv

:: ============================================================
:: STEP 3/5 — DIPENDENZE PYTHON
:: ============================================================
echo.
echo  [3/5] Dipendenze Python...

set "DEPS_OK=1"
for %%p in (flask playwright pandas) do (
    "!PYTHON!" -c "import %%p" >nul 2>&1
    if !errorlevel! neq 0 set "DEPS_OK=0"
)

if !DEPS_OK! equ 0 (
    echo  Installazione dipendenze (prima volta: 1-3 minuti)...
    "!PYTHON!" -m pip install --quiet -r "!APP_DIR!\requirements.txt"
    if !errorlevel! neq 0 (
        color 0C
        echo  [ERRORE] Installazione dipendenze fallita!
        echo  Verifica la connessione internet e riprova.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Dipendenze installate
) else (
    echo  [OK] Tutte le dipendenze gia installate
)

:: ============================================================
:: STEP 4/5 — PLAYWRIGHT CHROMIUM
:: ============================================================
echo.
echo  [4/5] Browser Chromium...

set "CHROMIUM_FOUND=0"
for /d %%d in ("!LOCALAPPDATA!\ms-playwright\chromium-*") do (
    if exist "%%d\chrome-win\chrome.exe" set "CHROMIUM_FOUND=1"
)

if !CHROMIUM_FOUND! equ 0 (
    echo  Download Chromium (200 MB — solo la prima volta, attendere)...
    "!PYTHON!" -m playwright install chromium
    if !errorlevel! neq 0 (
        color 0C
        echo  [ERRORE] Download Chromium fallito!
        echo  Verifica la connessione internet e riprova.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Chromium installato
) else (
    echo  [OK] Chromium gia installato
)

:: ============================================================
:: STEP 5/5 — AVVIO SERVER
:: ============================================================
echo.
echo  [5/5] Avvio server...

:: Controlla se il server e' gia in esecuzione
netstat -ano 2>nul | findstr ":5001 " >nul 2>&1
if !errorlevel! equ 0 (
    echo  [OK] Server gia in esecuzione
    start "" "http://localhost:5001"
    echo.
    echo  Browser aperto su http://localhost:5001
    echo  Premi un tasto per chiudere questa finestra...
    pause >nul
    exit /b 0
)

echo.
echo  =============================================
echo    Tutto pronto!
echo    Interfaccia: http://localhost:5001
echo    Chiudi questa finestra per fermare il server
echo  =============================================
echo.

:: Apri il browser dopo 3 secondi
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5001"

:: Avvia il server Flask in foreground
cd /d "!APP_DIR!"
"!PYTHON!" api_server.py

:: Il server si e' fermato
echo.
color 0E
echo  Server fermato.
color 0A
echo  Premi un tasto per chiudere...
pause >nul
