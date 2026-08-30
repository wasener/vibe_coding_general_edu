# 環境安裝：第 6 章開始需要

第 1 到 5 章打開瀏覽器就能做，這份文件可以先跳過。

**第 6 章開始要在自己的電腦上跑 Flask 伺服器**，所以需要裝 Python 環境。這是全課唯一需要安裝東西的地方，裝一次就能用到期末。

預計花 20 到 30 分鐘。裝不起來很正常，卡住就去看最後的「常見安裝問題」。

---

## 一、裝 Miniconda

Conda 幫你把這門課用的套件跟電腦裡其他東西隔開，之後刪掉也不會影響到別的程式。

前往 https://docs.conda.io/projects/miniconda/ 下載對應你系統的安裝檔：

| 系統 | 選哪個 |
| --- | --- |
| Windows | Windows 64-bit 安裝檔（.exe） |
| macOS（M1／M2／M3 以後） | macOS Apple M1 64-bit（.pkg） |
| macOS（Intel） | macOS Intel x86 64-bit（.pkg） |

安裝時全部按預設值即可。

**裝完要重開終端機**，不然指令會找不到。

- Windows：從開始選單打開「Anaconda Prompt」
- macOS：打開「終端機」（Terminal）

驗證：

```bash
conda --version
```

有跑出版本號就成功了。

---

## 二、建立這門課的環境

```bash
conda create -n vibecoding python=3.11
conda activate vibecoding
```

`vibecoding` 是環境名稱，可以自己取。**每次要跑第 6、7 章的程式之前，都要先執行 `conda activate vibecoding`。**

怎麼知道有沒有啟動？終端機提示字元前面會出現 `(vibecoding)`。沒看到就是沒啟動，套件一定找不到。

---

## 三、安裝套件

先把這個 repo 抓下來：

```bash
git clone （本 repo 網址）
cd （repo 資料夾名稱）
```

不會用 Git 也沒關係，在 GitHub 頁面上按 **Code → Download ZIP**，解壓縮後用終端機 `cd` 進去就好。

然後裝套件：

```bash
pip install -r requirements.txt
```

驗證：

```bash
python -c "import flask, pandas; print('OK')"
```

印出 `OK` 就成功了。

---

## 四、設定 API 金鑰（第 7 章才需要）

第 6 章不用金鑰，可以先跳過這一段。

1. 到你選用的 LLM 服務申請免費 API 金鑰（各家申請方式見第 7.5 節）
2. 把 `.env.example` 複製一份，改名為 `.env`

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

3. 用文字編輯器打開 `.env`，把金鑰貼在等號後面

```
LLM_API_KEY=你的金鑰貼這裡
```

### 三件不能做的事

- **不要把金鑰貼進 `run.py`**，程式一律從 `.env` 讀
- **不要把 `.env` 上傳到任何地方**，包含交作業、貼截圖、傳給同學
- **不要把金鑰貼進聊天視窗問 AI**

金鑰等於你的帳號密碼。真的外流了，立刻到平台後台撤銷重發，這比什麼都快。

---

## 五、跑起來看看

### 第 6 章：藥局查詢網站

```bash
conda activate vibecoding
cd ch06-data-basics/project-6-5
python init_db.py       # 第一次要跑，把 CSV 匯進資料庫
python run.py
```

打開瀏覽器輸入 `http://127.0.0.1:8051`。

`init_db.py` 只要跑一次。之後重開只需要 `python run.py`。

### 第 7 章：健康對話小幫手

**先把第 6 章關掉**，兩章都用 port 8051。

```bash
conda activate vibecoding
cd ch07-qa-assistant/project-7-2
python init_db.py
python run.py
```

一樣打開 `http://127.0.0.1:8051`。

### 怎麼關掉

在跑程式的終端機視窗按 `Ctrl + C`。

視窗關掉了但程式還占著 port，用這個強制關：

```bash
kill $(lsof -ti:8051)                    # macOS / Linux
```

```powershell
netstat -ano | findstr :8051             # Windows：先查 PID
taskkill /PID <上面查到的數字> /F         # 再關掉
```

---

## 常見安裝問題

| 錯誤訊息 | 原因 | 怎麼處理 |
| --- | --- | --- |
| `conda: command not found` | 沒重開終端機 | 關掉重開；Windows 要用 Anaconda Prompt |
| `ModuleNotFoundError: No module named 'flask'` | 沒啟動環境 | 先 `conda activate vibecoding`，確認提示字元有 `(vibecoding)` |
| `Address already in use` | port 8051 被占住 | 用上面的指令關掉舊的 |
| `Permission denied` | 資料夾權限 | 換一個你有寫入權限的位置，別放在系統資料夾 |
| 網頁打開是空的、查不到資料 | 沒跑 `init_db.py` | 先跑一次 `python init_db.py` |
| CSV 讀進來全是亂碼 | 政府資料常見 Big5 編碼 | `init_db.py` 裡指定 `encoding='big5'` 或 `'cp950'` |
| `KeyError: 'LLM_API_KEY'` | `.env` 沒建立或沒填 | 確認檔名是 `.env`（前面有點），且金鑰已填入 |

### 卡住的時候

Vibe Coding 的精神就是「不會就問 AI」。把**完整的錯誤訊息**貼給 AI，並說明你在做什麼、剛剛打了什麼指令。

問法建議：

```
我在跑一個 Flask 專案，執行 python run.py 之後出現以下錯誤，
請用白話解釋這是什麼意思，以及我該怎麼處理。

（貼上完整錯誤訊息）
```

**貼之前先確認錯誤訊息裡沒有 API 金鑰或個人資料。** 有的話先塗掉。

---

## 不想安裝的替代方案

如果環境真的裝不起來，或你用的是學校公用電腦裝不了東西：

1. **用 Replit**：把 `project-6-5/` 或 `project-7-2/` 整包上傳，Replit 會自動裝套件。缺點是免費方案有使用時數限制。
2. **只做瀏覽器軌**：第 9 章的十個專題有七個不需要本機環境，期末專題仍然做得完。
3. **找同學或助教一起看**：安裝問題通常十分鐘內解得掉，卡在這裡很不划算。

裝不起來不代表你學不會這門課。環境設定是所有工程師都會遇到的麻煩，跟你的理解能力無關。
