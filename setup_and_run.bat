@echo off
REM 成本分析系統 - 自動部署和啟動腳本 (Windows)

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ======================================
echo 成本分析系統 - 部署啟動 (Windows)
echo ======================================

REM 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 Python
    echo 請先安裝 Python 3.8 或更新版本
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python 版本: %PYTHON_VERSION%

REM 建立虛擬環境
if not exist "venv" (
    echo 📦 建立虛擬環境...
    python -m venv venv
)

REM 啟動虛擬環境
echo 🔌 啟動虛擬環境...
call venv\Scripts\activate.bat

REM 安裝依賴
echo 📚 安裝依賴...
pip install -q -r requirements.txt

REM 建立日誌目錄
if not exist "logs" mkdir logs

REM 啟動 Streamlit
echo.
echo ======================================
echo ✅ 應用啟動成功！
echo ======================================
echo.
echo 🌐 訪問地址:
echo    http://localhost:8501
echo.
echo 按 Ctrl+C 停止應用
echo ======================================
echo.

python -m streamlit run app.py --logger.level=info --client.toolbarMode=viewer

pause
