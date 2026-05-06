@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Versao alternativa com modelo MEDIUM (mais leve, ~1.5GB)
REM Use este se o large-v3 estiver muito lento na sua maquina
REM Qualidade ainda excelente para PT-BR

set WHISPER_MODEL=medium
set WHISPER_LANG=pt

call "transcrever.bat"
