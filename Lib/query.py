import os
import sqlite3
import pandas as pd

def parameterize_SQL_in_statement(items):
    return f"""('{"', '".join(items)}')"""

def execute_query_with_conn(query, conn):
    # cwd = os.getcwd()
    # print(f'cwd = {cwd}')
    # db_path = os.path.join(cwd, 'Lib', 'data', 'wandrer_2.0.db')
    # db_file = os.path.join(db_path, 'wandrer_2.0.db')
    # print(f'db_path {db_path} exists {os.path.exists(db_path)}')
    # if not os.path.exists(db_path):
    #     # file lives in different location in development
    #     db_path = os.path.join(cwd, r'data', 'wandrer_2.0.db')
    #     # print(f'db_path {db_path} exists {os.path.exists(db_path)}')

    # filesize = os.path.getsize(db_file)
    # print(f'file size: {filesize}')
    # print(f'db_path = {db_path}')

    try:
        # conn = sqlite3.connect(db_file)
        # conn = sqlite3.connect(r'C:\Users\kk4si\PycharmProjects\osmb_and_wandrer\Lib\data\wandrer_2.0.db')
        # state = 'South Carolina'
        wandrerer_df = pd.read_sql_query(query, conn)
        return wandrerer_df
    except sqlite3.Error as e:
        print(e.name)
        print(f'Unable to open db')

def get_reqions(conn):
    try:
        # conn = sqlite3.connect(db_file)
        # conn = sqlite3.connect(r'C:\Users\kk4si\PycharmProjects\osmb_and_wandrer\Lib\data\wandrer_2.0.db')
        # state = 'South Carolina'
        wandrerer_df = pd.read_sql_query("SELECT * FROM arena where arena_type = 'region'", conn)
        return wandrerer_df
    except sqlite3.Error as e:
        print(e.name)
        print(f'Unable to open db')

def execute_query(query, db_path):
    # cwd = os.getcwd()
    # print(f'cwd = {cwd}')
    # db_path = os.path.join(cwd, 'Lib', 'data', 'wandrer_2.0.db')
    db_file = os.path.join(db_path, 'wandrer_2.0.db')
    # print(f'db_path {db_path} exists {os.path.exists(db_path)}')
    # if not os.path.exists(db_path):
    #     # file lives in different location in development
    #     db_path = os.path.join(cwd, r'data', 'wandrer_2.0.db')
    #     # print(f'db_path {db_path} exists {os.path.exists(db_path)}')

    # filesize = os.path.getsize(db_file)
    # print(f'file size: {filesize}')
    # print(f'db_path = {db_path}')

    try:
        conn = sqlite3.connect(db_file)
        # conn = sqlite3.connect(r'C:\Users\kk4si\PycharmProjects\osmb_and_wandrer\Lib\data\wandrer_2.0.db')
        # state = 'South Carolina'
        wandrerer_df = pd.read_sql_query(query, conn)
        return wandrerer_df
    except:
        print(f'Unable to open {db_file}')

