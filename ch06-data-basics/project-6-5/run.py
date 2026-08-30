"""健保特約醫事機構－藥局查詢：Flask + SQLite。

資料來源：A21030000I-D21005-001.csv（全民健保特約醫事機構－藥局，公開資料）。
"""

import csv
import io
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "pharmacies.db"
CSV_DEFAULT_PATH = APP_DIR / "A21030000I-D21005-001.csv"
PER_PAGE = 20

app = Flask(__name__)
app.secret_key = "pharmacy-search-dev-secret"

# 縣市別代碼 -> 縣市名稱（依實際資料檔核對過的對照表），依慣用地理順序排列供下拉選單使用
COUNTY_ORDER = [
    ("63000", "臺北市"), ("65000", "新北市"), ("10017", "基隆市"), ("68000", "桃園市"),
    ("10018", "新竹市"), ("10004", "新竹縣"), ("10005", "苗栗縣"), ("66000", "臺中市"),
    ("10007", "彰化縣"), ("10008", "南投縣"), ("10009", "雲林縣"), ("10020", "嘉義市"),
    ("10010", "嘉義縣"), ("10021", "臺南市"), ("64000", "高雄市"), ("10013", "屏東縣"),
    ("10002", "宜蘭縣"), ("10015", "花蓮縣"), ("10014", "臺東縣"), ("10016", "澎湖縣"),
    ("09020", "金門縣"),
]
COUNTY_NAME_BY_CODE = dict(COUNTY_ORDER)

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
TIME_SLOTS = ["上午", "下午", "晚上"]

CSV_REQUIRED_COLUMNS = {
    "醫事機構代碼", "醫事機構名稱", "醫事機構種類", "電話", "地址", "分區業務組",
    "特約類別", "服務項目", "診療科別", "終止合約或歇業日期", "固定看診時段",
    "備註", "縣市別代碼", "合約起日",
}


# ---------------------------------------------------------------------------
# 資料庫
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


def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pharmacies (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            kind TEXT,
            phone TEXT,
            address TEXT,
            business_group TEXT,
            contract_type TEXT,
            service_items TEXT,
            departments TEXT,
            end_date TEXT,
            clinic_hours TEXT,
            note TEXT,
            county_code TEXT,
            county_name TEXT,
            contract_start TEXT
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
            new_count INTEGER,
            updated_count INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fetch_last_import_summary(conn):
    row = conn.execute("SELECT * FROM import_logs ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else None


def fetch_pharmacy_count(conn):
    return conn.execute("SELECT COUNT(*) FROM pharmacies").fetchone()[0]


# ---------------------------------------------------------------------------
# 匯入（醫事機構代碼為主鍵，重複匯入會更新既有資料）
# ---------------------------------------------------------------------------


def run_csv_import(conn, file_obj, source_filename):
    reader = csv.DictReader(file_obj)
    fieldnames = set(reader.fieldnames or [])
    missing = CSV_REQUIRED_COLUMNS - fieldnames
    if missing:
        raise ValueError(f"CSV 檔案缺少必要欄位：{'、'.join(sorted(missing))}")

    total_rows = 0
    upsert_rows = []
    codes_in_file = set()

    for row in reader:
        total_rows += 1
        code = (row.get("醫事機構代碼") or "").strip()
        if not code:
            continue
        codes_in_file.add(code)
        county_code = (row.get("縣市別代碼") or "").strip()
        upsert_rows.append((
            code,
            row.get("醫事機構名稱", ""),
            row.get("醫事機構種類", ""),
            row.get("電話", ""),
            row.get("地址", ""),
            row.get("分區業務組", ""),
            row.get("特約類別", ""),
            row.get("服務項目", ""),
            row.get("診療科別", ""),
            row.get("終止合約或歇業日期", ""),
            row.get("固定看診時段", ""),
            row.get("備註", ""),
            county_code,
            COUNTY_NAME_BY_CODE.get(county_code, ""),
            row.get("合約起日", ""),
        ))

    existing_codes = {r[0] for r in conn.execute("SELECT code FROM pharmacies")}
    new_count = len(codes_in_file - existing_codes)
    updated_count = len(codes_in_file & existing_codes)

    conn.executemany(
        """
        INSERT INTO pharmacies
            (code, name, kind, phone, address, business_group, contract_type,
             service_items, departments, end_date, clinic_hours, note,
             county_code, county_name, contract_start)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(code) DO UPDATE SET
            name = excluded.name,
            kind = excluded.kind,
            phone = excluded.phone,
            address = excluded.address,
            business_group = excluded.business_group,
            contract_type = excluded.contract_type,
            service_items = excluded.service_items,
            departments = excluded.departments,
            end_date = excluded.end_date,
            clinic_hours = excluded.clinic_hours,
            note = excluded.note,
            county_code = excluded.county_code,
            county_name = excluded.county_name,
            contract_start = excluded.contract_start
        """,
        upsert_rows,
    )
    conn.execute(
        """
        INSERT INTO import_logs (imported_at, source_filename, total_rows_in_file, new_count, updated_count)
        VALUES (?, ?, ?, ?, ?)
        """,
        (now_text(), source_filename, total_rows, new_count, updated_count),
    )
    conn.commit()

    return {
        "total_rows_in_file": total_rows,
        "new_count": new_count,
        "updated_count": updated_count,
    }


# ---------------------------------------------------------------------------
# 查詢（名稱、所在縣市、看診時段）＋分頁
# ---------------------------------------------------------------------------


def search_pharmacies(conn, name, county_code, weekday, time_slot, page):
    where = []
    params = []

    if name:
        where.append("name LIKE ?")
        params.append(f"%{name}%")
    if county_code:
        where.append("county_code = ?")
        params.append(county_code)
    if weekday and time_slot:
        where.append("clinic_hours LIKE ?")
        params.append(f"%{weekday}{time_slot}看診%")

    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    total = conn.execute(
        f"SELECT COUNT(*) FROM pharmacies {where_clause}", params
    ).fetchone()[0]

    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * PER_PAGE

    rows = conn.execute(
        f"""
        SELECT code, name, kind, phone, address, county_name, clinic_hours, departments
        FROM pharmacies
        {where_clause}
        ORDER BY county_code, name
        LIMIT ? OFFSET ?
        """,
        [*params, PER_PAGE, offset],
    ).fetchall()

    return {
        "rows": rows,
        "total": total,
        "page": page,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    conn = get_db()
    name = request.args.get("name", "").strip()
    county_code = request.args.get("county", "").strip()
    weekday = request.args.get("weekday", "").strip()
    time_slot = request.args.get("time_slot", "").strip()
    try:
        page = int(request.args.get("page", "1"))
    except ValueError:
        page = 1

    result = search_pharmacies(conn, name, county_code, weekday, time_slot, page)

    query_params = {}
    if name:
        query_params["name"] = name
    if county_code:
        query_params["county"] = county_code
    if weekday:
        query_params["weekday"] = weekday
    if time_slot:
        query_params["time_slot"] = time_slot

    return render_template(
        "index.html",
        result=result,
        name=name,
        county_code=county_code,
        weekday=weekday,
        time_slot=time_slot,
        counties=COUNTY_ORDER,
        weekdays=WEEKDAYS,
        time_slots=TIME_SLOTS,
        query_params=query_params,
        pharmacy_count=fetch_pharmacy_count(conn),
        last_import=fetch_last_import_summary(conn),
        default_filename=CSV_DEFAULT_PATH.name,
        default_file_available=CSV_DEFAULT_PATH.exists(),
    )


@app.route("/import", methods=["POST"])
def import_page():
    conn = get_db()
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
            flash("找不到可匯入的檔案，請上傳藥局開放資料 CSV。", "error")
            return redirect(url_for("index"))

        summary = run_csv_import(conn, stream, source_name)
        flash(
            "匯入完成：讀取 {total} 筆（新增 {new}、更新 {upd}）。".format(
                total=summary["total_rows_in_file"],
                new=summary["new_count"],
                upd=summary["updated_count"],
            ),
            "success",
        )
    except ValueError as exc:
        flash(f"匯入失敗：{exc}", "error")
    finally:
        if stream is not None:
            stream.close()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8051, debug=True)
