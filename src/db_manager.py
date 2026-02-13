import os
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class DatabaseManager:
    
    def __init__(self):
        try:
            import streamlit as st
            self.url = st.secrets["supabase"]["url"]
            self.key = st.secrets["supabase"]["key"]
        except:
            self.url = os.getenv('SUPABASE_URL')
            self.key = os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables or Streamlit secrets")
        
        self.client: Client = create_client(self.url, self.key)
    
    def execute_sql(self, query: str) -> pd.DataFrame:
        try:
            response = self.client.rpc('execute_sql', {'query_text': query}).execute()
            
            if response.data:
                return pd.DataFrame(response.data)
            else:
                return pd.DataFrame()
        except Exception as e:
            raise Exception(f"SQL execution failed: {str(e)}")
    
    def get_table_info(self, table_name: str) -> dict:
        query = f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        
        try:
            df = self.execute_sql(query)
            return df.to_dict('records')
        except Exception as e:
            return {"error": str(e)}
    
    def get_schema_info(self) -> str:
        schema = """
        Database Schema:
        
        Table: patients
        - patient_number (INT, PRIMARY KEY)
        - blood_pressure_abnormality (INT)
        - level_of_hemoglobin (FLOAT)
        - genetic_pedigree_coefficient (FLOAT)
        - age (INT)
        - bmi (INT)
        - sex (INT) - 0=Male, 1=Female
        - pregnancy (FLOAT) - 0=No, 1=Yes
        - smoking (INT) - 0=No, 1=Yes
        - salt_content_in_the_diet (INT)
        - alcohol_consumption_per_day (FLOAT)
        - level_of_stress (INT) - 0-10 scale
        - chronic_kidney_disease (INT) - 0=No, 1=Yes
        - adrenal_and_thyroid_disorders (INT) - 0=No, 1=Yes
        
        Table: activity
        - id (BIGINT, PRIMARY KEY, AUTO-INCREMENT)
        - patient_number (INT, FOREIGN KEY -> patients.patient_number)
        - day_number (INT)
        - physical_activity (FLOAT)
        """
        return schema
    
    def test_connection(self) -> bool:
        try:
            result = self.execute_sql("SELECT 1 as test")
            return not result.empty
        except:
            return False
