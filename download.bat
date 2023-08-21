@echo off

REM Verifica se o Python 3 está instalado
python --version 2>NUL
if %errorlevel% neq 0 (
    echo Python 3 não está instalado. Por favor, instale o Python 3 para continuar.
    pause
    exit
)

python3 -m pip install --upgrade pip
REM Verifica e instala as dependências
python3 -c "import pkgutil; exit(1 if pkgutil.find_loader('beautifulsoup4') else 0)" && (
    echo beautifulsoup4 já está instalado.
) || (
    python3 -m pip install beautifulsoup4
)

python3 -c "import pkgutil; exit(1 if pkgutil.find_loader('spotdl') else 0)" && (
    echo spotdl já está instalado.
) || (
    @REM python3 -m pip install spotdl
    echo spotdl nao está instalado.

)

python3 -c "import pkgutil; exit(1 if pkgutil.find_loader('ffmpeg-python') else 0)" && (
    echo FFmpeg já foi baixado.
) || (
    python3 -m spotdl --download-ffmpeg
)

REM Executa o arquivo Python
python3 ./functions/index.py

pause