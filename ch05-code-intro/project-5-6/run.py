"""血壓紀錄小幫手：Flask + SQLite 版本。"""

import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "blood_pressure.db"

SYS_MIN, SYS_MAX = 60, 260
DIA_MIN, DIA_MAX = 30, 160
PULSE_MIN, PULSE_MAX = 30, 220
DEFAULT_START = date(2000, 1, 1)

# 血壓分類的四個等級，數字越大代表越嚴重；用來決定套色與排序。
CATEGORY_ORDER = ["normal", "elevated", "stage1", "stage2"]
CATEGORY_LABELS = {
    "normal": "正常血壓",
    "elevated": "血壓偏高",
    "stage1": "高血壓一期",
    "stage2": "高血壓二期",
}
CATEGORY_SEVERITY = {"normal": 0, "elevated": 1, "stage1": 2, "stage2": 3}
# 對照衛福部／美國心臟學會慣用的分類方式：一期／二期只要收縮壓「或」舒張壓
# 其中一項達標就算數；血壓偏高則要收縮壓達標、且舒張壓仍在正常範圍，兩者都要成立。
CATEGORY_MATCH_MODE = {"elevated": "and", "stage1": "or", "stage2": "or"}
DEFAULT_THRESHOLDS = {
    "normal": (None, 119, None, 79),
    "elevated": (120, 129, None, 79),
    "stage1": (130, 139, 80, 90),
    "stage2": (140, None, 90, None),
}

app = Flask(__name__)
app.secret_key = "blood-pressure-dev-secret"


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
        CREATE TABLE IF NOT EXISTS blood_pressure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measure_date TEXT NOT NULL,
            measure_time TEXT NOT NULL,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            pulse INTEGER,
            note TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bp_thresholds (
            category TEXT PRIMARY KEY,
            sys_min INTEGER,
            sys_max INTEGER,
            dia_min INTEGER,
            dia_max INTEGER
        )
        """
    )
    existing = {row[0] for row in conn.execute("SELECT category FROM bp_thresholds")}
    for category in CATEGORY_ORDER:
        if category not in existing:
            sys_min, sys_max, dia_min, dia_max = DEFAULT_THRESHOLDS[category]
            conn.execute(
                "INSERT INTO bp_thresholds (category, sys_min, sys_max, dia_min, dia_max) VALUES (?, ?, ?, ?, ?)",
                (category, sys_min, sys_max, dia_min, dia_max),
            )
    conn.commit()
    conn.close()


def insert_record(measure_date, measure_time, systolic, diastolic, pulse, note):
    conn = get_db()
    conn.execute(
        """
        INSERT INTO blood_pressure (measure_date, measure_time, systolic, diastolic, pulse, note)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (measure_date, measure_time, systolic, diastolic, pulse, note),
    )
    conn.commit()


def delete_record(record_id):
    conn = get_db()
    conn.execute("DELETE FROM blood_pressure WHERE id = ?", (record_id,))
    conn.commit()


def query_records(start_date, end_date, sys_min, sys_max, dia_min, dia_max):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT id, measure_date, measure_time, systolic, diastolic, pulse, note
        FROM blood_pressure
        WHERE measure_date BETWEEN ? AND ?
          AND systolic BETWEEN ? AND ?
          AND diastolic BETWEEN ? AND ?
        ORDER BY measure_date DESC, measure_time DESC
        """,
        (str(start_date), str(end_date), sys_min, sys_max, dia_min, dia_max),
    ).fetchall()
    return rows


# ---------------------------------------------------------------------------
# 血壓標準（設定值的讀取／寫入／分類判斷）
# ---------------------------------------------------------------------------


def get_thresholds():
    conn = get_db()
    rows = conn.execute("SELECT * FROM bp_thresholds").fetchall()
    return {row["category"]: dict(row) for row in rows}


def save_thresholds(values):
    conn = get_db()
    for category, (sys_min, sys_max, dia_min, dia_max) in values.items():
        conn.execute(
            """
            UPDATE bp_thresholds
            SET sys_min = ?, sys_max = ?, dia_min = ?, dia_max = ?
            WHERE category = ?
            """,
            (sys_min, sys_max, dia_min, dia_max, category),
        )
    conn.commit()


def reset_thresholds():
    save_thresholds(DEFAULT_THRESHOLDS)


def _in_range(value, lo, hi):
    if value is None:
        return False
    if lo is not None and value < lo:
        return False
    if hi is not None and value > hi:
        return False
    return True


def classify_bp(systolic, diastolic, thresholds):
    """依照設定值判斷血壓分類，由最嚴重的等級開始比對，比對不到就是正常血壓。"""
    for category in ("stage2", "stage1", "elevated"):
        t = thresholds[category]
        sys_hit = _in_range(systolic, t["sys_min"], t["sys_max"])
        dia_hit = _in_range(diastolic, t["dia_min"], t["dia_max"])
        matched = (sys_hit or dia_hit) if CATEGORY_MATCH_MODE[category] == "or" else (sys_hit and dia_hit)
        if matched:
            return category
    return "normal"


# ---------------------------------------------------------------------------
# 路由：新增紀錄
# ---------------------------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
def add_page():
    errors = []

    if request.method == "POST":
        measure_date = request.form.get("measure_date", "").strip()
        measure_time = request.form.get("measure_time", "").strip()
        systolic_raw = request.form.get("systolic", "").strip()
        diastolic_raw = request.form.get("diastolic", "").strip()
        pulse_raw = request.form.get("pulse", "").strip()
        note = request.form.get("note", "").strip()

        if not measure_date:
            errors.append("請選擇量測日期。")
        if not measure_time:
            errors.append("請選擇量測時間。")

        systolic = diastolic = pulse = None
        try:
            systolic = int(systolic_raw)
            if not (SYS_MIN <= systolic <= SYS_MAX):
                errors.append(f"收縮壓必須介於 {SYS_MIN}～{SYS_MAX} 之間。")
        except ValueError:
            errors.append("收縮壓必須是數字。")
        try:
            diastolic = int(diastolic_raw)
            if not (DIA_MIN <= diastolic <= DIA_MAX):
                errors.append(f"舒張壓必須介於 {DIA_MIN}～{DIA_MAX} 之間。")
        except ValueError:
            errors.append("舒張壓必須是數字。")
        if pulse_raw:
            try:
                pulse = int(pulse_raw)
                if not (PULSE_MIN <= pulse <= PULSE_MAX):
                    errors.append(f"脈搏必須介於 {PULSE_MIN}～{PULSE_MAX} 之間。")
            except ValueError:
                errors.append("脈搏必須是數字。")

        if not errors:
            insert_record(measure_date, measure_time, systolic, diastolic, pulse, note)
            flash("已新增一筆血壓紀錄！", "success")
            return redirect(url_for("add_page"))

    return render_template(
        "add.html",
        errors=errors,
        today=date.today().isoformat(),
        now_time=datetime.now().strftime("%H:%M"),
        sys_min=SYS_MIN, sys_max=SYS_MAX,
        dia_min=DIA_MIN, dia_max=DIA_MAX,
        pulse_min=PULSE_MIN, pulse_max=PULSE_MAX,
    )


# ---------------------------------------------------------------------------
# 路由：歷史紀錄（查詢＋刪除）
# ---------------------------------------------------------------------------


def _parse_filters(args):
    def parse_int(name, default, lo, hi):
        raw = args.get(name, "").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            return default
        return max(lo, min(hi, value))

    start_raw = args.get("start_date", "").strip()
    end_raw = args.get("end_date", "").strip()
    try:
        start_date = date.fromisoformat(start_raw) if start_raw else DEFAULT_START
    except ValueError:
        start_date = DEFAULT_START
    try:
        end_date = date.fromisoformat(end_raw) if end_raw else date.today()
    except ValueError:
        end_date = date.today()

    return {
        "start_date": start_date,
        "end_date": end_date,
        "sys_max": parse_int("sys_max", SYS_MAX, SYS_MIN, SYS_MAX),
        "sys_min": parse_int("sys_min", SYS_MIN, SYS_MIN, SYS_MAX),
        "dia_max": parse_int("dia_max", DIA_MAX, DIA_MIN, DIA_MAX),
        "dia_min": parse_int("dia_min", DIA_MIN, DIA_MIN, DIA_MAX),
    }


@app.route("/history")
def history_page():
    f = _parse_filters(request.args)

    warning = None
    records = []
    if f["start_date"] > f["end_date"]:
        warning = "起始日期不能晚於結束日期，請重新選擇查詢範圍。"
    elif f["sys_min"] > f["sys_max"]:
        warning = "最低收縮壓不能大於最高收縮壓，請重新輸入。"
    elif f["dia_min"] > f["dia_max"]:
        warning = "最低舒張壓不能大於最高舒張壓，請重新輸入。"
    else:
        records = query_records(
            f["start_date"], f["end_date"],
            f["sys_min"], f["sys_max"],
            f["dia_min"], f["dia_max"],
        )

    thresholds = get_thresholds()
    rows = []
    for r in records:
        category = classify_bp(r["systolic"], r["diastolic"], thresholds)
        rows.append({
            "record": r,
            "category": category,
            "category_label": CATEGORY_LABELS[category],
        })

    return render_template(
        "history.html",
        filters=f,
        warning=warning,
        rows=rows,
        sys_min=SYS_MIN, sys_max=SYS_MAX,
        dia_min=DIA_MIN, dia_max=DIA_MAX,
        default_start=DEFAULT_START.isoformat(),
        today=date.today().isoformat(),
        query_string=request.query_string.decode(),
    )


@app.route("/history/<int:record_id>/delete", methods=["POST"])
def delete_page(record_id):
    delete_record(record_id)
    query_string = request.form.get("query_string", "")
    target = url_for("history_page")
    if query_string:
        target = f"{target}?{query_string}"
    return redirect(target)


# ---------------------------------------------------------------------------
# 路由：血壓標準設定
# ---------------------------------------------------------------------------


@app.route("/thresholds", methods=["GET", "POST"])
def thresholds_page():
    errors = []

    if request.method == "POST":
        if request.form.get("action") == "reset":
            reset_thresholds()
            flash("已還原為預設的血壓標準。", "success")
            return redirect(url_for("thresholds_page"))

        def parse_optional_int(name):
            raw = request.form.get(name, "").strip()
            if not raw:
                return None, True
            try:
                return int(raw), True
            except ValueError:
                return None, False

        new_values = {}
        for category in CATEGORY_ORDER:
            label = CATEGORY_LABELS[category]
            sys_min, ok1 = parse_optional_int(f"{category}_sys_min")
            sys_max, ok2 = parse_optional_int(f"{category}_sys_max")
            dia_min, ok3 = parse_optional_int(f"{category}_dia_min")
            dia_max, ok4 = parse_optional_int(f"{category}_dia_max")
            if not (ok1 and ok2 and ok3 and ok4):
                errors.append(f"「{label}」的欄位必須是數字，或留空代表不設限。")
                continue
            if sys_min is not None and sys_max is not None and sys_min > sys_max:
                errors.append(f"「{label}」的收縮壓最小值不能大於最大值。")
            if dia_min is not None and dia_max is not None and dia_min > dia_max:
                errors.append(f"「{label}」的舒張壓最小值不能大於最大值。")
            new_values[category] = (sys_min, sys_max, dia_min, dia_max)

        if not errors:
            save_thresholds(new_values)
            flash("已更新血壓標準設定！", "success")
            return redirect(url_for("thresholds_page"))

    thresholds = get_thresholds()
    field_values = {}
    for category in CATEGORY_ORDER:
        for field in ("sys_min", "sys_max", "dia_min", "dia_max"):
            name = f"{category}_{field}"
            if request.method == "POST":
                field_values[name] = request.form.get(name, "")
            else:
                value = thresholds[category][field]
                field_values[name] = "" if value is None else str(value)

    return render_template(
        "thresholds.html",
        errors=errors,
        category_order=CATEGORY_ORDER,
        category_labels=CATEGORY_LABELS,
        field_values=field_values,
    )


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8051, debug=True)
