@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  ==========================================================
echo    TRANSCRITOR DE AUDIO - Aliare
echo    Instalacao de dependencias (executar UMA VEZ)
echo  ==========================================================
echo.

REM Verifica Python
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON=py -3
    goto :check_version
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON=python
    goto :check_version
)

echo  [ERRO] Python nao encontrado.
echo.
echo  Instale Python 3.9 ou superior:
echo    https://www.python.org/downloads/
echo  IMPORTANTE: marque "Add Python to PATH" durante a instalacao.
echo.
pause
exit /b 1

:check_version
echo  [OK] Python detectado.
%PYTHON% --version
echo.

REM Cria venv local (isolado, nao precisa de admin)
if not exist "venv" (
    echo  [INFO] Criando ambiente virtual em .\venv ...
    %PYTHON% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERRO] Falha ao criar venv.
        pause
        exit /b 1
    )
    echo  [OK] Ambiente virtual criado.
) else (
    echo  [INFO] Ambiente virtual ja existe.
)

echo.
echo  [INFO] Atualizando pip...
call "venv\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet
if %ERRORLEVEL% NEQ 0 (
    echo  [AVISO] Falha ao atualizar pip, continuando...
)

echo.
echo  [INFO] Instalando faster-whisper e dependencias...
echo         (primeira instalacao baixa ~500MB - pode demorar varios minutos)
echo.
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERRO] Falha na instalacao das dependencias.
    echo  Verifique sua conexao de internet e tente novamente.
    pause
    exit /b 1
)

echo.
echo  ==========================================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo  ==========================================================
echo.
echo  Proximos passos:
echo    1. Coloque arquivos de audio (.ogg, .mp3, etc) na pasta 'entrada\'
echo    2. Execute 'transcrever.bat'
echo    3. Aguarde - na PRIMEIRA execucao baixa o modelo Whisper (~3GB para large-v3)
echo    4. As transcricoes apareceram na pasta 'saida\' como arquivos .txt
echo.
pause
