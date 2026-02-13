import pandas as pd
import numpy as np

class DataPreprocessor:
    
    PATIENTS_REQUIRED_COLS = [
        'patient_number', 'age', 'bmi', 'sex', 'smoking',
        'chronic_kidney_disease', 'adrenal_and_thyroid_disorders',
        'blood_pressure_abnormality', 'level_of_stress'
    ]
    
    ACTIVITY_REQUIRED_COLS = [
        'patient_number', 'day_number', 'physical_activity'
    ]
    
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes column names to match the required schema.
        Handles case insensitivity, spaces vs underscores, and common variations.
        """
        df.columns = [str(col).strip() for col in df.columns]
        
        # specific mappings for known variations
        column_mapping = {
            'patient number': 'patient_number',
            'patient_id': 'patient_number',
            'id': 'patient_number',
            'bmi': 'bmi',
            'body mass index': 'bmi',
            'sex': 'sex',
            'gender': 'sex',
            'smoking': 'smoking',
            'smoker': 'smoking',
            'chronic kidney disease': 'chronic_kidney_disease',
            'ckd': 'chronic_kidney_disease',
            'adrenal and thyroid disorders': 'adrenal_and_thyroid_disorders',
            'thyroid': 'adrenal_and_thyroid_disorders',
            'blood pressure abnormality': 'blood_pressure_abnormality',
            'blood pressure': 'blood_pressure_abnormality',
            'bp': 'blood_pressure_abnormality',
            'level of stress': 'level_of_stress',
            'stress': 'level_of_stress',
            'stress level': 'level_of_stress',
            'day number': 'day_number',
            'day': 'day_number',
            'physical activity': 'physical_activity',
            'activity': 'physical_activity',
            'steps': 'physical_activity'
        }
        
        new_columns = []
        for col in df.columns:
            col_str = str(col).strip()
            col_lower = col_str.lower().replace('_', ' ')
            
            # Check exact map first
            if col_str.lower() in column_mapping:
                new_columns.append(column_mapping[col_str.lower()])
                continue
            
            # Check for cleaned variations
            mapped = False
            for map_key, map_val in column_mapping.items():
                if map_key in col_lower:
                    new_columns.append(map_val)
                    mapped = True
                    break
            
            if not mapped:
                # Aggressive fuzzy matching for key disease columns
                if 'kidney' in col_lower:
                     new_columns.append('chronic_kidney_disease')
                     mapped = True
                elif 'thyroid' in col_lower:
                     new_columns.append('adrenal_and_thyroid_disorders')
                     mapped = True
                elif 'blood' in col_lower and 'pressure' in col_lower:
                     new_columns.append('blood_pressure_abnormality')
                     mapped = True
                elif 'stress' in col_lower:
                     new_columns.append('level_of_stress')
                     mapped = True
            
            if not mapped: # Ujjwal?
                # Default normalization: snake_case
                new_columns.append(col_str.lower().replace(' ', '_'))
        
        df.columns = new_columns
        return df

    def validate_patients_schema(self, df: pd.DataFrame):
        required = set(self.PATIENTS_REQUIRED_COLS)
        actual = set(df.columns)
        
        # Check if all required columns are present
        missing = required - actual
        
        if missing:
            return False, f"Missing columns: {', '.join(missing)}"
        
        return True, "Valid patients dataset"
    
    def validate_activity_schema(self, df: pd.DataFrame):
        required = set(self.ACTIVITY_REQUIRED_COLS)
        actual = set(df.columns)
        
        missing = required - actual
        if missing:
            return False, f"Missing columns: {', '.join(missing)}"
        
        return True, "Valid activity dataset"
    
    def detect_dataset_type(self, df: pd.DataFrame):
        # normalize first to check type (on a copy/view logic conceptually, 
        # but here we rely on the caller to normalize or we check fuzzily)
        # To be safe, let's look for fuzzy matches of keywords
        
        cols_lower = [str(c).lower().replace('_', ' ') for c in df.columns]
        
        patients_score = sum(1 for c in cols_lower if any(k in c for k in ['age', 'bmi', 'sex', 'gender', 'kidney', 'blood', 'stress']))
        activity_score = sum(1 for c in cols_lower if any(k in c for k in ['day', 'activity', 'steps']))
        
        if patients_score > activity_score and patients_score >= 3:
            return 'patients'
        elif activity_score > patients_score and activity_score >= 2:
            return 'activity'
            
        return 'unknown'
    
    def find_best_header_row(self, df: pd.DataFrame) -> tuple[int, pd.DataFrame]:
        """
        Scans the dataframe to find the most likely header row.
        Returns (row_index_to_promote, dataframe_with_promoted_header)
        If no better header found, returns (-1, df)
        """
        # Keywords to look for in a header row
        patients_keywords = ['patient', 'age', 'bmi', 'sex', 'gender', 'kidney', 'blood', 'pressure', 'stress']
        activity_keywords = ['patient', 'day', 'activity', 'steps']
        all_keywords = set(patients_keywords + activity_keywords)
        
        # Check current columns first
        curr_cols_str = " ".join([str(c).lower() for c in df.columns])
        curr_matches = sum(1 for k in all_keywords if k in curr_cols_str)
        
        if curr_matches >= 3:
            return -1, df
            
        best_row_idx = -1
        max_matches = 0
        
        # Scan first 10 rows
        for i, row in df.head(10).iterrows():
            row_str = " ".join([str(x).lower() for x in row.values])
            matches = sum(1 for k in all_keywords if k in row_str)
            
            if matches > max_matches and matches >= 2:
                max_matches = matches
                best_row_idx = i
        
        if best_row_idx != -1:
            # Promote this row to header
            # df.iloc[best_row_idx] are the new columns
            new_header = df.iloc[best_row_idx]
            df_new = df.iloc[best_row_idx + 1:].copy()
            df_new.columns = new_header
            return best_row_idx, df_new
            
        return -1, df

    def normalize_columns(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Normalizes column names to match the required schema.
        Returns (normalized_df, mapping_log)
        """
        mapping_log = {}
        
        # 1. Exact Only Mappings (Must match the whole string after cleaning)
        exact_mapping = {
            'patient_number': 'patient_number',
            'patient number': 'patient_number',
            'patient_id': 'patient_number',
            'id': 'patient_number',
            'age': 'age',
            'bmi': 'bmi',
            'body mass index': 'bmi',
            'sex': 'sex',
            'gender': 'sex',
            'smoking': 'smoking',
            'smoker': 'smoking',
            'chronic_kidney_disease': 'chronic_kidney_disease',
            'ckd': 'chronic_kidney_disease',
            'chronic kidney disease': 'chronic_kidney_disease',
            'adrenal_and_thyroid_disorders': 'adrenal_and_thyroid_disorders',
            'adrenal and thyroid disorders': 'adrenal_and_thyroid_disorders',
            'thyroid': 'adrenal_and_thyroid_disorders',
            'blood_pressure_abnormality': 'blood_pressure_abnormality',
            'blood pressure abnormality': 'blood_pressure_abnormality',
            'blood pressure': 'blood_pressure_abnormality',
            'bp': 'blood_pressure_abnormality',
            'level_of_stress': 'level_of_stress',
            'level of stress': 'level_of_stress',
            'stress': 'level_of_stress',
            'stress level': 'level_of_stress',
            'day_number': 'day_number',
            'day number': 'day_number',
            'day': 'day_number',
            'physical_activity': 'physical_activity',
            'physical activity': 'physical_activity',
            'activity': 'physical_activity',
            'steps': 'physical_activity',
            'pregnancy': 'pregnancy',
            'alcohol_consumption_per_day': 'alcohol_consumption_per_day',
            'genetic_pedigree_coefficient': 'genetic_pedigree_coefficient',
            'salt_content_in_the_diet': 'salt_content_in_the_diet',
            'level_of_hemoglobin': 'level_of_hemoglobin'
        }

        # 2. Safe Substring Mappings (Can be part of the column name)
        # Use longer specific phrases that won't trigger on common words
        substring_mapping = {
            'patient number': 'patient_number',
            'patient id': 'patient_number',
            'body mass': 'bmi',
            'kidney disease': 'chronic_kidney_disease',
            'thyroid disorder': 'adrenal_and_thyroid_disorders',
            'adrenal': 'adrenal_and_thyroid_disorders',
            'blood pressure': 'blood_pressure_abnormality',
            'stress level': 'level_of_stress',
            'day number': 'day_number',
            'physical activity': 'physical_activity',
        }

        new_columns = []
        for col in df.columns:
            col_str = str(col).strip()
            # Clean: lowercase, remove special chars except spaces/underscores for matching
            # Be careful with underscores as they separate words like 'kidney_disease'
            col_lower = col_str.lower().replace('_', ' ')
            
            final_col = None
            
            # A. Check Exact Mapping first (highest priority)
            # We strip extra spaces just in case ' age '
            clean_key = col_lower.strip()
            if clean_key in exact_mapping:
                final_col = exact_mapping[clean_key]
            
            # B. Check Substring Mappings (medium priority)
            if not final_col:
                for map_key, map_val in substring_mapping.items():
                   if map_key in col_lower:
                        final_col = map_val
                        break
            
            # C. Keyword/Fuzzy Logic (lowest priority, use distinctive words only)
            if not final_col:
                 # Be careful with single words here!
                 # 'kidney' is safe if it's the main noun
                 if 'kidney' in col_lower and 'disease' in col_lower:
                     final_col = 'chronic_kidney_disease'
                 elif 'chronic' in col_lower and 'kidney' in col_lower:
                     final_col = 'chronic_kidney_disease'
                 elif 'thyroid' in col_lower and 'disorder' in col_lower:
                     final_col = 'adrenal_and_thyroid_disorders'
                 elif 'adrenal' in col_lower: # 'adrenal' is quite unique
                     final_col = 'adrenal_and_thyroid_disorders'
                 elif 'blood' in col_lower and 'pressure' in col_lower:
                     final_col = 'blood_pressure_abnormality'
                 elif 'hemoglobin' in col_lower:
                     final_col = 'level_of_hemoglobin'
                 elif 'pedigree' in col_lower:
                     final_col = 'genetic_pedigree_coefficient'
                 elif 'salt' in col_lower and 'diet' in col_lower:
                     final_col = 'salt_content_in_the_diet'
                 elif 'alcohol' in col_lower and 'day' in col_lower:
                     final_col = 'alcohol_consumption_per_day'
                 # 'stress' alone can leverage existing column checks, but be careful
                 elif 'stress' in col_lower and 'level' in col_lower:
                     final_col = 'level_of_stress'
            
            # D. Fallback
            if not final_col:
                # Default normalization: snake_case
                # Replace spaces and special chars with underscores
                # This ensures distinct columns like 'alcohol consumption per day' don't get lost
                final_col = col_lower.replace(' ', '_')
            
            new_columns.append(final_col)
            mapping_log[str(col)] = final_col
        
        df.columns = new_columns
        return df, mapping_log

    def preprocess_patients_data(self, df: pd.DataFrame):
        df_clean = df.copy()
        
        # Handle values
        if 'pregnancy' in df_clean.columns and 'sex' in df_clean.columns:
            df_clean['pregnancy'] = df_clean.apply(
                lambda row: 0 if row['sex'] == 0 else row.get('pregnancy', 0),
                axis=1
            )
            df_clean['pregnancy'] = df_clean['pregnancy'].fillna(0)
        
        if 'alcohol_consumption_per_day' in df_clean.columns:
            median_val = df_clean['alcohol_consumption_per_day'].median()
            df_clean['alcohol_consumption_per_day'].fillna(median_val, inplace=True)
        
        if 'genetic_pedigree_coefficient' in df_clean.columns:
            median_val = df_clean['genetic_pedigree_coefficient'].median()
            df_clean['genetic_pedigree_coefficient'].fillna(median_val, inplace=True)
        
        if 'bmi' in df_clean.columns:
            mean_val = df_clean['bmi'].mean()
            df_clean['bmi'].fillna(mean_val, inplace=True)
        
        if 'smoking' in df_clean.columns:
            df_clean['smoking'].fillna(0, inplace=True)
        
        if 'salt_content_in_the_diet' in df_clean.columns:
            median_val = df_clean['salt_content_in_the_diet'].median()
            df_clean['salt_content_in_the_diet'].fillna(median_val, inplace=True)
        
        return df_clean
    
    def preprocess_activity_data(self, df: pd.DataFrame):
        df_clean = df.copy()
        
        if 'day_number' in df_clean.columns:
            df_clean = df_clean[df_clean['day_number'] > 0]
        
        if 'physical_activity' in df_clean.columns:
            median_val = df_clean['physical_activity'].median()
            df_clean['physical_activity'].fillna(median_val, inplace=True)
        
        return df_clean


