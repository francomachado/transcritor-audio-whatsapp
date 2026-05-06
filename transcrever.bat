@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM ============================================================
REM   Transcritor de Audio em Lote - Aliare
REM   Le pasta 'entrada' e gera .txt na pasta 'saida'
REM ============================================================

REM Verifica se o venv existe
if not exist "venv\Scripts\activate.bat" (
    echo.
    echo  [ERRO] Ambiente virtual nao encontrado.
    echo         Execute primeiro: instalar.bat
    echo.
    pause
    exit /b 1
)

REM Ativa o venv
call "venv\Scripts\activate.bat"

REM Cria pastas de entrada/saida se nao existirem
if not exist "entrada" mkdir "entrada"
if not exist "saida" mkdir "saida"

REM Modelo padrao - voce pode trocar aqui
REM Opcoes: tiny, base, small, medium, large-v3
REM Recomendo large-v3 para qualidade maxima em PT-BR
REM Se a maquina for fraca, use 'medium' ou 'small'
if "%WHISPER_MODEL%"=="" set WHISPER_MODEL=large-v3
if "%WHISPER_LANG%"=="" set WHISPER_LANG=pt

REM Executa o script
python transcrever.py

REM Mantem janela aberta se houver erro
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [AVISO] Script encerrou com erro.
    pause
)
