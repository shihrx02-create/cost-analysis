#!/bin/bash

# 成本分析系統 - 部署前檢查

echo "=========================================="
echo "成本分析系統 - 部署前檢查"
echo "=========================================="
echo ""

ERRORS=0

# 檢查 Python
echo "🔍 檢查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "   ✅ Python 版本: $PYTHON_VERSION"
else
    echo "   ❌ 未找到 Python 3"
    ERRORS=$((ERRORS+1))
fi

# 檢查虛擬環境
echo "🔍 檢查虛擬環境..."
if [ -d ".venv" ]; then
    echo "   ✅ 虛擬環境已存在"
else
    echo "   ❌ 虛擬環境不存在"
    ERRORS=$((ERRORS+1))
fi

# 檢查主應用程式
echo "🔍 檢查應用程式..."
if [ -f "app.py" ]; then
    echo "   ✅ app.py 存在"
    # 檢查語法
    if python3 -m py_compile app.py 2>/dev/null; then
        echo "   ✅ app.py 語法正確"
    else
        echo "   ❌ app.py 語法錯誤"
        ERRORS=$((ERRORS+1))
    fi
else
    echo "   ❌ app.py 不存在"
    ERRORS=$((ERRORS+1))
fi

# 檢查依賴清單
echo "🔍 檢查依賴清單..."
if [ -f "requirements.txt" ]; then
    echo "   ✅ requirements.txt 存在"
    STREAMLIT=$(grep -i "streamlit" requirements.txt)
    PANDAS=$(grep -i "pandas" requirements.txt)
    REQUESTS=$(grep -i "requests" requirements.txt)
    
    if [ ! -z "$STREAMLIT" ]; then
        echo "   ✅ streamlit 已列入"
    else
        echo "   ⚠️  streamlit 缺失"
    fi
    
    if [ ! -z "$PANDAS" ]; then
        echo "   ✅ pandas 已列入"
    else
        echo "   ⚠️  pandas 缺失"
    fi
    
    if [ ! -z "$REQUESTS" ]; then
        echo "   ✅ requests 已列入"
    else
        echo "   ⚠️  requests 缺失"
    fi
else
    echo "   ❌ requirements.txt 不存在"
    ERRORS=$((ERRORS+1))
fi

# 檢查啟動腳本
echo "🔍 檢查啟動腳本..."
if [ -f "setup_and_run.sh" ]; then
    if [ -x "setup_and_run.sh" ]; then
        echo "   ✅ setup_and_run.sh 可執行"
    else
        echo "   ⚠️  setup_and_run.sh 不可執行（需執行: chmod +x setup_and_run.sh）"
    fi
else
    echo "   ❌ setup_and_run.sh 不存在"
fi

if [ -f "setup_and_run.bat" ]; then
    echo "   ✅ setup_and_run.bat 存在"
else
    echo "   ❌ setup_and_run.bat 不存在"
fi

# 檢查文檔
echo "🔍 檢查文檔..."
DOCS=0
[ -f "快速開始.md" ] && echo "   ✅ 快速開始.md" && DOCS=$((DOCS+1))
[ -f "部署說明.md" ] && echo "   ✅ 部署說明.md" && DOCS=$((DOCS+1))
[ -f "部署檢查清單.md" ] && echo "   ✅ 部署檢查清單.md" && DOCS=$((DOCS+1))

if [ $DOCS -eq 0 ]; then
    echo "   ⚠️  未找到文檔"
fi

# 檢查 HTML 模板
echo "🔍 檢查 HTML 模板..."
if [ -f "3-041004-032PN-0.html" ]; then
    echo "   ✅ HTML 模板存在"
else
    echo "   ⚠️  未找到 HTML 模板"
fi

echo ""
echo "=========================================="

if [ $ERRORS -eq 0 ]; then
    echo "✅ 所有檢查通過！應用已準備部署"
    echo ""
    echo "🚀 開始部署："
    echo "   ./setup_and_run.sh"
    exit 0
else
    echo "❌ 發現 $ERRORS 個問題，請修復後重試"
    exit 1
fi
