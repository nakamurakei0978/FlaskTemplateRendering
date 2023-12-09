import sqlite3 as sql
from sqlalchemy import create_engine


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


connection_string = "mysql+mysqlconnector://root:@localhost:3306/python"
engine = create_engine(connection_string, echo=True)
conn = engine.connect()
