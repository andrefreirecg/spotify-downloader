@echo off

REM Verifica se o Python 3 está instalado
python --version 2>NUL
if %errorlevel% neq 0 (
    echo Python 3 não está instalado. Por favor, instale o Python 3 para continuar.
    pause
    exit
)

python3 -m pip install --upgrade pip
python3 -m pip install requests
python3 -m pip install BeautifulSoup4
python3 -m pip install bs4
python3 -m pip uninstall spotdl
python3 -m pip install spotdl
python3 -m spotdl --download-ffmpeg

REM Executa o arquivo Python
cd functions
python3 index.py

pause
