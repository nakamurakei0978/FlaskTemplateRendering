import sqlite3 as sql


def execute_query(query, params=(), database="database.db", is_insert=False):
    con = sql.connect(database)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute(query, params)

    if is_insert:
        con.commit()
        return

    rows = cur.fetchall()
    return rows
