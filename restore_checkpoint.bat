@echo off
:: This script restores the latest checkpoint from GitHub

echo 🔄 Restoring latest checkpoint...

:: Go to your project directory
cd /d "C:\Users\Anushka M\Documents\pathxv0.4"

:: Pull latest changes from GitHub
git fetch origin
git reset --hard origin/main

echo ✅ Checkpoint restored to the latest commit from GitHub!
pause
