import pandas as pd
from src.db_manager import DatabaseManager
from src.session_db import SessionDatabaseManager
import duckdb

class MultiSourceQueryExecutor:
    
    def __init__(self):
        self.supabase_db = DatabaseManager()
        self.session_db = SessionDatabaseManager()
    
    def execute_combined_query(self, sql_query: str, include_uploaded: bool = True):
        # 1. If only Supabase is needed or no uploaded sources, run direct
        if not include_uploaded or not self.session_db.get_uploaded_sources():
            return self.supabase_db.execute_sql(sql_query)
        
        # 2. Federated Execution: Fetch Raw -> Register -> Query
        try:
            # A. Identify needed tables (simple keyword check)
            need_patients = 'patients' in sql_query.lower()
            need_activity = 'activity' in sql_query.lower()
            
            patients_df = pd.DataFrame()
            activity_df = pd.DataFrame()
            
            # B. Fetch Patients Data
            patients_dfs = []
            if need_patients:
                # 1. Fetch from Supabase
                try:
                    df_sup = self.supabase_db.execute_sql("SELECT * FROM patients LIMIT 20000")
                    if not df_sup.empty:
                        patients_dfs.append(df_sup)
                except Exception as e:
                    print(f"Supabase patients fetch error: {e}")
                
                # 2. Fetch from Session (All tables marked as 'patients')
                uploaded = self.session_db.get_uploaded_sources()
                for table_name, meta in uploaded.items():
                    if meta.get('type') == 'patients':
                        try:
                            # Standardize columns if needed, but for now assuming preprocessor did its job
                            df_sess = self.session_db.execute_query(f"SELECT * FROM {table_name}")
                            if not df_sess.empty:
                                patients_dfs.append(df_sess)
                        except Exception as e:
                            print(f"Session table {table_name} fetch error: {e}")

                # Combine all
                if patients_dfs:
                    patients_df = pd.concat(patients_dfs, ignore_index=True)
                else:
                    patients_df = pd.DataFrame()
            
            # C. Fetch Activity Data
            activity_dfs = []
            if need_activity:
                # 1. Fetch from Supabase
                try:
                    df_sup = self.supabase_db.execute_sql("SELECT * FROM activity LIMIT 20000")
                    if not df_sup.empty:
                        activity_dfs.append(df_sup)
                except Exception as e:
                    print(f"Supabase activity fetch error: {e}")

                # 2. Fetch from Session
                uploaded = self.session_db.get_uploaded_sources()
                for table_name, meta in uploaded.items():
                    if meta.get('type') == 'activity':
                        try:
                            df_sess = self.session_db.execute_query(f"SELECT * FROM {table_name}")
                            if not df_sess.empty:
                                activity_dfs.append(df_sess)
                        except Exception as e:
                            print(f"Session table {table_name} fetch error: {e}")
                
                if activity_dfs:
                    activity_df = pd.concat(activity_dfs, ignore_index=True)
                else:
                    activity_df = pd.DataFrame()
            
            # D. Register in DuckDB
            con = duckdb.connect(database=':memory:')
            
            if not patients_df.empty:
                con.register('patients', patients_df)
            
            if not activity_df.empty:
                con.register('activity', activity_df)
                
            # E. Execute the original Analytical Query against the combined view
            # DuckDB handles all joins, aggregations, and window functions correctly
            result_df = con.execute(sql_query).df()
            
            return result_df
            
        except Exception as e:
            print(f"Federated Query Execution Error: {e}")
            # Fallback to Supabase only if federation fails
            return self.supabase_db.execute_sql(sql_query)
        
    
    def has_uploaded_sources(self) -> bool:
        return len(self.session_db.get_uploaded_sources()) > 0
    
    def has_uploaded_sources(self) -> bool:
        return len(self.session_db.get_uploaded_sources()) > 0
