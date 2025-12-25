#!/bin/bash

# 成本分析系統 - 自動部署和啟動腳本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================"
echo "成本分析系統 - 部署啟動"
echo "======================================"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 未找到 Python 3"
    echo "請先安裝 Python 3.8 或更新版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"

# 建立虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 建立虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "🔌 啟動虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo "📚 安裝依賴..."
pip install -q -r requirements.txt

# 建立日誌目錄
mkdir -p logs

# 啟動 Streamlit
echo ""
echo "======================================"
echo "✅ 應用啟動成功！"
echo "======================================"
echo ""
echo "🌐 訪問地址:"
echo "   http://localhost:8501"
echo ""
echo "按 Ctrl+C 停止應用"
echo "======================================"
echo ""

streamlit run app.py \
    --logger.level=info \
    --client.toolbarMode=viewer
