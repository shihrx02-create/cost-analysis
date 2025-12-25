#!/bin/bash

# ═════════════════════════════════════════════════════════════
# 成本分析應用 - 一鍵推送到 GitHub
# ═════════════════════════════════════════════════════════════

echo "📤 開始推送代碼到 GitHub..."
echo ""

# 檢查 Git 配置
if ! git config user.name &> /dev/null; then
    echo "❌ Git 未配置"
    echo "請先執行以下命令配置 Git："
    echo ""
    echo "  git config --global user.name '你的名字'"
    echo "  git config --global user.email '你的郵箱'"
    echo ""
    exit 1
fi

# 檢查 remote 設定
if ! git remote get-url origin &> /dev/null; then
    echo "❌ 尚未設定 GitHub repository"
    echo ""
    echo "請先執行："
    echo "  git remote add origin https://github.com/[用戶名]/cost-analysis.git"
    echo ""
    exit 1
fi

echo "✅ Git 配置正常"
echo "📍 Repository: $(git remote get-url origin)"
echo ""

# 推送
read -p "準備推送？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    git commit -m "更新成本分析應用 $(date +%Y-%m-%d)"
    git branch -M main
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ 推送成功！"
        echo ""
        echo "下一步："
        echo "1. 訪問 https://streamlit.io/cloud"
        echo "2. 按 'New app'"
        echo "3. 選擇你的 repository: cost-analysis"
        echo "4. 點擊 'Deploy'"
        echo ""
    else
        echo "❌ 推送失敗"
        exit 1
    fi
else
    echo "取消推送"
fi
