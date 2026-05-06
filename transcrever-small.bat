@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Versao alternativa com modelo SMALL (~500MB)
REM Use este se a maquina tiver pouca RAM
REM Qualidade boa, mas pior que medium/large

set WHISPER_MODEL=small
set WHISPER_LANG=pt

call "transcrever.bat"
