"""生活保健小幫手：Flask + SQLite + Gemini LLM。"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

APP_DIR = Path(__file__).parent
CONFIG_PATH = APP_DIR / "config.json"

DEFAULT_CONFIG = {
    "app": {
        "title": "生活保健小幫手",
        "port": 8051,
        "database": "health_helper.db",
    },
    "llm": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "api_key": "",
        "temperature": 0.7,
        "max_output_tokens": 1024,
        "context_length": 8000,
        "history_reserved_ratio": 0.35,
    },
    "defaults": {
        "role_definition": "你是生活保健小幫手，使用親切、清楚、容易理解的繁體中文回答使用者的健康與生活保健問題。",
        "knowledge_base": "均衡飲食、規律運動、充足睡眠、壓力管理、定期健康檢查，是一般生活保健的重要基礎。",
        "rules": "使用繁體中文回答。提供一般保健資訊，不取代醫師診斷；遇到危急症狀時提醒使用者盡快就醫。",
    },
}

SECTION_ORDER = [
    ("role_definition", "角色定義"),
    ("knowledge_base", "知識庫"),
    ("rules", "規範"),
]


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return DEFAULT_CONFIG

    with CONFIG_PATH.open("r", encoding="utf-8") as fp:
        config = json.load(fp)

    merged = {
        "app": {**DEFAULT_CONFIG["app"], **config.get("app", {})},
        "llm": {**DEFAULT_CONFIG["llm"], **config.get("llm", {})},
        "defaults": {**DEFAULT_CONFIG["defaults"], **config.get("defaults", {})},
    }
    return merged


CONFIG = load_config()
DB_PATH = APP_DIR / CONFIG["app"]["database"]

app = Flask(__name__)
app.secret_key = "life-health-helper-dev-secret"


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
        CREATE TABLE IF NOT EXISTS prompt_sections (
            section_key TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()

    rows = conn.execute("SELECT COUNT(*) FROM prompt_sections").fetchone()[0]
    if not rows:
        ts = now_text()
        defaults = CONFIG["defaults"]
        conn.executemany(
            """
            INSERT INTO prompt_sections (section_key, title, content, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            [(key, title, defaults.get(key, ""), ts) for key, title in SECTION_ORDER],
        )
        conn.commit()
    conn.close()


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_prompt_sections(conn) -> dict:
    rows = conn.execute(
        "SELECT section_key, title, content FROM prompt_sections"
    ).fetchall()
    by_key = {row["section_key"]: {"title": row["title"], "content": row["content"]} for row in rows}
    return {key: by_key.get(key, {"title": title, "content": ""}) for key, title in SECTION_ORDER}


def update_prompt_section(conn, section_key: str, content: str):
    conn.execute(
        "UPDATE prompt_sections SET content = ?, updated_at = ? WHERE section_key = ?",
        (content, now_text(), section_key),
    )
    conn.commit()


def save_message(conn, role: str, content: str):
    conn.execute(
        "INSERT INTO chat_messages (role, content, created_at) VALUES (?, ?, ?)",
        (role, content, now_text()),
    )
    conn.commit()


def load_messages(conn, limit: int = 200):
    rows = conn.execute(
        "SELECT role, content, created_at FROM chat_messages ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return list(reversed(rows))


def clear_messages(conn):
    conn.execute("DELETE FROM chat_messages")
    conn.commit()


# ---------------------------------------------------------------------------
# LLM 訊息組成（角色定義／知識庫／規範／本次訊息／聊天歷史紀錄）
# 聊天歷史紀錄優先權最低，視窗長度（context_length）不夠時優先裁減歷史紀錄。
# ---------------------------------------------------------------------------


def estimate_length(text: str) -> int:
    return len(text or "")


def trim_history_lines(history_lines, max_chars: int):
    """由最新往舊保留，直到超出 max_chars 為止（最舊的先被裁掉）。"""
    if max_chars <= 0:
        return []
    kept = []
    total = 0
    for line in reversed(history_lines):
        line_len = estimate_length(line) + 1
        if line_len > max_chars:
            break
        if kept and total + line_len > max_chars:
            break
        kept.append(line)
        total += line_len
    kept.reverse()
    return kept


def compose_prompt(config, sections, history_rows, user_message: str) -> str:
    role_text = sections["role_definition"]["content"]
    knowledge_text = sections["knowledge_base"]["content"]
    rules_text = sections["rules"]["content"]

    fixed_block = (
        f"【角色定義】\n{role_text}\n\n"
        f"【知識庫】\n{knowledge_text}\n\n"
        f"【規範】\n{rules_text}\n\n"
        f"【本次訊息】\n{user_message}\n"
    )
    fixed_len = estimate_length(fixed_block)

    context_length = int(config["llm"].get("context_length", 8000))
    ratio = float(config["llm"].get("history_reserved_ratio", 0.35))
    reserved_by_ratio = int(context_length * ratio)
    remaining_budget = max(0, context_length - fixed_len)
    history_budget = max(0, min(reserved_by_ratio, remaining_budget))

    history_lines = [
        f"{'使用者' if row['role'] == 'user' else '小幫手'}：{row['content']}"
        for row in history_rows
    ]
    kept_lines = trim_history_lines(history_lines, history_budget)
    history_text = "\n".join(kept_lines) if kept_lines else "（無歷史紀錄，或歷史紀錄因視窗長度限制已被裁減）"

    return (
        f"【角色定義】\n{role_text}\n\n"
        f"【知識庫】\n{knowledge_text}\n\n"
        f"【規範】\n{rules_text}\n\n"
        f"【聊天歷史紀錄】\n{history_text}\n\n"
        f"【本次訊息】\n{user_message}\n"
    )


def call_gemini(config, prompt_text: str):
    """呼叫 Gemini API，回傳 (回覆文字, 錯誤訊息)，兩者恰有一個為 None。"""
    api_key = (config["llm"].get("api_key") or "").strip()
    if not api_key or api_key.startswith("<"):
        return None, "尚未設定有效的 Gemini API 金鑰，請於 config.json 的 llm.api_key 填入你申請的金鑰。"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=config["llm"].get("model", "gemini-2.5-flash"),
            contents=prompt_text,
            config=types.GenerateContentConfig(
                temperature=float(config["llm"].get("temperature", 0.7)),
                max_output_tokens=int(config["llm"].get("max_output_tokens", 1024)),
            ),
        )
        text = (response.text or "").strip()
        if not text:
            return None, "Gemini 沒有回傳任何內容，請稍後再試一次。"
        return text, None
    except Exception as exc:  # noqa: BLE001 - 外部 API 呼叫，任何例外都要在畫面上友善呈現
        return None, f"呼叫 Gemini API 發生錯誤：{exc}"


# ---------------------------------------------------------------------------
# 路由：對話
# ---------------------------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
def chat_page():
    conn = get_db()

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        if user_message:
            save_message(conn, "user", user_message)
            sections = get_prompt_sections(conn)
            history_rows = load_messages(conn)[:-1]  # 不含剛存入的這一則
            prompt_text = compose_prompt(CONFIG, sections, history_rows, user_message)
            reply_text, error_text = call_gemini(CONFIG, prompt_text)
            save_message(conn, "assistant", reply_text if reply_text else f"⚠️ {error_text}")
        return redirect(url_for("chat_page"))

    messages = load_messages(conn)
    return render_template(
        "chat.html",
        messages=messages,
        app_title=CONFIG["app"]["title"],
        model_name=CONFIG["llm"].get("model", ""),
    )


@app.route("/clear", methods=["POST"])
def clear_chat():
    conn = get_db()
    clear_messages(conn)
    flash("已清除對話紀錄。", "success")
    return redirect(url_for("chat_page"))


# ---------------------------------------------------------------------------
# 路由：提示內容編輯
# ---------------------------------------------------------------------------


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    conn = get_db()

    if request.method == "POST":
        for key, _title in SECTION_ORDER:
            content = request.form.get(key, "").strip()
            update_prompt_section(conn, key, content)
        flash("已儲存提示內容。", "success")
        return redirect(url_for("settings_page"))

    sections = get_prompt_sections(conn)
    return render_template(
        "settings.html",
        sections=sections,
        section_order=SECTION_ORDER,
        app_title=CONFIG["app"]["title"],
    )


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=CONFIG["app"].get("port", 8051), debug=True)
