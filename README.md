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
│   ├── 通識版_第5章_操作說明_血壓紀錄工具_python_v1.docx
│   └── project-5-6/              範例程式專案
│       ├── blood_pressure.db
│       ├── pic-01-新增紀錄.png
│       ├── pic-02-歷史紀錄.png
│       ├── pic-03-血壓標準設定.png
│       ├── pic-04-歷史紀錄+狀態顯示.png
│       ├── prompt-coding.txt     專案開發所使用的 prompt 範本
│       ├── requirements.txt      環境套件清單
│       ├── run.py                主要執行程式
│       ├── static/
│       │   └── style.css
│       └── templates/
│           ├── add.html
│           ├── base.html
│           ├── history.html
│           └── thresholds.html
│
├── ch06-data-basics/             資料的基本觀念  ★ 需要 Python 環境
│   ├── 通識版_第6章_操作說明_健保特約醫事機構-藥局_python_v1.docx
│   └── project-6-5/              範例程式專案
│       ├── A21030000I-D21005-001.csv
│       ├── pharmacies.db
│       ├── pic-01-資料匯入.png
│       ├── pic-02-查詢.png
│       ├── prompt-coding.txt     專案開發所使用的 prompt 範本
│       ├── requirements.txt      環境套件清單
│       ├── run.py                主要執行程式
│       └── templates/
│           ├── base.html
│           └── index.html
│
├── ch07-qa-assistant/            衛教問答小幫手  ★ 需要 Python 環境 + API 金鑰
│   ├── 通識版_第7章_操作說明_LLM對話應用程式_python_v1.docx
│   └── project-7-2/              範例程式專案
│       ├── config.json
│       ├── health_helper.db
│       ├── pic-01-對話.png
│       ├── pic-02-提示內容編輯.png
│       ├── prompt-coding.txt     專案開發所使用的 prompt 範本
│       ├── requirements.txt      環境套件清單
│       ├── run.py                主要執行程式
│       └── templates/
│           ├── base.html
│           ├── chat.html
│           └── settings.html
│
├── ch08-ai-ethics/               真假、隱私與倫理
├── ch09-final-project/           期末專題實戰
│    ├── 通識版_第9章_操作說明_居家醫療備用藥箱_python_v1.docx
│    └── project-9-3/             範例程式專案
│       ├── A21030000I-E41001-001.csv
│       ├── checklist-medicine-cabinet.txt
│       ├── checklist-medicine-cabinet-after.txt
│       ├── medicine_cabinet.db
│       ├── pic-01-首頁-藥箱現況.png
│       ├── pic-02-新增藥品.png
│       ├── pic-03-查詢藥品.png
│       ├── pic-04-匯入開放資料.png
│       ├── prompt-coding.txt     專案開發所使用的 prompt 範本
│       ├── requirements.txt      環境套件清單
│       ├── run.py                主要執行程式
│       ├── srs-medicine-cabinet.txt
│       ├── static/
│       │   └── css/
│       │       └── style.css
│       ├── stitch_medicinecabinet_home_tool/
│       │   ├── DESIGN.md
│       │   ├── code.html
│       │   └── screen.png
│       └── templates/
│           ├── 404.html
│           ├── about.html
│           ├── add-edit.html
│           ├── base.html
│           ├── detail.html
│           ├── import.html
│           ├── index.html
│           └── search.html
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

## 第 5 章：血壓紀錄工具（project-5-6）

用 Flask ＋ SQLite 做一個能記錄、能查詢，還會自動判斷血壓狀態的小工具。資料存在本機的 `blood_pressure.db`，不需要另外架設資料庫。

**三個頁面**

| 頁面 | 功能 |
| --- | --- |
| 新增紀錄 | 輸入量測日期、時間、收縮壓、舒張壓、脈搏、備註，存成一筆紀錄 |
| 歷史紀錄 | 依日期區間與收縮壓、舒張壓上下限篩選，可單筆刪除，並依血壓狀態自動套色、標示狀態文字 |
| 血壓標準設定 | 自訂四級判定範圍，可一鍵還原預設值 |

**血壓標準預設值**

| 狀態 | 收縮壓 | 舒張壓 | 歷史紀錄底色 |
| --- | --- | --- | --- |
| 正常血壓 | < 120 | < 80 | 不變 |
| 血壓偏高 | 120～129 | < 80 | 黃色 |
| 高血壓一期 | 130～139 | 80～90 | 橘色 |
| 高血壓二期 | ≥ 140 | ≥ 90 | 紅色 |

**流程**：Prompt-01 建立紀錄與查詢功能 → Prompt-02 在既有專案上追加血壓標準設定頁 → `python run.py` 執行（http://127.0.0.1:8051）

**技術**：Flask ＋ SQLite，配色為 `#22713F` 深綠＋ `#FFF8F4` 暖白（改 `static/style.css` 的 `--bp-primary`、`--bp-bg` 即可換色）。開發工具為 claude-code。

血壓分類只是依自訂門檻做「顯示」，不是醫療診斷。完整指令紀錄放在 `ch05-code-intro/project-5-6/prompt-coding.txt`。

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

## 第 7 章範例專案：project-7-2 生活保健小幫手

用 Flask 串接 Gemini API，把「角色定義、知識庫、規範」做成使用者自己就能編輯的畫面。一句起手句加八條細節完成。

**專案概要**

| 項目 | 內容 |
| --- | --- |
| 資料夾 | `ch07-qa-assistant/project-7-2/` |
| 技術 | Flask ＋ SQLite ＋ Gemini API（預設 `gemini-2.5-flash`）＋ Bootstrap |
| 資料庫 | `health_helper.db`（對話紀錄與提示內容） |
| 參數設定 | `config.json`（LLM 供應商、模型、金鑰、輸出長度） |
| 執行埠號 | `python run.py` → http://127.0.0.1:8051 |
| 開發工具 | CODEX |

**流程**：寫起手句（含 8 條細節）→ AI 產生 `run.py` 與樣板 → 測試發現回覆跑出對話框 → 一句話請 AI 修正 → 填入金鑰執行

**金鑰**：到 Google AI Studio 免費申請，填進 `config.json` 的 `llm.api_key`。填好金鑰的 `config.json` 不要傳給別人，也不要推上公開倉庫。

**進階挑戰**：換模型、支援圖片上傳、提示內容版本紀錄、API 使用量統計、回覆下方固定顯示免責提醒。

完整指令紀錄放在 `ch07-qa-assistant/project-7-2/prompt-coding.txt`，操作講義為同章的 `.docx` 檔。

---

## 第 9 章：居家醫療備用藥箱（project-9-3）

期末專題示範：「過期與保存檢核器」。記錄家中常備藥的開封日期，依「開封後有效期限」用綠／黃／紅／灰四色標示狀態，並提供廢棄處理指引。這是全書規劃流程最完整的範例。

**用到的資料集**

| 項目 | 內容 |
| --- | --- |
| 名稱 | 健保用藥品項（藥品開放資料） |
| 檔案代號 | `A21030000I-E41001-001.csv` |
| 提供機關 | 衛生福利部中央健康保險署 |
| 處理方式 | 原始約 22 萬列，篩選眼藥水／內服藥水／外用藥膏三類、只留有效且最新的一筆，實測約 1 秒匯入 |

**流程**：AI 產生 SRS 文件 → 依 SRS 拆出工作清單 → stitch 生成介面樣板 → 中途調整需求（新增藥品查詢與資料匯入）→ 依清單逐頁開發 → 完成

**六個頁面**

| 頁面 | 功能 |
| --- | --- |
| 首頁／藥箱清單 | 卡片呈現所有藥品與剩餘天數，可依分類、狀態、關鍵字篩選 |
| 新增／編輯藥品 | 依分類自動帶入開封後保存天數，可自行覆寫 |
| 藥品詳情 | 到期日、剩餘天數與廢棄處理指引 |
| 藥品查詢 | 查詢健保藥品開放資料，可直接「加入藥箱」 |
| 資料匯入 | 匯入／更新開放資料，自動統計新增、更新、下架筆數 |
| 關於 | 資料來源、免責聲明與最後匯入時間 |

**技術**：Flask ＋ Jinja2 ＋ SQLite（`medicine_cabinet.db`，四張表），執行埠號 8051。第一版用 Streamlit，因無法還原 stitch 樣板而整個換成 Flask——這個換路線的過程刻意保留，示範逐步驗證的價值。開發工具為 claude-code。

SRS（`srs-medicine-cabinet.txt`）、工作清單（`checklist-medicine-cabinet.txt`）與完整指令紀錄（`prompt-coding.txt`）都放在 `ch09-final-project/project-9-3/`，建議對照著看。

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

第 1、2、3、4、8 章由黃煒盛撰寫。 
第 5、6、7、9 章由呂子墨撰寫。
