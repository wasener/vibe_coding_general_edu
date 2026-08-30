# Vibe Coding：AI 生活應用通識課 — 範例與教學資源

本 repo 收錄《Vibe Coding：AI 生活應用通識課》全書的範例程式、Prompt 起手句、開放資料取用腳本與附錄資源。

本書是給**沒有程式背景的通識學生**寫的 AI 素養與實作入門教材，全書 9 章。目標不是把讀者訓練成工程師，而是培養能負責任使用 AI 的能力。

> **本 repo 只放程式碼與教學資源，不含書籍內文。** 完整章節內容請參閱紙本或電子書。

---

## 重要：本課有兩種難度軌道

第 1 到 5 章打開瀏覽器就能做。**第 6 章開始需要在自己的電腦上安裝 Python 環境**，因為要跑 Flask 伺服器與 SQLite 資料庫。

| 章 | 軌道 | 需要準備什麼 |
| --- | --- | --- |
| 1–5 | **瀏覽器軌** | 只要有瀏覽器與免費帳號，零安裝 |
| 6–7 | **本機軌** | Python 環境（conda）＋ 終端機；第 7 章另需 LLM API 金鑰 |
| 8 | 不限 | 討論與查證練習，不寫程式 |
| 9 | 依主題 | 10 個專題中，入門與基礎題留在瀏覽器軌 |

如果你只想留在瀏覽器軌，第 9 章的十個專題有七個做得到。要做第 6、7 章的完整實作，請先讀 [`SETUP.md`](SETUP.md)。

---

## 快速開始

### 瀏覽器軌（第 1–5 章）

1. 註冊免費帳號：[Google AI Studio](https://aistudio.google.com)、[Lovable](https://lovable.dev)、[Replit](https://replit.com)
2. 打開章節資料夾，例如 `ch03-first-tool/`
3. 複製 `prompts.md` 裡的起手句，貼進工具，開始對話

### 本機軌（第 6–7 章）

```bash
# 1. 建立環境（詳細步驟見 SETUP.md）
conda create -n vibecoding python=3.11
conda activate vibecoding
pip install -r requirements.txt

# 2. 跑第 6 章的藥局查詢網站
cd ch06-data-basics/project-6-5
python init_db.py          # 匯入健保署藥局名冊 CSV
python run.py              # 瀏覽器打開 http://127.0.0.1:8051

# 3. 換跑第 7 章之前，先把第 6 章關掉
kill $(lsof -ti:8051)      # macOS / Linux
```

**第 6 章與第 7 章都用 port 8051。** 同時開兩個一定失敗，錯誤訊息通常是 `Address already in use`。先關掉前一個再跑下一個。

---

## 目錄結構

```
.
├── README.md
├── SETUP.md                      Python 環境安裝（第 6 章起需要）
├── LICENSE                       MIT，適用所有程式碼
├── LICENSE-CONTENT.md            CC BY-NC-SA 4.0，適用文件與教材
├── DISCLAIMER.md                 使用邊界與免責聲明（務必閱讀）
├── requirements.txt              pip 套件清單
├── environment.yml               conda 環境定義
├── .env.example                  環境變數範本，複製成 .env 後填入金鑰
├── .gitignore
│
├── ch01-ai-intro/                認識生成式 AI 與 Vibe Coding
├── ch02-prompt-basics/           跟 AI 好好說話：Prompt 的基本功
├── ch03-first-tool/              一句話做出健康小工具
├── ch04-health-search/           醫療保健與藥妝查詢網站
├── ch05-code-intro/              Python、HTML、JavaScript 與應用
│
├── ch06-data-basics/             資料的基本觀念  ★ 需要 Python 環境
│   ├── README.md
│   ├── prompts.md                Prompt-01 起手句與 8 條細節
│   ├── project-6-5/              藥局查詢網站
│   │   ├── run.py                    Flask 主程式，port 8051
│   │   ├── init_db.py                CSV 匯入 SQLite
│   │   ├── templates/
│   │   └── static/
│   └── exercises.md
│
├── ch07-qa-assistant/            衛教問答小幫手  ★ 需要 Python 環境 + API 金鑰
│   ├── README.md
│   ├── prompts.md                起手句與五段訊息結構範本
│   ├── project-7-2/              健康對話小幫手
│   │   ├── run.py                    Flask 主程式，port 8051
│   │   ├── init_db.py
│   │   ├── templates/                對話分頁／提示編輯分頁
│   │   └── static/
│   └── exercises.md
│
├── ch08-ai-ethics/               真假、隱私與倫理
├── ch09-final-project/           期末專題實戰
│   ├── topic01-daily-health-log/       每日健康記錄本      入門・瀏覽器
│   ├── topic02-medication-reminder/    用藥提醒            基礎・瀏覽器
│   ├── topic03-ingredient-check/       保養品成分檢查      中級・瀏覽器
│   ├── topic04-price-notebook/         藥妝比價筆記        基礎・瀏覽器
│   ├── topic05-clinic-finder/          醫療院所查詢        中級・本機
│   ├── topic06-vaccine-dashboard/      疫苗接種儀表板      基礎・瀏覽器
│   ├── topic07-sunscreen-guide/        防曬衛教            基礎・瀏覽器
│   ├── topic08-skincare-schedule/      保養排程            基礎・瀏覽器
│   ├── topic09-health-qa-bot/          衛教問答小幫手      中級・本機
│   └── topic10-campus-health-wiki/     校園健康小百科      基礎・瀏覽器
│
├── appendix/
│   ├── prompt-templates.md       全書起手句彙整
│   ├── tool-guide.md             免費工具註冊與使用對照
│   ├── glossary.md               名詞解釋
│   └── troubleshooting.md        常見錯誤與排解
│
└── data/
    ├── README.md                 資料取用說明與顯名標示格式
    ├── fetch_scripts/            開放資料下載腳本
    └── samples/                  極小量教學用樣本（標註來源與取用日期）
```

每個章節資料夾內含：

| 檔案 | 內容 |
| --- | --- |
| `README.md` | 該章要做出什麼、需要哪些工具、常見卡關點 |
| `prompts.md` | 該章的起手句與追加細節，可直接複製 |
| `project-X-Y/` | 可實際執行的完整專案（第 6、7 章） |
| `exercises.md` | 課後作業與選擇題題目 |

第 6、7 章的專案資料夾名稱（`project-6-5`、`project-7-2`）與書中操作講義一致，學生照著書打指令就能對得上。

---

## 各章範例對照

| 章 | 主題 | 主要產出 | 工具與技術 |
| --- | --- | --- | --- |
| 1 | 認識生成式 AI 與 Vibe Coding | 第一次對話練習 | Google AI Studio |
| 2 | Prompt 的基本功 | 起手句改寫前後對照 | Google AI Studio |
| 3 | 一句話做出健康小工具 | 可運作的健康小網頁 | Lovable |
| 4 | 醫療保健與藥妝查詢網站 | 成分與藥品查詢網站 | Lovable ＋ 政府開放資料 |
| 5 | Python、HTML、JavaScript 與應用 | 讀懂並微調 AI 生成的程式 | Replit |
| 6 | 資料的基本觀念 | 藥局查詢網站 | Flask ＋ SQLite ＋ Bootstrap ＋ pandas |
| 7 | 衛教問答小幫手 | 健康對話小幫手（雙分頁） | Flask ＋ SQLite ＋ LLM API |
| 8 | 真假、隱私與倫理 | 查證與風險檢核清單 | 不限工具 |
| 9 | 期末專題實戰 | 10 選 1 的完整小作品 | 依主題而定 |

第 5 章的定位是「看懂與微調」，不是「從零手寫」。第 6 章把第 5 章的血壓小工具從「只會記」升級成「查得到」，第 7 章再加上 AI 對話能力——三章是連續的一條線，跳著做會接不上。

---

## 第 6 章：藥局查詢網站

把健保署的藥局名冊 CSV 匯進 SQLite，做成可以搜尋的網站。

**用到的資料集**

| 項目 | 內容 |
| --- | --- |
| 名稱 | 健保特約醫事機構－藥局 |
| 檔案代號 | `A21030000I-D21005-001.csv` |
| 提供機關 | 衛生福利部中央健康保險署 |
| 取得方式 | `data/fetch_scripts/fetch_pharmacy_list.py` |

**流程**：下載 CSV → pandas 讀取與清理 → 匯入 SQLite → Flask 提供查詢介面 → Bootstrap 排版

起手句與 8 條追加細節放在 `ch06-data-basics/prompts.md`。

---

## 第 7 章：健康對話小幫手

雙分頁設計：一頁對話，一頁編輯提示內容。學生可以直接改系統提示，馬上看到回答怎麼變。

**訊息的五段結構**

送進模型的訊息拆成五段，並依優先權裁減，避免超過長度上限：

| 段落 | 作用 |
| --- | --- |
| 角色定義 | 這個小幫手是誰、講話的口吻 |
| 知識庫 | 可以依據的衛教資料 |
| 規範 | 不能做的事（不診斷、不宣稱療效、遇症狀引導就醫） |
| 本次訊息 | 使用者這一次問的問題 |
| 聊天歷史紀錄 | 前面的對話，長度不夠時最先被裁掉 |

**API 金鑰**：複製 `.env.example` 成 `.env` 填入你自己的金鑰。`.env` 已被 `.gitignore` 排除。

---

## 開放資料來源

| 來源 | 網址 | 用於 |
| --- | --- | --- |
| 政府資料開放平臺 | https://data.gov.tw | 各章通用入口 |
| 食藥署開放資料 | https://data.fda.gov.tw | 化粧品成分、藥品資訊（Ch4） |
| 食藥署資料開放服務平台 | https://mcp.fda.gov.tw | 藥品許可證查詢（Ch4） |
| 疾管署開放資料 | https://data.cdc.gov.tw | 疫苗接種、傳染病統計（Ch4、Ch9） |
| 健保署開放資料 | 經 data.gov.tw | 特約藥局與醫療院所名冊（Ch6） |

### 三個原則

1. **不整包 commit 原始資料集。** 用 `data/fetch_scripts/` 現抓。資料會更新，commit 進去很快就過期。
2. **標註來源與取用日期。** 政府開放資料採「政府資料開放授權條款－第 1 版」，未盡顯名標示義務者，視為自始未取得授權。格式見 [`data/README.md`](data/README.md)。
3. **先確認資料實際存了什麼再動手。** 第 4 章有一個完整的踩雷紀錄：藥品仿單查詢表面上做成功了，實際失敗，因為資料集存的是 PDF 連結而非文字內容，最後改成 PDF 檢視器才解決。這是刻意保留的教學案例。

---

## 安全與使用邊界

本書所有作品都遵守以下原則，repo 內的範例也一致：

- **不宣稱療效**
- **不做診斷**
- **不做用藥建議**
- **遇到症狀描述，引導就醫**
- **一律標註資料來源，以官方公告為準**

第 7 章把這幾條寫進系統提示的「規範」段，並在 7.4 做邊界測試。完整說明請讀 [`DISCLAIMER.md`](DISCLAIMER.md)。這不是形式，是這門課的核心教學目標之一。

### API 金鑰安全

第 7 章開始會用到 LLM API 金鑰。**絕對不要把金鑰 commit 進 repo。**

- 金鑰一律寫在 `.env`，程式讀環境變數，不寫死在 `run.py` 裡
- `.gitignore` 已排除 `.env`、`*.key`、`instance/`
- 交作業、貼截圖、上傳到 Replit 之前先確認金鑰沒露出來
- 若不小心推上去了，**立刻到平台後台撤銷該金鑰再重發**。光把 commit 刪掉沒有用，歷史裡的內容還在

---

## 常見卡關

| 症狀 | 原因與處理 |
| --- | --- |
| `Address already in use` | Ch6 與 Ch7 都用 port 8051。先 `kill $(lsof -ti:8051)` 關掉前一個 |
| `ModuleNotFoundError` | 忘記 `conda activate vibecoding`，或沒跑 `pip install -r requirements.txt` |
| 網站查不到任何藥局 | 沒先跑 `init_db.py`，SQLite 還是空的 |
| CSV 讀進來是亂碼 | 政府資料常見 Big5 編碼，指定 `encoding` 參數 |
| AI 回答一直不穩定 | 這是模型特性，不是 bug。第 7.5 節有說明 |

更多見 [`appendix/troubleshooting.md`](appendix/troubleshooting.md)。

---

## 授權

本 repo 採用雙授權，程式碼與教材分開：

| 內容 | 授權 |
| --- | --- |
| 所有程式碼（`.py`、`.html`、`.js`、`.css`、腳本） | [MIT License](LICENSE) |
| 文件、起手句、習題、附錄表格 | [CC BY-NC-SA 4.0](LICENSE-CONTENT.md) |
| 政府開放資料 | 依原提供機關授權條款，見 [`data/README.md`](data/README.md) |
| 書籍內文與書中圖表 | 不在本 repo 授權範圍內，著作權另行保留 |

授課教師可自由於課堂使用、改編本 repo 的教材，改編後請以相同授權釋出並標示出處。

---

## 勘誤與問題回報

請開一個 [Issue](../../issues)，並註明：

- 章節與檔案路徑
- 作業系統與 Python 版本（本機軌）或使用的線上工具（瀏覽器軌）
- 預期結果與實際結果
- 錯誤訊息完整內容（**把金鑰、個資遮掉**）

書中截圖是撰稿當時的工具介面。工具改版快，介面可能有落差，操作邏輯通常不變。

---

## 引用方式

```
（作者姓名）。《Vibe Coding：AI 生活應用通識課》。（出版社），（年份）。
範例程式碼：（本 repo 網址）
```

---

## 作者

（作者姓名），（任職學校／系所）

第 6、7 章由（協同作者姓名）撰寫。
