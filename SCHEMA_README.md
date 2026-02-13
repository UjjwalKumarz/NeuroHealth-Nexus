# NeuroHealth Nexus - Corrected Database Schema

## Actual CSV Column Structure

### Health Dataset 1 (N=2000) - 14 Columns
```
Patient_Number, Blood_Pressure_Abnormality, Level_of_Hemoglobin, 
Genetic_Pedigree_Coefficient, Age, BMI, Sex, Pregnancy, Smoking, 
salt_content_in_the_diet, alcohol_consumption_per_day, Level_of_Stress, 
Chronic_kidney_disease, Adrenal_and_thyroid_disorders
```

### Health Dataset 2 (N=20000) - 3 Columns
```
Patient_Number, Day_Number, Physical_activity
```

## Supabase Schema Instructions

### Step 1: Copy the SQL Schema
Open the file `supabase_schema.sql` in this directory.

### Step 2: Execute in Supabase SQL Editor
1. Go to your Supabase project dashboard
2. Click on "SQL Editor" in the left sidebar
3. Click "New Query"
4. Paste the entire contents of `supabase_schema.sql`
5. Click "Run" to execute

### Step 3: Verify Tables Created
Run these verification queries:
```sql
SELECT COUNT(*) FROM patients;
SELECT COUNT(*) FROM activity;
SELECT * FROM patients LIMIT 5;
SELECT * FROM activity LIMIT 5;
```

### Step 4: Seed the Database
After creating the tables, run:
```bash
python src/seed_db.py
```

## Column Mappings

### Patients Table Mapping
| CSV Column | Database Column |
|------------|----------------|
| Patient_Number | patient_number |
| Blood_Pressure_Abnormality | blood_pressure_abnormality |
| Level_of_Hemoglobin | level_of_hemoglobin |
| Genetic_Pedigree_Coefficient | genetic_pedigree_coefficient |
| Age | age |
| BMI | bmi |
| Sex | sex |
| Pregnancy | pregnancy |
| Smoking | smoking |
| salt_content_in_the_diet | salt_content_in_the_diet |
| alcohol_consumption_per_day | alcohol_consumption_per_day |
| Level_of_Stress | level_of_stress |
| Chronic_kidney_disease | chronic_kidney_disease |
| Adrenal_and_thyroid_disorders | adrenal_and_thyroid_disorders |

### Activity Table Mapping
| CSV Column | Database Column |
|------------|----------------|
| Patient_Number | patient_number |
| Day_Number | day_number |
| Physical_activity | physical_activity |
