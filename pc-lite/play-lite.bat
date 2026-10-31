@echo off
chcp 65001 >nul
cd /d %~dp0
echo Starting APK Cloud LITE player (this PC only)...
python lite-player.py
pause
