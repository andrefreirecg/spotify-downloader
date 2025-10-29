@echo off

REM Verifica se o Python 3 está instalado
python --version 2>NUL
if %errorlevel% neq 0 (
    echo Python 3 não está instalado. Por favor, instale o Python 3 para continuar.
    pause
    exit
)

echo Atualizando pip...
python3 -m pip install --upgrade pip --quiet

echo Verificando bibliotecas instaladas...

REM Verifica requests
python3 -c "import requests" 2>NUL
if %errorlevel% neq 0 (
    echo Instalando requests...
    python3 -m pip install requests --quiet
) else (
    echo [OK] requests já instalado
)

REM Verifica BeautifulSoup4
python3 -c "import bs4" 2>NUL
if %errorlevel% neq 0 (
    echo Instalando BeautifulSoup4...
    python3 -m pip install BeautifulSoup4 --quiet
) else (
    echo [OK] BeautifulSoup4 já instalado
)

REM Verifica spotdl
python3 -c "import spotdl" 2>NUL
if %errorlevel% neq 0 (
    echo Instalando spotdl...
    python3 -m pip install spotdl --quiet
    echo Baixando ffmpeg...
    python3 -m spotdl --download-ffmpeg
) else (
    echo [OK] spotdl já instalado
)

REM Executa o arquivo Python
echo Iniciando aplicativo...
cd functions
start /B python3 index.py

REM Aguarda um momento para a janela abrir
timeout /t 2 /nobreak >NUL

echo.
echo Aplicativo iniciado! Verifique a janela do Spotify Downloader.
echo.
pause
