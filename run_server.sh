#!/bin/bash

# 成本分析系統 - 伺服器後台執行腳本
# 用途：在伺服器上使用 tmux 持續運行應用
# 使用：./run_server.sh

APP_DIR="/opt/cost-analysis"  # 修改為實際路徑
SESSION_NAME="cost-analysis"
PORT="8501"

echo "🚀 啟動成本分析系統伺服器版本..."
echo "📍 應用目錄: $APP_DIR"
echo "📊 端口: $PORT"

# 檢查是否已有 tmux session 運行
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "✅ 應用已在運行"
    echo "📊 查看日誌: tmux capture-pane -t $SESSION_NAME -p"
    echo "🔄 重啟: ./run_server.sh restart"
    exit 0
fi

# 啟動 tmux session
echo "⏳ 建立新 session..."
tmux new-session -d -s $SESSION_NAME -c "$APP_DIR"

# 在 session 中執行啟動命令
tmux send-keys -t $SESSION_NAME "source venv/bin/activate && streamlit run app.py --server.address 0.0.0.0 --server.port $PORT" Enter

echo ""
echo "======================================"
echo "✅ 伺服器已啟動！"
echo "======================================"
echo ""
echo "🌐 訪問地址: http://伺服器IP:$PORT"
echo ""
echo "📊 查看運行狀態:"
echo "   tmux attach-session -t $SESSION_NAME"
echo ""
echo "⏹️  停止應用:"
echo "   tmux kill-session -t $SESSION_NAME"
echo ""
echo "📋 查看日誌:"
echo "   tmux capture-pane -t $SESSION_NAME -p"
echo "======================================"
