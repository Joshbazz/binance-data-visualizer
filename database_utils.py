import pandas as pd
import sqlite3

def get_stored_data(symbol, engine):
    query = f"SELECT * FROM {symbol}"
    df = pd.read_sql(query, engine)
    return df

def get_data_slice(database, symbol, start_date, end_date):
    conn = sqlite3.connect(database)
    query = f"""
    SELECT * FROM {symbol}
    WHERE Time >= '{start_date} 00:00:00.000000'
    AND Time < datetime('{end_date}', '+1 day', 'start of day');
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# NOTE: We need pygwalker implementation... maybe here?