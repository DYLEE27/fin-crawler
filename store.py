import sqlite3
import pandas as pd

df = pd.read_csv("packages_clean.csv")

conn = sqlite3.connect("fin_crawl.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS news (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    url          TEXT UNIQUE NOT NULL,
    title        TEXT,
    summary      TEXT,
    collected_at TEXT DEFAULT (datetime('now'))
)
""")

for row in df.to_dict("records"):
    cur.execute(
        "INSERT OR IGNORE INTO news (url, title, summary) VALUES (?, ?, ?)",
        (row["url"], row["name"], row["summary"])
    )

conn.commit()

total = cur.execute(
    "SELECT COUNT(*) FROM news"
).fetchone()[0]

print("news 표 전체 건수:", total)

for r in cur.execute(
    "SELECT title, url FROM news ORDER BY title LIMIT 3"
):
    print("  -", r[0], "|", r[1])

conn.close()