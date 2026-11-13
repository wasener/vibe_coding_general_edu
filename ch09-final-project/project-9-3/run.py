"""居家醫療備用藥箱「過期與保存檢核器」：Flask + SQLite.

依 checklist-medicine-cabinet.txt 逐頁開發，本檔案已完成全部 6 個頁面：
    ・首頁／藥箱清單（index.html）－ FR-2、FR-3、FR-4、6-1、6-2、§10
    ・新增／編輯藥品（add-edit.html）－ FR-1、FR-6、6-1
    ・藥品詳情（detail.html）－ FR-2、FR-3、FR-5、6-3
    ・藥品查詢（search.html）－ FR-7、4-4
    ・資料匯入（import.html）－ FR-8、4-3、4-4、4-5
    ・關於／資料來源說明（about.html）－ §8、§10、§11
"""

import csv
import io
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "medicine_cabinet.db"
CSV_DEFAULT_PATH = APP_DIR / "A21030000I-E41001-001.csv"
APP_TITLE = "MedicineCabinet"
APP_SUBTITLE = "居家醫療備用藥箱「過期與保存檢核器」"

app = Flask(__name__)
# 本機單機使用的教學示範專案，不涉及帳號或跨站表單，secret_key 僅用來讓
# flash() 訊息可以運作，不做為正式部署的安全機制。
app.secret_key = "medicine-cabinet-dev-secret"

# ---------------------------------------------------------------------------
# 業務規則（對應 SRS 第 6 節）
# ---------------------------------------------------------------------------

CATEGORIES = ["眼藥水", "內服藥水", "外用藥膏", "其他"]
STATUS_LABELS = ["安全", "即將到期", "已過期", "尚未設定"]

# 6-1　各分類「開封後保存天數」預設值（一般參考經驗值，非醫療標準）
DEFAULT_SHELF_LIFE_DAYS = {
    "眼藥水": 30,
    "內服藥水": 90,
    "外用藥膏": 90,
    "其他": 90,
}

# 6-2　顏色警示規則的顯示樣式
STATUS_STYLE = {
    "green": {"label": "安全", "color": "#00694A", "bg": "#E3F5EC"},
    "yellow": {"label": "即將到期", "color": "#B76E00", "bg": "#FFF3E0"},
    "red": {"label": "已過期", "color": "#BA1A1A", "bg": "#FFDAD6"},
    "gray": {"label": "尚未設定", "color": "#6E7A72", "bg": "#EDEDEC"},
}

# 6-3　廢棄處理指引（種子資料，寫入 disposal_guides 表）
DISPOSAL_GUIDES_SEED = {
    "眼藥水": "不要直接倒入水槽或馬桶，避免污染水源；建議連同容器交由社區藥局、藥物回收點或依當地環保機關公告方式處理。",
    "內服藥水": "不要直接倒入水槽或馬桶，避免污染水源；建議連同容器交由社區藥局、藥物回收點或依當地環保機關公告方式處理。",
    "外用藥膏": "關緊瓶蓋後以一般垃圾丟棄前，建議先確認當地是否有藥物回收管道；仍建議優先送交社區藥局回收。",
    "其他": "無法判斷時，一律建議洽詢附近藥局或社區環保機關，不要自行判斷丟棄方式。",
}

DISCLAIMER_TEXT = "本工具僅協助記錄與提醒，保存期限與廢棄方式請以藥品標示或藥師意見為準。"
DATA_SOURCE_TEXT = (
    "藥品參考資料來源：全民健保藥品給付項目及支付標準（衛福部健保署公開資料）；"
    "有效起日／迄日為健保支付價格生效期間，不代表藥品保存期限。"
)

# 4-3　分類篩選規則的關鍵字（依 SRS 4-3 順序判斷，眼藥水優先於外用藥膏，外用藥膏優先於內服藥水）
FORM_KEYWORDS = {
    "眼藥水": ("點眼", "眼用", "眼"),
    "外用藥膏": ("乳膏", "軟膏", "凝膠", "外用"),
    "內服藥水": ("液劑", "糖漿", "懸液"),
}

# 4-5(2)　匯入時比對資料是否有變動所需的欄位
CSV_REQUIRED_COLUMNS = {
    "藥品代號", "藥品中文名稱", "成分", "劑型", "藥商", "支付價", "有效起日", "有效迄日",
}

# 底部導覽列（(路由, 顯示文字, Material Symbols 圖示名稱)）
NAV_ITEMS = [
    ("/", "首頁", "home"),
    ("/add-edit", "新增藥品", "add_circle"),
    ("/search", "藥品查詢", "search"),
    ("/import", "資料匯入", "upload_file"),
    ("/about", "關於", "info"),
]


@app.context_processor
def inject_globals():
    return {
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "nav_items": NAV_ITEMS,
    }


# ---------------------------------------------------------------------------
# 資料庫（對應 SRS 第 7 節資料模型）
# ---------------------------------------------------------------------------


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(str(DB_PATH))
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def init_db():
    """建立 SRS 第 7 節四張資料表，並寫入必要的種子資料（僅在首次啟動時執行）。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            drug_ref_code TEXT,
            opened_date TEXT,
            shelf_life_days INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS drug_reference (
            drug_code TEXT PRIMARY KEY,
            name_zh TEXT,
            ingredient TEXT,
            form TEXT,
            category_guess TEXT,
            manufacturer TEXT,
            payment_price REAL,
            valid_from TEXT,
            valid_to TEXT,
            status TEXT,
            imported_at TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS disposal_guides (
            category TEXT PRIMARY KEY,
            guide_text TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS import_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imported_at TEXT NOT NULL,
            source_filename TEXT,
            total_rows_in_file INTEGER,
            valid_rows_after_filter INTEGER,
            new_count INTEGER,
            updated_count INTEGER,
            deactivated_count INTEGER
        )
        """
    )
    conn.commit()

    _ensure_disposal_guides_seed(conn)
    _ensure_demo_medicines_seed(conn)
    conn.close()


def _ensure_disposal_guides_seed(conn):
    rows = conn.execute("SELECT COUNT(*) FROM disposal_guides").fetchone()[0]
    if rows:
        return
    conn.executemany(
        "INSERT INTO disposal_guides (category, guide_text) VALUES (?, ?)",
        list(DISPOSAL_GUIDES_SEED.items()),
    )
    conn.commit()


def _ensure_demo_medicines_seed(conn):
    """首次啟動時寫入幾筆示範藥品，方便直接看到綠／黃／紅／灰四種狀態。"""
    rows = conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
    if rows:
        return

    today = date.today()

    def days_ago(n):
        return (today - timedelta(days=n)).isoformat()

    demo_rows = [
        ("普拿疼糖漿（示範資料）", "內服藥水", days_ago(40), 90, "小孩發燒備用"),
        ("生理食鹽水點眼液（示範資料）", "眼藥水", days_ago(25), 30, "隱形眼鏡族常備"),
        ("樂敷消炎軟膏（示範資料）", "外用藥膏", days_ago(120), 90, "已過期，待清理"),
        ("小兒退燒藥水（示範資料）", "內服藥水", days_ago(100), 90, ""),
        ("人工淚液（示範資料）", "眼藥水", days_ago(10), 30, ""),
        ("優碘外用液（示範資料）", "其他", None, 90, "尚未輸入開封日期"),
    ]
    ts = now_text()
    conn.executemany(
        """
        INSERT INTO medicines
            (name, category, drug_ref_code, opened_date, shelf_life_days, note, created_at, updated_at)
        VALUES (?, ?, NULL, ?, ?, ?, ?, ?)
        """,
        [(name, cat, opened, shelf, note, ts, ts) for name, cat, opened, shelf, note in demo_rows],
    )
    conn.commit()


def fetch_last_import_summary(conn):
    row = conn.execute("SELECT * FROM import_logs ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else None


def fetch_last_import_time(conn):
    summary = fetch_last_import_summary(conn)
    return summary["imported_at"] if summary else None


def fetch_medicines(conn):
    rows = conn.execute(
        """
        SELECT id, name, category, drug_ref_code, opened_date, shelf_life_days, note
        FROM medicines
        ORDER BY id DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def fetch_medicine(conn, med_id):
    row = conn.execute("SELECT * FROM medicines WHERE id = ?", (med_id,)).fetchone()
    return dict(row) if row else None


def insert_medicine(conn, name, category, drug_ref_code, opened_date, shelf_life_days, note):
    ts = now_text()
    cur = conn.execute(
        """
        INSERT INTO medicines
            (name, category, drug_ref_code, opened_date, shelf_life_days, note, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (name, category, drug_ref_code, opened_date, shelf_life_days, note, ts, ts),
    )
    conn.commit()
    return cur.lastrowid


def update_medicine(conn, med_id, name, category, drug_ref_code, opened_date, shelf_life_days, note):
    conn.execute(
        """
        UPDATE medicines
        SET name = ?, category = ?, drug_ref_code = ?, opened_date = ?,
            shelf_life_days = ?, note = ?, updated_at = ?
        WHERE id = ?
        """,
        (name, category, drug_ref_code, opened_date, shelf_life_days, note, now_text(), med_id),
    )
    conn.commit()


def delete_medicine(conn, med_id):
    conn.execute("DELETE FROM medicines WHERE id = ?", (med_id,))
    conn.commit()


def query_drug_reference(conn, keyword, limit=50):
    """FR-6／FR-7 共用的查詢邏輯：只查目前有效（4-4 已在匯入時篩選去重）的資料。"""
    keyword = (keyword or "").strip()
    sql = """
        SELECT drug_code, name_zh, ingredient, form, category_guess, manufacturer,
               payment_price, valid_from, valid_to
        FROM drug_reference
        WHERE status = '正常'
    """
    params = []
    if keyword:
        sql += " AND (name_zh LIKE ? OR ingredient LIKE ? OR manufacturer LIKE ?)"
        like = f"%{keyword}%"
        params += [like, like, like]
    sql += " ORDER BY name_zh LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [_build_drug_reference_view(dict(r)) for r in rows]


def _build_drug_reference_view(row):
    row["valid_from_display"] = format_roc_date(row.get("valid_from"))
    row["valid_to_display"] = format_roc_date(row.get("valid_to"))
    price = row.get("payment_price")
    row["payment_price_display"] = f"{price:.2f}" if price is not None else "未提供"
    return row


# ---------------------------------------------------------------------------
# 業務邏輯（對應 SRS FR-2、FR-3、6-1、6-2）
# ---------------------------------------------------------------------------


def calc_expiry(opened_date_str, shelf_life_days):
    """開封後到期日 = 開封日期 + 開封後保存天數（6-1／FR-2）。"""
    if not opened_date_str:
        return None
    opened = date.fromisoformat(opened_date_str)
    return opened + timedelta(days=shelf_life_days)


def calc_status(expiry):
    """依 6-2 規則，回傳 green／yellow／red／gray 四種狀態代碼之一。"""
    if expiry is None:
        return "gray"
    remaining = (expiry - date.today()).days
    if remaining < 0:
        return "red"
    if remaining < 14:
        return "yellow"
    return "green"


def build_medicine_view(row):
    """把一筆藥品資料補上到期日、剩餘天數、狀態、畫面顯示字串，供樣板直接使用。"""
    expiry = calc_expiry(row["opened_date"], row["shelf_life_days"])
    status = calc_status(expiry)
    remaining = (expiry - date.today()).days if expiry else None

    if remaining is None:
        remaining_display = "—"
    elif remaining < 0:
        remaining_display = f"已過期 {abs(remaining)} 天"
    else:
        remaining_display = f"剩餘 {remaining} 天"

    return {
        **row,
        "expiry_date": expiry,
        "remaining_days": remaining,
        "status": status,
        "style": STATUS_STYLE[status],
        "opened_display": row["opened_date"] or "未設定",
        "expiry_display": expiry.isoformat() if expiry else "—",
        "remaining_display": remaining_display,
    }


def apply_filters(medicine_views, category, status, keyword):
    """FR-4　分類搜尋與篩選：分類、狀態、關鍵字，三者可單獨或合併使用。"""
    result = medicine_views
    if category and category != "全部":
        result = [m for m in result if m["category"] == category]
    if status and status != "全部":
        result = [m for m in result if m["style"]["label"] == status]
    if keyword:
        kw = keyword.strip()
        if kw:
            result = [m for m in result if kw in m["name"]]
    return result


# ---------------------------------------------------------------------------
# 開放資料匯入（對應 SRS 4-3、4-4、4-5、FR-8）
# ---------------------------------------------------------------------------


def classify_form(form_text):
    """4-3　依「劑型」欄位關鍵字判斷分類，眼藥水／外用藥膏／內服藥水的檢查順序即為優先順序。"""
    text = form_text or ""
    if any(k in text for k in FORM_KEYWORDS["眼藥水"]):
        return "眼藥水"
    if any(k in text for k in FORM_KEYWORDS["外用藥膏"]) and "注射" not in text:
        return "外用藥膏"
    if any(k in text for k in FORM_KEYWORDS["內服藥水"]) and "注射" not in text and "眼" not in text:
        return "內服藥水"
    return None


def roc_to_iso(roc_text):
    """民國年 YYYMMDD（7 碼）轉西元 ISO 日期字串，格式不符時回傳 None。"""
    if not roc_text or len(roc_text) != 7 or not roc_text.isdigit():
        return None
    year = int(roc_text[:3]) + 1911
    month, day = roc_text[3:5], roc_text[5:7]
    try:
        return date(year, int(month), int(day)).isoformat()
    except ValueError:
        return None


def format_roc_date(roc_text):
    if roc_text == "9991231":
        return "長期有效"
    return roc_to_iso(roc_text) or (roc_text or "—")


def is_currently_valid(valid_to_raw):
    """4-4(1)　有效迄日 ≧ 今天，或有效迄日 ＝ 9991231（目前仍生效、尚無結束日期）。"""
    if valid_to_raw == "9991231":
        return True
    iso = roc_to_iso(valid_to_raw)
    if not iso:
        return False
    return date.fromisoformat(iso) >= date.today()


def run_csv_import(conn, file_obj, source_filename):
    """依 4-3 分類篩選 → 4-4 有效性與去重 → 4-5 新增／更新／下架，寫入 drug_reference。"""
    reader = csv.DictReader(file_obj)
    fieldnames = set(reader.fieldnames or [])
    missing = CSV_REQUIRED_COLUMNS - fieldnames
    if missing:
        raise ValueError(f"CSV 檔案缺少必要欄位：{'、'.join(sorted(missing))}")

    total_rows = 0
    best = {}  # drug_code -> (valid_from, data_dict)

    for row in reader:
        total_rows += 1
        category_guess = classify_form(row.get("劑型", ""))
        if not category_guess:
            continue
        valid_to = (row.get("有效迄日") or "").strip()
        if not is_currently_valid(valid_to):
            continue
        code = (row.get("藥品代號") or "").strip()
        if not code:
            continue
        valid_from = (row.get("有效起日") or "").strip()

        if code in best and valid_from <= best[code][0]:
            continue  # 4-4(2)　同一藥品代號僅保留有效起日最新的一筆

        try:
            price = float(row.get("支付價") or 0)
        except ValueError:
            price = None

        best[code] = (
            valid_from,
            {
                "drug_code": code,
                "name_zh": row.get("藥品中文名稱", ""),
                "ingredient": row.get("成分", ""),
                "form": row.get("劑型", ""),
                "category_guess": category_guess,
                "manufacturer": row.get("藥商", ""),
                "payment_price": price,
                "valid_from": valid_from,
                "valid_to": valid_to,
            },
        )

    existing_codes = {
        r["drug_code"]
        for r in conn.execute("SELECT drug_code FROM drug_reference WHERE status = '正常'")
    }
    new_codes = set(best.keys())
    to_add = new_codes - existing_codes
    to_update = new_codes & existing_codes
    to_deactivate = existing_codes - new_codes

    ts = now_text()
    upsert_rows = [
        (
            data["drug_code"], data["name_zh"], data["ingredient"], data["form"],
            data["category_guess"], data["manufacturer"], data["payment_price"],
            data["valid_from"], data["valid_to"], "正常", ts,
        )
        for _, data in best.values()
    ]
    conn.executemany(
        """
        INSERT INTO drug_reference
            (drug_code, name_zh, ingredient, form, category_guess, manufacturer,
             payment_price, valid_from, valid_to, status, imported_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(drug_code) DO UPDATE SET
            name_zh = excluded.name_zh,
            ingredient = excluded.ingredient,
            form = excluded.form,
            category_guess = excluded.category_guess,
            manufacturer = excluded.manufacturer,
            payment_price = excluded.payment_price,
            valid_from = excluded.valid_from,
            valid_to = excluded.valid_to,
            status = '正常',
            imported_at = excluded.imported_at
        """,
        upsert_rows,
    )
    if to_deactivate:
        conn.executemany(
            "UPDATE drug_reference SET status = '已停用', imported_at = ? WHERE drug_code = ?",
            [(ts, code) for code in to_deactivate],
        )

    conn.execute(
        """
        INSERT INTO import_logs
            (imported_at, source_filename, total_rows_in_file, valid_rows_after_filter,
             new_count, updated_count, deactivated_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (ts, source_filename, total_rows, len(best), len(to_add), len(to_update), len(to_deactivate)),
    )
    conn.commit()

    return {
        "source_filename": source_filename,
        "total_rows_in_file": total_rows,
        "valid_rows_after_filter": len(best),
        "new_count": len(to_add),
        "updated_count": len(to_update),
        "deactivated_count": len(to_deactivate),
    }


# ---------------------------------------------------------------------------
# 表單處理共用邏輯（對應 SRS FR-1）
# ---------------------------------------------------------------------------


def _parse_medicine_form(form):
    name = form.get("name", "").strip()
    category = form.get("category", "")
    opened_date_raw = form.get("opened_date", "").strip()
    shelf_life_raw = form.get("shelf_life_days", "").strip()
    note = form.get("note", "").strip()
    drug_ref_code = form.get("drug_ref_code", "").strip() or None

    errors = []
    if not name:
        errors.append("請輸入藥品名稱。")
    if category not in CATEGORIES:
        errors.append("請選擇分類。")

    opened_date_value = opened_date_raw or None
    if opened_date_value:
        try:
            date.fromisoformat(opened_date_value)
        except ValueError:
            errors.append("開封日期格式不正確。")
            opened_date_value = None

    shelf_life_days = None
    if not shelf_life_raw:
        errors.append("請輸入開封後保存天數。")
    else:
        try:
            shelf_life_days = int(shelf_life_raw)
            if shelf_life_days <= 0:
                errors.append("開封後保存天數必須是正整數。")
        except ValueError:
            errors.append("開封後保存天數必須是正整數。")

    values = {
        "name": name,
        "category": category,
        "drug_ref_code": drug_ref_code,
        "opened_date": opened_date_value,
        "shelf_life_days": shelf_life_days,
        "note": note,
    }
    raw_values = {
        "name": name,
        "category": category,
        "drug_ref_code": drug_ref_code or "",
        "opened_date": opened_date_raw,
        "shelf_life_days": shelf_life_raw,
        "note": note,
    }
    return errors, values, raw_values


def _medicine_form_context(conn, med=None, errors=None, form_values=None):
    prefill_code = request.args.get("prefill_code", "").strip()
    prefill = None
    if prefill_code and not med:
        row = conn.execute(
            "SELECT * FROM drug_reference WHERE drug_code = ?", (prefill_code,)
        ).fetchone()
        prefill = _build_drug_reference_view(dict(row)) if row else None

    search_keyword = request.args.get("q", "").strip()
    search_results = query_drug_reference(conn, search_keyword, limit=10) if search_keyword else []

    return {
        "med": med,
        "errors": errors or [],
        "form_values": form_values,
        "categories": CATEGORIES,
        "default_shelf_life_days": DEFAULT_SHELF_LIFE_DAYS,
        "today_iso": date.today().isoformat(),
        "prefill": prefill,
        "search_keyword": search_keyword,
        "search_results": search_results,
    }


# ---------------------------------------------------------------------------
# 路由：首頁／藥箱清單（index.html）－ FR-2、FR-3、FR-4、6-1、6-2、§10
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    conn = get_db()
    category = request.args.get("category", "全部")
    status = request.args.get("status", "全部")
    keyword = request.args.get("keyword", "").strip()

    all_views = [build_medicine_view(r) for r in fetch_medicines(conn)]

    counts = {code: 0 for code in STATUS_STYLE}
    for m in all_views:
        counts[m["status"]] += 1

    summary = [
        ("全部藥品", len(all_views), "#00694A"),
        ("即將到期", counts["yellow"], STATUS_STYLE["yellow"]["color"]),
        ("已過期", counts["red"], STATUS_STYLE["red"]["color"]),
        ("尚未設定開封日", counts["gray"], STATUS_STYLE["gray"]["color"]),
    ]

    medicines = apply_filters(all_views, category, status, keyword)

    return render_template(
        "index.html",
        disclaimer_text=DISCLAIMER_TEXT,
        data_source_text=DATA_SOURCE_TEXT,
        last_import=fetch_last_import_time(conn),
        categories=CATEGORIES,
        statuses=STATUS_LABELS,
        category=category,
        status=status,
        keyword=keyword,
        summary=summary,
        medicines=medicines,
    )


# ---------------------------------------------------------------------------
# 路由：新增／編輯藥品（add-edit.html）－ FR-1、FR-6、6-1
# ---------------------------------------------------------------------------


@app.route("/add-edit", methods=["GET", "POST"])
def add_edit_page():
    conn = get_db()
    if request.method == "POST":
        errors, values, raw_values = _parse_medicine_form(request.form)
        if errors:
            ctx = _medicine_form_context(conn)
            ctx.update(errors=errors, form_values=raw_values)
            return render_template("add-edit.html", **ctx), 400
        med_id = insert_medicine(conn, **values)
        flash(f"已新增藥品「{values['name']}」。", "success")
        return redirect(url_for("detail_page", med_id=med_id))

    ctx = _medicine_form_context(conn)
    return render_template("add-edit.html", **ctx)


@app.route("/add-edit/<int:med_id>", methods=["GET", "POST"])
def edit_medicine_page(med_id):
    conn = get_db()
    med = fetch_medicine(conn, med_id)
    if not med:
        abort(404)

    if request.method == "POST":
        errors, values, raw_values = _parse_medicine_form(request.form)
        if errors:
            ctx = _medicine_form_context(conn, med=med)
            ctx.update(errors=errors, form_values=raw_values)
            return render_template("add-edit.html", **ctx), 400
        update_medicine(conn, med_id, **values)
        flash(f"已更新藥品「{values['name']}」。", "success")
        return redirect(url_for("detail_page", med_id=med_id))

    ctx = _medicine_form_context(conn, med=med)
    return render_template("add-edit.html", **ctx)


@app.route("/medicines/<int:med_id>/delete", methods=["POST"])
def delete_medicine_page(med_id):
    conn = get_db()
    med = fetch_medicine(conn, med_id)
    if med:
        delete_medicine(conn, med_id)
        flash(f"已刪除藥品「{med['name']}」。", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# 路由：藥品詳情（detail.html）－ FR-2、FR-3、FR-5、6-3
# ---------------------------------------------------------------------------


@app.route("/detail/<int:med_id>")
def detail_page(med_id):
    conn = get_db()
    med = fetch_medicine(conn, med_id)
    if not med:
        abort(404)
    view = build_medicine_view(med)
    guide_row = conn.execute(
        "SELECT guide_text FROM disposal_guides WHERE category = ?", (med["category"],)
    ).fetchone()
    guide_text = guide_row["guide_text"] if guide_row else None
    return render_template(
        "detail.html", med=view, guide_text=guide_text, disclaimer_text=DISCLAIMER_TEXT
    )


# ---------------------------------------------------------------------------
# 路由：藥品查詢（search.html）－ FR-7、4-4
# ---------------------------------------------------------------------------


@app.route("/search")
def search_page():
    conn = get_db()
    keyword = request.args.get("keyword", "").strip()
    has_reference_data = conn.execute("SELECT COUNT(*) FROM drug_reference").fetchone()[0] > 0
    results = query_drug_reference(conn, keyword, limit=60) if keyword else []
    return render_template(
        "search.html",
        keyword=keyword,
        results=results,
        has_reference_data=has_reference_data,
    )


# ---------------------------------------------------------------------------
# 路由：資料匯入（import.html）－ FR-8、4-3、4-4、4-5
# ---------------------------------------------------------------------------


@app.route("/import", methods=["GET", "POST"])
def import_page():
    conn = get_db()
    if request.method == "POST":
        uploaded = request.files.get("csv_file")
        stream = None
        try:
            if uploaded and uploaded.filename:
                stream = io.TextIOWrapper(uploaded.stream, encoding="utf-8-sig", newline="")
                source_name = uploaded.filename
            elif CSV_DEFAULT_PATH.exists():
                stream = open(CSV_DEFAULT_PATH, encoding="utf-8-sig", newline="")
                source_name = CSV_DEFAULT_PATH.name
            else:
                flash("找不到可匯入的檔案，請上傳健保藥品開放資料 CSV。", "error")
                return redirect(url_for("import_page"))

            summary = run_csv_import(conn, stream, source_name)
            flash(
                "匯入完成：讀取 {total} 筆，篩選後有效 {valid} 筆（新增 {new}、更新 {upd}、下架 {deact}）。".format(
                    total=summary["total_rows_in_file"],
                    valid=summary["valid_rows_after_filter"],
                    new=summary["new_count"],
                    upd=summary["updated_count"],
                    deact=summary["deactivated_count"],
                ),
                "success",
            )
        except ValueError as exc:
            flash(f"匯入失敗：{exc}", "error")
        finally:
            if stream is not None:
                stream.close()
        return redirect(url_for("import_page"))

    return render_template(
        "import.html",
        last_summary=fetch_last_import_summary(conn),
        default_filename=CSV_DEFAULT_PATH.name,
        default_file_available=CSV_DEFAULT_PATH.exists(),
    )


# ---------------------------------------------------------------------------
# 路由：關於／資料來源說明（about.html）－ §8、§10、§11
# ---------------------------------------------------------------------------


@app.route("/about")
def about_page():
    conn = get_db()
    return render_template(
        "about.html",
        disclaimer_text=DISCLAIMER_TEXT,
        data_source_text=DATA_SOURCE_TEXT,
        last_import=fetch_last_import_time(conn),
        disposal_guides=DISPOSAL_GUIDES_SEED,
    )


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8051, debug=True)
