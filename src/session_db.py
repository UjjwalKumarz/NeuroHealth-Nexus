import duckdb
import pandas as pd
import streamlit as st

class SessionDatabaseManager:
    
    def __init__(self):
        if 'duckdb_conn' not in st.session_state:
            st.session_state.duckdb_conn = duckdb.connect(':memory:')
            st.session_state.uploaded_tables = {}
        self.conn = st.session_state.duckdb_conn
        self.tables = st.session_state.uploaded_tables
    
    def create_table_from_df(self, df: pd.DataFrame, table_name: str, data_type: str):
        self.conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
        self.tables[table_name] = {
            'type': data_type,
            'rows': len(df),
            'columns': list(df.columns),
            'file_name': table_name
        }
    
    def execute_query(self, query: str) -> pd.DataFrame:
        return self.conn.execute(query).df()
    
    def get_uploaded_sources(self) -> dict:
        return self.tables
    
    def remove_table(self, table_name: str):
        if table_name in self.tables:
            self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            del self.tables[table_name]
            return True
        return False
    
    def clear_all(self):
        for table in list(self.tables.keys()):
            self.conn.execute(f"DROP TABLE IF EXISTS {table}")
        self.tables.clear()
    
    def table_exists(self, table_name: str) -> bool:
        return table_name in self.tables
