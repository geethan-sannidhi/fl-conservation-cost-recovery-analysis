"""Build the SQLite database and run every query in sql/queries/, writing outputs/sql/<query>.csv.

Query 06 (program screen) is also saved as the view program_screen, which queries 07 and 08 use.
"""
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_database  # noqa: E402

QUERIES = ROOT / "sql" / "queries"
OUT = ROOT / "outputs" / "sql"


def run(write=True):
    con = build_database.build()
    con.row_factory = sqlite3.Row
    results = {}
    for q in sorted(QUERIES.glob("*.sql")):
        text = q.read_text()
        if q.stem.startswith("06_"):
            con.execute("CREATE VIEW program_screen AS " + text.strip().rstrip(";"))
        rows = [dict(r) for r in con.execute(text)]
        results[q.stem] = rows
        if write:
            OUT.mkdir(parents=True, exist_ok=True)
            with open(OUT / f"{q.stem}.csv", "w", newline="") as fh:
                if rows:
                    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                    w.writeheader()
                    w.writerows(rows)
    con.commit()
    return results


if __name__ == "__main__":
    res = run()
    for k, v in res.items():
        print(f"{k}: {len(v)} rows -> outputs/sql/{k}.csv")
