#!/bin/bash

# 成本分析系統 - GitHub 推送輔助腳本
# 用途：簡化推送代碼到 GitHub 的過程

set -e

echo "╔═══════════════════════════════════════════╗"
echo "║  成本分析系統 - GitHub 推送助手          ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# 檢查 git
if ! command -v git &> /dev/null; then
    echo "❌ 錯誤: Git 未安裝"
    echo "請先安裝 Git: https://git-scm.com/download"
    exit 1
fi

# 檢查是否在 git repo 中
if [ ! -d ".git" ]; then
    echo "❌ 錯誤: 這不是一個 git repository"
    echo "請執行: git init"
    exit 1
fi

# 顯示當前狀態
echo "📊 當前 Git 狀態:"
git status --short

echo ""
echo "🔧 選擇操作:"
echo "  1. 查看更改（git status）"
echo "  2. 添加所有文件並提交"
echo "  3. 推送到 GitHub"
echo "  4. 查看遠程地址"
echo "  5. 設置遠程地址"
echo ""

read -p "請選擇 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📋 詳細狀態:"
        git status
        ;;
    
    2)
        echo ""
        read -p "提交信息 (預設: Update): " commit_msg
        commit_msg=${commit_msg:-"Update"}
        
        git add .
        git commit -m "$commit_msg"
        echo "✅ 提交成功"
        ;;
    
    3)
        echo ""
        git remote -v
        echo ""
        read -p "確認推送到 origin/main? (y/n): " confirm
        
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            git push -u origin main 2>/dev/null || {
                echo "⚠️  推送失敗，可能需要設置遠程地址"
                echo "請執行: git remote add origin <你的GitHub URL>"
            }
        fi
        ;;
    
    4)
        echo ""
        echo "📍 遠程地址:"
        git remote -v
        ;;
    
    5)
        echo ""
        read -p "輸入你的 GitHub Repository URL: " repo_url
        git remote remove origin 2>/dev/null || true
        git remote add origin "$repo_url"
        echo "✅ 遠程地址已設置"
        git remote -v
        ;;
    
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac

echo ""
echo "✅ 操作完成"
