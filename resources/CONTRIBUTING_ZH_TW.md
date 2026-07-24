# 貢獻指南

❤️感謝您向 SecRandom 做出貢獻，您可以為 SecRandom 專案做出包括但不限於反饋 Bug、提出功能請求、貢獻代碼等貢獻。在進行貢獻前，請務必閱讀以下指南。

**語言選擇** [ [简体中文](../CONTRIBUTING.md) | [English](./CONTRIBUTING_EN.md) | **✔繁體中文** ]

> 本 Readme **由 AI 翻譯**，並由我們的開發人員審核。如果您發現任何錯誤，請向我們報告。

## 反饋 Bug

如果在使用 SecRandom 的過程中遇到 Bug，可以在 GitHub Issues 中提交 Bug 反饋。

**請務必準確地按照 Issues 模板中的要求和示例填寫相關字段**，否則開發者可能難以診斷您遇到的問題。

## 提交功能請求

如果您有關於 SecRandom 新功能的想法，歡迎在 GitHub Issues 提交功能請求。

## 貢獻代碼

在為 SecRandom 貢獻代碼之前，請務必閱讀以下指南。

### 技術棧

在開始貢獻之前，了解專案的技術棧將有助於您更快地上手：

| 類別 | 技術/工具 | 用途 |
|------|-----------|------|
| 程式設計語言 | Python 3.13.5 | 專案的主要開發語言 |
| 包管理器 | uv | 依賴管理和虛擬環境建立 |
| UI 框架 | PySide6 + PyQt-Fluent-Widgets | 現代化桌面應用介面開發 |
| 日誌管理 | loguru | 高效的日誌記錄 |
| 數據處理 | numpy & pandas | 數據處理和分析 |
| 語音合成 | edge-tts | 文本轉語音功能 |
| Excel 處理 | openpyxl | Excel 檔案導入導出 |
| 安全認證 | pyotp | 雙因素認證 |

### 開發環境搭建

#### 1. 前置條件

確保您的系統已安裝以下軟體：

- Python 3.13.5
- Git
- uv 包管理器 ([安裝指南](https://docs.astral.sh/uv/getting-started/))

#### 2. 準備工作

1. **Fork 專案**
   - 訪問 [SecRandom GitHub 倉庫](https://github.com/SECTL/SecRandom)
   - 點擊右上角的 "Fork" 按鈕，建立您自己的倉庫副本

2. **克隆倉庫**

   ```bash
   git clone https://github.com/您的使用者名/SecRandom.git
   cd SecRandom
   ```

3. **添加上游倉庫**

   ```bash
   git remote add upstream https://github.com/SECTL/SecRandom.git
   ```

#### 3. 安裝依賴

使用 uv 安裝專案依賴：

```bash
uv sync
```

#### 4. 運行專案

安裝依賴後，您可以直接運行專案：

```bash
uv run main.py
```

#### 5. C# IPC 相關開發

您需要 .NET 9.0 來生成 .NET 組件的 Python 存根（用於 IDE 提示）。如果您選擇放棄 IDE 提示，則無需安裝 .NET 9.0。
組件存放在 `data/dlls` 目錄中。以下是存根生成方法：

```bash
powershell ./scripts/generate-stubs.ps1
```

如果您正在使用 Linux 發行版，請先安裝 [PowerShell 7](https://github.com/PowerShell/PowerShell)，並將上方命令中的 `powershell` 替換為 `pwsh`。

### 貢獻準則

**您為 SecRandom 貢獻的功能須遵循以下準則：**

- **穩定**：您貢獻的功能需要能盡可能穩定工作。
- **具有泛用性**：您貢獻的功能需要面向大部分使用者。
- **激進功能需添加開關**：如果您貢獻的功能比較激進，請添加功能開關，並預設禁用此功能。
- **能用**：在提交補丁前，請在本地測試您實現的功能是否能正常使用。
- 盡量不要提交僅包含文案修復的補丁。

### 補丁品質

隨著本專案的規模逐漸擴大，有些使用者提交了一些低品質的補丁。這些補丁有的完全不能實現預期的功能，有的甚至根本不能通過編譯，浪費了開發者的時間和精力對這些補丁進行代碼審閱和問題排查。我們接受有瑕疵的補丁， **但我們希望您在提交補丁前，您的補丁至少應該滿足以下的要求：**

- 實現的功能能夠工作，在提交補丁前請至少在本地機器測試一次補丁的功能是否可以正常工作。
- 我們不建議在沒有人為干預的情況下完全地使用生成式人工智能實現您要貢獻的功能。

如果您持續提交低品質的補丁，我們可能會限制您繼續向本專案/組織提交補丁。

### 分支與開發週期

SecRandom 代碼倉庫目前具有以下分支：

- `master`：SecRandom 主要開發分支。

當開始下個版本的 SecRandom 時，會將當前的主分支分叉到對應的維護分支。在開發下一個版本的 SecRandom 過程中，也會在維護分支上並行維護當前穩定版本的功能。

由於不同開發分支上的代碼介面可能存在差異。因此，**根據您做出的貢獻類型，您需要選擇不同的基礎分支。**

**以下類型的貢獻建議以當前的維護分支為基礎分支：**

- 修復穩定版中的 Bug
- 對穩定版中的功能進行小幅度的優化

**以下類型的貢獻建議以 `master` 為基礎分支：**

- 添加新的功能
- 對代碼進行重構
- 其它對 SecRandom 進行較大改動的貢獻
- 修改README等文檔

### 提交

在本代碼倉庫提交時，請盡量遵守 [約定式提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/) 規範。

### 合併更改

在進行合併之前，請先測試您貢獻的代碼，確保您貢獻的代碼能穩定運作。

您可以向本專案發起 [Pull Request](https://github.com/SECTL/SecRandom/pulls) 來合併您的更改。在發起 Pull Request 時，請簡要地描述您做的更改，並最好附上您實現的功能的演示截圖/影片。

### Actions 構建工作流

SecRandom 專案使用 GitHub Actions 進行自動構建和發布，配置文件位於 `.github/workflows/build-unified.yml`。

#### 觸發構建

您可以通過以下方式觸發構建：

1. **提交消息觸發**：
   - 在 commit 消息中包含 `开始打包` 關鍵詞
   - 示例：`git commit -m "新增功能 开始打包"`

---

感謝您對 SecRandom 專案的支持和貢獻！讓我們一起打造更好的公平隨機抽取系統！ 🚀
