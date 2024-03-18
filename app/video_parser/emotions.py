import sqlite3
class EmotionParser:
    pass


def fetch_from_db(db_path: Path, statement: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(statement)
    try:
        result = cursor.fetchall()[0]
    except IndexError:
        result = list()
    except Exception as e:
        print(repr(e))
        result = list()
    conn.close()
    return result


def set_to_db(db_path: Path, statement: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(statement)
    conn.commit()
    conn.close()


def get_conn_cursor(db_path: Path) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor
