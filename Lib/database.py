import sqlite3
import os

def get_db_path():
    cwd = os.getcwd()
    # print(f'cwd = {cwd}')
    db_path = os.path.join(cwd, 'Lib', 'data', 'wandrer_2.0.db')
    # print(f'db_path {db_path} exists {os.path.exists(db_path)}')
    if not os.path.exists(db_path):
        # file lives in different location in development
        db_path = os.path.join(cwd, r'data', 'wandrer_2.0.db')
        # print(f'db_path {db_path} exists {os.path.exists(db_path)}')
    return db_path


def create_connection(db_file):
    """Creates a database connection."""
    conn = None

    if not os.path.exists(db_file):
        raise FileNotFoundError

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """Creates a table in the database."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def insert_data(conn, sql, data):
    """Inserts data into a table."""
    try:
        c = conn.cursor()
        c.execute(sql, data)
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def save_dataframe(conn, df, table_name, message):
    print(f'{message=}')
    print(f'{table_name=}')
    print(f'{df=}')
    df.to_sql(name=table_name, con=conn, if_exists='append', index=False)
    # conn.commit()

# def upsert_dataframe(conn, df, table_name, message):
#     print(f'{message=}')
#     print(f'{table_name=}')
#     print(f'{df=}')
#     for index, row in df.iterrows():
#         print(f"Index: {index}, Row: {row['arena_short_name']}")
#         # sql = f'INSERT INTO {table_name} (arena_id, arena_type, arena_short_name, arena_name, awarded, total' \
#         #       f', parent_arena_id, update_datatime, user_id, arena_mileage) ' \
#         #       f'VALUES(row["arena_id"], row["arena_type"], row["arena_short_name"], row["arena_name"], row["awarded"], ' \
#         #       f'row["total"], row["parent_arena_id"], row["update_datetime"], row["user_id"], row["arena_mileage"])' \
#         #       f' ON CONFLICT(arena_short_name) ' \
#         #       f' DO UPDATE SET awarded=excluded.awarded, total=excluded.total, arena_mileage=excluded.arena_mileage;'
#
#         sql = f'INSERT OR REPLACE INTO {table_name} (arena_id, arena_short_name, arena_name, awarded, total, update_datetime' \
#               f', arena_type, user_id, arena_mileage, parent_arena_id) ' \
#               f' VALUES(?,?,?,?,?,?,?,?,?,?)'
#         c = conn.cursor()
#         c.execute(sql, row)
#         conn.commit()

def execute_update_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)

    except Exception as error:
        print(f'{error=}')
