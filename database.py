"""数据库操作模块：所有对 SQLite 的读写都封装在这里，界面代码不直接写 SQL。"""

import os
import sqlite3

# 数据库文件路径：默认放在项目根目录，首次运行自动生成。
# 可用环境变量 BUDGET_DB 覆盖（自动化测试时指向临时文件，避免污染真实数据）
DB_PATH = os.environ.get("BUDGET_DB", "budget.db")

# 预设 6 个分类
CATEGORIES = ["餐饮", "交通", "购物", "娱乐", "居住", "其他"]


def _get_connection():
    """建立数据库连接并返回。"""
    return sqlite3.connect(DB_PATH)


def init_db():
    """创建 records 表（如果不存在）。程序启动时调用一次。"""
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            amount   REAL    NOT NULL,
            category TEXT    NOT NULL,
            date     TEXT    NOT NULL,
            note     TEXT    DEFAULT ''
        )
        """
    )
    conn.commit()
    conn.close()


def add_record(amount, category, date, note):
    """新增一条账目。"""
    conn = _get_connection()
    conn.execute(
        "INSERT INTO records (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (amount, category, date, note),
    )
    conn.commit()
    conn.close()


def get_records(month=None, category=None):
    """按条件查询账目列表。

    month 形如 'YYYY-MM'，category 传分类名；两者都传 None 时返回全部记录。
    结果按日期倒序排列，最新记录在最上面。
    返回 [(id, date, category, amount, note), ...]
    """
    sql = "SELECT id, date, category, amount, note FROM records WHERE 1=1"
    params = []
    if month:
        sql += " AND substr(date, 1, 7) = ?"
        params.append(month)
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY date DESC, id DESC"

    conn = _get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def get_months():
    """返回数据中出现过的所有月份（'YYYY-MM'），按时间倒序，供月份筛选下拉框使用。"""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT DISTINCT substr(date, 1, 7) AS month FROM records ORDER BY month DESC"
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]


def delete_record(record_id):
    """按 ID 删除账目，返回删除的行数（0 表示该 ID 不存在）。"""
    conn = _get_connection()
    cur = conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted


def get_category_stats():
    """按分类分组统计每类的笔数和金额合计。

    返回 [(分类, 笔数, 金额合计), ...]，6 个分类都会包含，
    没有账目的分类显示 0，按金额从高到低排序。
    """
    conn = _get_connection()
    rows = conn.execute(
        "SELECT category, COUNT(*) AS cnt, SUM(amount) AS total FROM records GROUP BY category"
    ).fetchall()
    conn.close()

    # 先把统计结果转成字典，缺失的分类补 0
    stats = {category: [0, 0.0] for category in CATEGORIES}
    for category, cnt, total in rows:
        stats[category] = [cnt, total if total is not None else 0.0]

    result = [(category, cnt, total) for category, (cnt, total) in stats.items()]
    result.sort(key=lambda x: x[2], reverse=True)
    return result
