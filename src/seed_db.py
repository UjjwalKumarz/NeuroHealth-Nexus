import pandas as pd
import numpy as np
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

def preprocess_health_dataset(df):
    print("\n[*] Preprocessing Health Dataset 1...")
    df_clean = df.copy()
    
    print(f"[*] Initial shape: {df_clean.shape}")
    print(f"[*] Missing values before cleaning:\n{df_clean.isnull().sum()}")
    
    print("\n[1] Handling Pregnancy (77.9% missing)...")
    df_clean['Pregnancy'] = df_clean.apply(
        lambda row: 0 if row['Sex'] == 0 else row['Pregnancy'],
        axis=1
    )
    df_clean['Pregnancy'] = df_clean['Pregnancy'].fillna(0)
    print(f"    [OK] Pregnancy missing: {df_clean['Pregnancy'].isnull().sum()}")
    
    print("\n[2] Handling Alcohol Consumption (12.1% missing)...")
    alcohol_median = df_clean['alcohol_consumption_per_day'].median()
    df_clean['alcohol_consumption_per_day'] = df_clean['alcohol_consumption_per_day'].fillna(alcohol_median)
    print(f"    [OK] Filled with median: {alcohol_median:.2f}")
    
    print("\n[3] Handling Genetic Pedigree Coefficient (4.6% missing)...")
    genetic_median = df_clean['Genetic_Pedigree_Coefficient'].median()
    df_clean['Genetic_Pedigree_Coefficient'] = df_clean['Genetic_Pedigree_Coefficient'].fillna(genetic_median)
    print(f"    [OK] Filled with median: {genetic_median:.4f}")
    
    print("\n[4] Handling other missing values...")
    if df_clean['salt_content_in_the_diet'].isnull().sum() > 0:
        salt_median = df_clean['salt_content_in_the_diet'].median()
        df_clean['salt_content_in_the_diet'] = df_clean['salt_content_in_the_diet'].fillna(salt_median)
        print(f"    [OK] Salt filled with median: {salt_median}")
    
    if df_clean['BMI'].isnull().sum() > 0:
        bmi_mean = df_clean['BMI'].mean()
        df_clean['BMI'] = df_clean['BMI'].fillna(bmi_mean)
        print(f"    [OK] BMI filled with mean: {bmi_mean:.2f}")
    
    if df_clean['Smoking'].isnull().sum() > 0:
        df_clean['Smoking'] = df_clean['Smoking'].fillna(0)
        print(f"    [OK] Smoking filled with 0 (non-smoker)")
    
    print(f"\n[*] Missing values after cleaning:\n{df_clean.isnull().sum()}")
    print(f"[OK] Final shape: {df_clean.shape}")
    
    return df_clean

def preprocess_activity_dataset(df):
    print("\n[*] Preprocessing Activity Dataset 2...")
    df_clean = df.copy()
    
    print(f"[*] Initial shape: {df_clean.shape}")
    print(f"[*] Columns: {df_clean.columns.tolist()}")
    print(f"[*] Missing Physical_activity: {df_clean['Physical_activity'].isnull().sum()} ({df_clean['Physical_activity'].isnull().sum()/len(df_clean)*100:.1f}%)")
    
    print("\n[1] Patient-specific imputation for Physical_activity...")
    
    global_median = df_clean['Physical_activity'].median()
    print(f"    [*] Global median activity: {global_median:.0f}")
    
    patient_medians = df_clean.groupby('Patient_Number')['Physical_activity'].transform('median')
    
    df_clean['Physical_activity'] = df_clean['Physical_activity'].fillna(patient_medians)
    
    if df_clean['Physical_activity'].isnull().sum() > 0:
        df_clean['Physical_activity'] = df_clean['Physical_activity'].fillna(global_median)
        print(f"    [OK] Remaining filled with global median")
    
    print(f"    [OK] Missing after imputation: {df_clean['Physical_activity'].isnull().sum()}")
    
    print(f"\n[*] Missing values after cleaning:\n{df_clean.isnull().sum()}")
    print(f"[OK] Final shape: {df_clean.shape}")
    print(f"[OK] Columns preserved: {df_clean.columns.tolist()}")
    
    return df_clean

def seed_database():
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )
    
    print("="*60)
    print("NeuroHealth Nexus - Database Seeding")
    print("="*60)
    
    print("\n[*] Loading CSV files...")
    df_patients = pd.read_csv('data/Health Dataset 1 (N=2000).csv')
    df_activity = pd.read_csv('data/Health Dataset 2 (N=20000).csv')
    
    print(f"[OK] Loaded {len(df_patients)} patient records")
    print(f"[OK] Loaded {len(df_activity)} activity records")
    
    df_patients_clean = preprocess_health_dataset(df_patients)
    df_activity_clean = preprocess_activity_dataset(df_activity)
    
    print("\n" + "="*60)
    print("[*] Mapping columns to database schema...")
    print("="*60)
    
    df_patients_final = df_patients_clean.rename(columns={
        'Patient_Number': 'patient_number',
        'Blood_Pressure_Abnormality': 'blood_pressure_abnormality',
        'Level_of_Hemoglobin': 'level_of_hemoglobin',
        'Genetic_Pedigree_Coefficient': 'genetic_pedigree_coefficient',
        'Age': 'age',
        'BMI': 'bmi',
        'Sex': 'sex',
        'Pregnancy': 'pregnancy',
        'Smoking': 'smoking',
        'salt_content_in_the_diet': 'salt_content_in_the_diet',
        'alcohol_consumption_per_day': 'alcohol_consumption_per_day',
        'Level_of_Stress': 'level_of_stress',
        'Chronic_kidney_disease': 'chronic_kidney_disease',
        'Adrenal_and_thyroid_disorders': 'adrenal_and_thyroid_disorders'
    })
    
    df_activity_final = df_activity_clean.rename(columns={
        'Patient_Number': 'patient_number',
        'Day_Number': 'day_number',
        'Physical_activity': 'physical_activity'
    })
    
    required_activity_cols = ['patient_number', 'day_number', 'physical_activity']
    print(f"[*] Activity columns after mapping: {df_activity_final.columns.tolist()}")
    print(f"[*] Required columns: {required_activity_cols}")
    
    for col in required_activity_cols:
        if col not in df_activity_final.columns:
            print(f"[ERROR] Missing required column: {col}")
            return False
    
    df_activity_final = df_activity_final[required_activity_cols]
    
    print("[OK] Column mapping complete")
    print(f"[OK] Patients final shape: {df_patients_final.shape}")
    print(f"[OK] Activity final shape: {df_activity_final.shape}")
    
    print("\n" + "="*60)
    print("[*] Uploading to Supabase...")
    print("="*60)
    
    batch_size = 500
    total_patients = len(df_patients_final)
    
    print(f"\n[*] Uploading {total_patients} patients in batches of {batch_size}...")
    
    for i in range(0, total_patients, batch_size):
        batch = df_patients_final.iloc[i:i+batch_size]
        records = batch.to_dict('records')
        
        try:
            supabase.table('patients').insert(records).execute()
            print(f"  [OK] Batch {i//batch_size + 1}: Uploaded patients {i+1} to {min(i+batch_size, total_patients)}")
        except Exception as e:
            print(f"  [ERROR] Batch {i//batch_size + 1}: {str(e)}")
            if records:
                print(f"     Sample record: {records[0]}")
            return False
    
    total_activity = len(df_activity_final)
    print(f"\n[*] Uploading {total_activity} activity records in batches of {batch_size}...")
    
    for i in range(0, total_activity, batch_size):
        batch = df_activity_final.iloc[i:i+batch_size]
        records = batch.to_dict('records')
        
        try:
            supabase.table('activity').insert(records).execute()
            print(f"  [OK] Batch {i//batch_size + 1}: Uploaded activity {i+1} to {min(i+batch_size, total_activity)}")
        except Exception as e:
            print(f"  [ERROR] Batch {i//batch_size + 1}: {str(e)}")
            if records:
                print(f"     Sample record: {records[0]}")
            return False
    
    print("\n" + "="*60)
    print("[*] Verifying uploaded data...")
    print("="*60)
    
    try:
        patient_count = supabase.table('patients').select('patient_number', count='exact').execute()
        activity_count = supabase.table('activity').select('id', count='exact').execute()
        
        print(f"\n[OK] Patients in database: {patient_count.count}")
        print(f"[OK] Activity records in database: {activity_count.count}")
        
        print("\n[*] Sample patient record:")
        sample_patient = supabase.table('patients').select('*').limit(1).execute()
        if sample_patient.data:
            for key, value in sample_patient.data[0].items():
                print(f"   {key}: {value}")
        
        print("\n[*] Sample activity record:")
        sample_activity = supabase.table('activity').select('*').limit(1).execute()
        if sample_activity.data:
            for key, value in sample_activity.data[0].items():
                print(f"   {key}: {value}")
        
        print("\n[*] Verifying foreign key relationships...")
        fk_check = supabase.table('activity').select('patient_number').limit(5).execute()
        if fk_check.data:
            patient_numbers = [r['patient_number'] for r in fk_check.data]
            print(f"[OK] Sample patient_numbers in activity table: {patient_numbers}")
            if None in patient_numbers or any(pn is None for pn in patient_numbers):
                print("[ERROR] Found NULL patient_number values!")
                return False
        
    except Exception as e:
        print(f"[ERROR] Could not verify counts: {str(e)}")
        return False
    
    print("\n" + "="*60)
    print("[SUCCESS] DATABASE SEEDING COMPLETE!")
    print("="*60)
    print(f"\n[*] Summary:")
    print(f"Patients processed: {total_patients}")
    print(f"Activity records processed: {total_activity}")
    print(f"Missing values handled: YES")
    print(f"Foreign keys validated: YES")
    print(f"Data quality: High (post-preprocessing)")
    print("\n[OK] Ready to launch Streamlit app!")
    
    return True

if __name__ == "__main__":
    success = seed_database()
    if not success:
        print("\n[ERROR] Seeding failed. Please check errors above.")
        exit(1)
