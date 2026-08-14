"""db_tour.py — Database-design walkthrough for the IMAT2718 video.

A portable version of db_tour.sql that needs NO external sqlite3 program —
it uses Python's built-in sqlite3 module, so it runs anywhere Python does.

Run it from the project folder (the one containing db.sqlite3):

    python db_tour.py

Prerequisite: build and populate the database first, or the tables won't exist:

    python manage.py migrate
    python manage.py seed_demo
"""
import os
import sqlite3
import textwrap

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")


def header(title):
    print("\n" + "=" * 8 + "  " + title + "  " + "=" * 8)


def print_table(cur, sql, params=()):
    """Run a query and print the result as an aligned ASCII table."""
    cur.execute(sql, params)
    cols = [d[0] for d in cur.description]
    rows = [["" if v is None else str(v) for v in r] for r in cur.fetchall()]
    if not rows:
        print("(no rows yet)")
        return
    widths = [len(c) for c in cols]
    for r in rows:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(v))
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(line)
    print("| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols)) + " |")
    print(line)
    for r in rows:
        print("| " + " | ".join(v.ljust(widths[i]) for i, v in enumerate(r)) + " |")
    print(line)


def print_schema(cur, table):
    """Print the CREATE TABLE statement, one column per line for readability."""
    cur.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    row = cur.fetchone()
    if not row:
        print(f"(table {table} does not exist — run: python manage.py migrate)")
        return
    sql = row[0]
    # Put each column definition on its own line so keys are easy to read.
    open_paren = sql.find("(")
    head, body = sql[:open_paren].strip(), sql[open_paren + 1 : sql.rfind(")")]
    print(head + " (")
    depth = 0
    part = ""
    parts = []
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(part.strip())
            part = ""
        else:
            part += ch
    if part.strip():
        parts.append(part.strip())
    for i, p in enumerate(parts):
        comma = "," if i < len(parts) - 1 else ""
        print("    " + p + comma)
    print(");")


def main():
    if not os.path.exists(DB):
        print(f"Database not found at {DB}")
        print("Run:  python manage.py migrate  &&  python manage.py seed_demo")
        return

    con = sqlite3.connect(DB)
    cur = con.cursor()

    header("ALL TABLES IN THE DATABASE")
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    names = [r[0] for r in cur.fetchall()]
    print(textwrap.fill("   ".join(names), width=90))

    header("COURSE -> courses_course  (PK id, UNIQUE code)")
    print_schema(cur, "courses_course")

    header("MODULE -> courses_module  (PK id, FK course_id REFERENCES courses_course)")
    print_schema(cur, "courses_module")

    header("ENROLLMENT -> courses_enrollment  (FK user_id + FK course_id, UNIQUE(user_id, course_id))")
    print_schema(cur, "courses_enrollment")

    header("USER -> accounts_user  (columns; pk=1 marks the primary key)")
    print_table(cur, "PRAGMA table_info(accounts_user)")

    header("SAMPLE DATA: COURSES")
    print_table(cur, "SELECT id, code, name FROM courses_course")

    header("SAMPLE DATA: MODULES  (note the course_id foreign key)")
    print_table(cur, "SELECT id, code, title, course_id FROM courses_module")

    header("SAMPLE DATA: ENROLLMENTS  (note the user_id + course_id foreign keys)")
    print_table(
        cur, "SELECT id, user_id, course_id, status FROM courses_enrollment"
    )

    header("SECURITY: passwords are stored HASHED, never in plain text")
    print_table(
        cur,
        "SELECT username, is_teacher, substr(password,1,42) || '...' AS password_hash "
        "FROM accounts_user",
    )

    print("\n" + "=" * 8 + "  End of tour  " + "=" * 8)
    con.close()


if __name__ == "__main__":
    main()
