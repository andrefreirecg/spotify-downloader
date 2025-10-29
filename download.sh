#!/bin/bash

echo "Verificando se o Python 3 está instalado..."

# Verifica se o Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não está instalado. Por favor, instale o Python 3 para continuar."
    exit 1
fi

echo "Atualizando pip..."
python3 -m pip install --upgrade pip --quiet

echo "Verificando bibliotecas instaladas..."

# Verifica requests
if ! python3 -c "import requests" 2>/dev/null; then
    echo "Instalando requests..."
    python3 -m pip install requests --quiet
else
    echo "[OK] requests já instalado"
fi

# Verifica BeautifulSoup4
if ! python3 -c "import bs4" 2>/dev/null; then
    echo "Instalando BeautifulSoup4..."
    python3 -m pip install BeautifulSoup4 --quiet
else
    echo "[OK] BeautifulSoup4 já instalado"
fi

# Verifica spotdl
if ! python3 -c "import spotdl" 2>/dev/null; then
    echo "Instalando spotdl..."
    python3 -m pip install spotdl --quiet
    echo "Baixando ffmpeg..."
    python3 -m spotdl --download-ffmpeg
else
    echo "[OK] spotdl já instalado"
fi

# Executa o arquivo Python
echo "Iniciando aplicativo..."
cd functions
python3 index.py

echo ""
echo "Aplicativo fechado."

