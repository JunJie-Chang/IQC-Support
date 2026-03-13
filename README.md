# IQC Support Agent

為 **International Quant Competition (IQC)** 團隊設計的 AI 助理，透過 Discord 與使用者互動，並可透過 Notion 工具建立筆記、排程會議、搜尋與列出頁面。

## 功能

- **Discord 機器人**：在頻道中 @ 提及機器人即可對話
- **Notion 整合**：
  - 建立筆記頁面（`create_note`）
  - 建立會議記錄（`create_meeting`）
  - 依關鍵字搜尋頁面（`search_notes`）
  - 列出最近編輯的頁面（`list_recent_pages`）
- **AI 後端**：使用 OpenRouter 呼叫 Claude 模型，具備 function calling 以執行上述工具

## 環境需求

- Python 3.10+
- Discord Bot Token、Notion API、OpenRouter API

## 安裝

```bash
# 複製專案後進入目錄
cd IQC-agent

# 建議使用虛擬環境
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

## 環境變數

在專案根目錄建立 `.env`，並填入以下變數（勿將 `.env` 提交至版本控制）：

| 變數 | 說明 |
|------|------|
| `DISCORD_BOT_TOKEN` | Discord 應用程式機器人 Token |
| `NOTION_API_KEY` | Notion 整合用的 API Key |
| `NOTION_PARENT_PAGE_ID` | 筆記/會議要建立於其下的 Notion 父頁面 ID |
| `OPENROUTER_API_KEY` | OpenRouter API Key（用於呼叫 Claude） |
| `OPENROUTER_MODEL` | 選用，預設為 `anthropic/claude-opus-4` |

## 執行

啟動 Discord 機器人（背景常駐）：

```bash
python bot.py
```

機器人上線後，在任一頻道中 **@ 提及機器人** 並輸入指令，例如：

- 「幫我建立一則筆記：標題『週會重點』，內容是……」
- 「排一個會議：主題 XXX，日期 2025-03-15，時間 14:00，與會者 A, B，議程……」
- 「搜尋和『策略』有關的筆記」
- 「列出最近 5 則頁面」

## 專案結構

```
IQC-agent/
├── agent.py        # AI 邏輯：OpenRouter + 工具定義與呼叫
├── bot.py          # Discord 機器人入口
├── notion_tools.py # Notion API 封裝（建立筆記、會議、搜尋、列表）
├── requirements.txt
├── .env            # 環境變數（需自行建立，勿提交）
└── README.md
```

## 授權與注意事項

- 請妥善保管 `.env` 中的 API Key 與 Token，勿提交至 Git
- Discord 機器人需在應用程式設定中開啟 **Message Content Intent**，才能讀取訊息內容
