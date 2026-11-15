@echo off
setlocal enableextensions
title Dashboard reparto avvolgimenti
cd /d "%~dp0"

echo ============================================================
echo  Dashboard di monitoraggio - reparto costruzione avvolgimenti
echo ============================================================
echo.

rem --- 1. Ricerca di Python ---------------------------------------------
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [ERRORE] Python non trovato.
    echo Installa Python 3.10 o successivo da https://www.python.org/downloads/
    echo e spunta "Add python.exe to PATH" durante l'installazione.
    echo.
    pause
    exit /b 1
)
echo [OK] Python trovato: %PY%
%PY% --version

rem --- 2. Controllo librerie --------------------------------------------
echo.
echo Controllo delle librerie necessarie...
%PY% -c "import streamlit, plotly, pandas, numpy, sklearn, lightgbm, shap, joblib" >nul 2>nul
if errorlevel 1 (
    echo Alcune librerie mancano: installazione in corso ^(serve internet, richiede qualche minuto^)...
    %PY% -m pip install --upgrade pip
    %PY% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERRORE] Installazione delle librerie non riuscita. Controlla la connessione a internet.
        pause
        exit /b 1
    )
) else (
    echo [OK] Tutte le librerie sono gia' presenti.
)

rem --- 3. Avvio dell'app -------------------------------------------------
echo.
echo Avvio della dashboard: si aprira' il browser su http://localhost:8501
echo Per chiudere l'app premi CTRL+C in questa finestra (o chiudila).
echo.
%PY% -m streamlit run app.py --server.headless false --browser.gatherUsageStats false

if errorlevel 1 (
    echo.
    echo [ERRORE] L'app si e' interrotta con un errore.
    pause
)
endlocal
