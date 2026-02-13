# NeuroHealth Nexus - Environment Setup

## 🔐 Required: Create .env File

Before running the seeding script, you need to create a `.env` file with your Supabase credentials.

### Step 1: Create `.env` file

Create a new file named `.env` in the `NeuroHealth_Nexus` directory with the following content:

```env
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

### Step 2: Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Click on **Settings** (gear icon) in the left sidebar
3. Click on **API**
4. Copy the following:
   - **Project URL** → paste as `SUPABASE_URL`
   - **anon/public key** → paste as `SUPABASE_KEY`

### Step 3: Get Your Groq API Key

1. Go to [console.groq.com](https://console.groq.com/)
2. Sign in or create an account
3. Go to **API Keys**
4. Create a new API key
5. Copy the key → paste as `GROQ_API_KEY`

### Step 4: Run the Seeding Script

After creating the `.env` file with your credentials, run:

```bash
python src/seed_db.py
```

## ✅ What the Seeding Script Does

The script will:
1. ✅ Load CSV files
2. ✅ Preprocess data based on audit report findings:
   - Handle Pregnancy missing values (77.9%) - conditional imputation
   - Handle Alcohol missing values (12.1%) - median imputation
   - Handle Genetic Pedigree missing values (4.6%) - median imputation
   - Handle Physical Activity missing values (19.2%) - patient-specific median
3. ✅ Upload to Supabase in batches
4. ✅ Verify data integrity

## 📊 Expected Output

You should see:
- Preprocessing statistics
- Upload progress for patients (4 batches of 500)
- Upload progress for activity (40 batches of 500)
- Verification counts
- Sample records

Total time: ~2-5 minutes depending on internet speed.
