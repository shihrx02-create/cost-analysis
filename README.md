# 🚀 成本分析系統 - 正式部署包

**準備日期**: 2025年12月26日  
**應用版本**: 1.0 正式版  
**部署狀態**: ✅ 完全就緒

---

## 📦 你現在擁有什麼

一個**完整的、可獨立運行的成本分析系統**：
- ✅ 自動化 XLSX/CSV 轉 HTML 成本分析表
- ✅ 雙語輸出（中文 + English）
- ✅ PDF 下載功能
- ✅ 自動翻譯製程名稱
- ✅ 5 種貨幣支援
- ✅ 專業 UI（Streamlit）
- ✅ **即便你關機也能運行**

---

## 🎯 3 種部署選擇

### ✨ 推薦：選項 1 - 在公司伺服器上 24/7 運行

**適合**: 多人使用、正式環境、需要隨時訪問

**步驟**:
1. 將整個 `成本分析` 資料夾複製到公司伺服器
2. 在伺服器上執行：
   ```bash
   cd /path/to/成本分析
   ./setup_and_run.sh
   ```
3. 應用將在 `http://伺服器IP:8501` 可用
4. 員工可從任何電腦訪問（無需你開機）

**保持運行**:
```bash
# 使用 tmux（推薦）
tmux new-session -d -s cost-app
tmux send-keys -t cost-app "./setup_and_run.sh" Enter

# 查看狀態
tmux attach-session -t cost-app

# 停止
tmux kill-session -t cost-app
```

---

### 🔄 選項 2 - 在你的 Mac 上持續運行

**適合**: 簡單快速、你的 Mac 24/7 開著

**步驟**:
```bash
cd /Users/grace/Desktop/成本分析
./setup_and_run.sh
```

**員工訪問**: `http://你的Mac局域網IP:8501`

**一直保持運行**:
使用 screen 或 tmux（見上方說明）

---

### 🏠 選項 3 - 員工各自在本機運行

**適合**: 簡單分散、無需伺服器

**步驟**:
1. 分發 `成本分析` 資料夾給員工
2. 員工執行：
   - macOS/Linux: `./setup_and_run.sh`
   - Windows: `setup_and_run.bat`
3. 應用自動開啟，各自獨立運行

---

## 📋 快速檢查清單

執行檢查腳本確保一切就緒：

```bash
cd /Users/grace/Desktop/成本分析
./check_deployment.sh
```

✅ 已驗證：所有檢查通過！

---

## 📚 重要文件說明

| 文件 | 用途 |
|------|------|
| `快速開始.md` | 👈 **新手看這個** - 3 分鐘快速開始 |
| `部署說明.md` | 詳細的伺服器部署指南 |
| `部署檢查清單.md` | 完整的功能和檔案檢查 |
| `app.py` | 主應用程式（不需改動） |
| `requirements.txt` | 所有依賴（自動安裝） |
| `setup_and_run.sh` | macOS/Linux 啟動（無需改動） |
| `setup_and_run.bat` | Windows 啟動（無需改動） |
| `check_deployment.sh` | 部署檢查工具 |

---

## 🚀 立即開始（30 秒快速演示）

```bash
# 打開終端，執行一行命令：
cd /Users/grace/Desktop/成本分析 && ./setup_and_run.sh
```

✨ 瀏覽器會自動開啟應用！

---

## 🌐 訪問方式

### 本地訪問
```
http://localhost:8501
```

### 網路訪問（伺服器/其他電腦）
```
http://伺服器IP:8501
或
http://192.168.x.x:8501
```

### 修改端口（如果 8501 被佔用）
```bash
streamlit run app.py --server.port 9000
```

---

## ✨ 應用功能一覽

### 輸入
- 📁 上傳 XLSX 或 CSV 檔案
- 🏷️ 輸入產品料號（必填）
- 💱 選擇貨幣（必填）
- 📊 設定匯率（必填）

### 輸出
- 📄 HTML 下載（可視化表格）
- 📕 PDF 下載（可列印）
- 🌍 雙語（中文 + English）

### 數據處理
- ✅ 自動識別左欄（現況）和右欄（評估）
- ✅ 自動翻譯製程名稱
- ✅ 計算成本、數量、百分比
- ✅ 美化輸出（符合客戶標準）

---

## 🔧 故障排除

**問題**: 運行時顯示 `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

**問題**: 端口 8501 已被佔用
```bash
streamlit run app.py --server.port 9000
```

**問題**: 員工無法訪問伺服器
1. 檢查伺服器防火牆是否開放 8501
2. 檢查 IP 地址是否正確
3. 嘗試 ping 伺服器確認網路連線

**問題**: 翻譯功能不工作
- 需要網際網路連線（使用 MyMemory API）
- 檢查公司網路是否有限制

更多幫助見 `部署說明.md`

---

## 📊 系統需求

| 項目 | 要求 |
|------|------|
| Python | 3.8+ |
| OS | macOS / Windows / Linux |
| 網路 | 建議有（用於翻譯） |
| 磁碟 | ~500MB |

---

## 💡 最佳實踐

✅ **強烈建議**:
- 定期備份上傳的 XLSX 檔案
- 定期備份應用代碼 `app.py`
- 保持伺服器 Python 最新
- 使用伺服器服務保持應用 24/7 運行

⚠️ **注意**:
- 首次啟動會安裝依賴（2-5 分鐘）
- 自動翻譯需要網路連線
- 防火牆可能需要配置

---

## 🎓 後續改進建議

如果將來需要擴展，可以：
1. 新增更多貨幣和匯率
2. 新增數據庫存儲歷史記錄
3. 新增圖表和視覺化
4. 新增使用者認證和權限管理
5. 部署到雲端（AWS, GCP 等）

---

## 📞 快速參考

**啟動應用**:
```bash
./setup_and_run.sh          # 自動設置 + 啟動
streamlit run app.py        # 直接啟動
```

**伺服器運行**:
```bash
tmux new-session -d -s app
tmux send-keys -t app "./setup_and_run.sh" Enter
```

**停止應用**:
```bash
Ctrl+C                       # 終端
pkill -f "streamlit run"     # 後台
```

**查看日誌**:
```bash
cat logs/app.log
```

---

## 🎉 就這樣！

你現在擁有一個**完整的、可立即部署的企業級應用**！

**下一步**:
1. 選擇部署方案（推薦選項 1）
2. 閱讀 `快速開始.md`
3. 執行 `./setup_and_run.sh`
4. 告訴員工訪問地址

**不需要我開機就能運行** ✅

---

**部署日期**: 2025年12月26日  
**版本**: 1.0 正式版  
**狀態**: 🟢 完全就緒  
**下一步**: 執行 `./setup_and_run.sh` 開始！
