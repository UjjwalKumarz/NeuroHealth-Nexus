# 📋 Streamlit Cloud Deployment Checklist

## Pre-Deployment Checklist

### ✅ Files to Include in GitHub Repository

- [x] `app.py` - Main application file
- [x] `requirements.txt` - All Python dependencies
- [x] `.streamlit/config.toml` - Streamlit configuration
- [x] `src/` folder - All source code files
  - [x] `agents.py`
  - [x] `db_manager.py`
  - [x] `visualizer.py`
  - [x] `ui_components.py`
  - [x] `seed_db.py`
- [x] `data/` folder - CSV datasets (optional)
- [x] `supabase_schema.sql` - Database schema
- [x] `README.md` - Project documentation
- [x] `.gitignore` - Exclude sensitive files
- [x] `.env.example` - Template for environment variables
- [x] Documentation files:
  - [x] `SETUP_INSTRUCTIONS.md`
  - [x] `PRIVACY.md`
  - [x] `SCHEMA_README.md`

### ❌ Files to EXCLUDE from GitHub (via .gitignore)

- [ ] `.env` - Contains actual secrets
- [ ] `.streamlit/secrets.toml` - Local secrets file
- [ ] `__pycache__/` - Python cache
- [ ] `.venv/` - Virtual environment
- [ ] `temp_doc_content.txt` - Temporary files

## Deployment Steps

### 1. Prepare Supabase Database

- [ ] Create Supabase project at [supabase.com](https://supabase.com)
- [ ] Run `supabase_schema.sql` in SQL Editor
- [ ] Create the `execute_sql` function (if not in schema):
  ```sql
  CREATE OR REPLACE FUNCTION execute_sql(query_text TEXT)
  RETURNS JSON
  LANGUAGE plpgsql
  SECURITY DEFINER
  AS $$
  DECLARE
    result JSON;
  BEGIN
    EXECUTE 'SELECT json_agg(row_to_json(t)) FROM (' || query_text || ') t' INTO result;
    RETURN result;
  END;
  $$;
  ```
- [ ] Seed database with sample data (run `python -m src.seed_db` locally)
- [ ] Copy Supabase URL and anon key

### 2. Get Groq API Key

- [ ] Sign up at [console.groq.com](https://console.groq.com)
- [ ] Create API key
- [ ] Copy API key for later use

### 3. Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - NeuroHealth Nexus"

# Add remote repository
git remote add origin <your-github-repo-url>

# Push to GitHub
git push -u origin main
```

### 4. Deploy on Streamlit Cloud

- [ ] Go to [share.streamlit.io](https://share.streamlit.io)
- [ ] Sign in with GitHub account
- [ ] Click **"New app"**
- [ ] Configure deployment:
  - **Repository**: Select your GitHub repository
  - **Branch**: `main` (or your default branch)
  - **Main file path**: `app.py`
  - **App URL**: Choose a custom URL (optional)

### 5. Configure Secrets in Streamlit Cloud

Click on **"Advanced settings"** → **"Secrets"** and add:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-supabase-anon-key"

[groq]
api_key = "your-groq-api-key"
```

**Important**: Replace with your actual credentials!

### 6. Deploy

- [ ] Click **"Deploy!"**
- [ ] Wait for deployment to complete (2-5 minutes)
- [ ] Check deployment logs for any errors

## Post-Deployment Verification

### Test Core Features

- [ ] App loads successfully
- [ ] Database connection works (check sidebar status)
- [ ] **Clinical Command Center** module:
  - [ ] Metrics display correctly
  - [ ] Charts render properly
  - [ ] Disease cohort analysis works
  - [ ] Patient triage functions
- [ ] **Proactive Life Engine** module:
  - [ ] What-if scenarios calculate
  - [ ] Activity analysis with filters works
  - [ ] Stress management displays data
- [ ] **Strategic Intelligence** module:
  - [ ] Natural language queries work
  - [ ] Population insights display
  - [ ] Heatmaps render correctly

### Check for Errors

- [ ] No errors in Streamlit Cloud logs
- [ ] All visualizations load
- [ ] Database queries execute successfully
- [ ] AI agent responses work

## Troubleshooting Common Issues

### Database Connection Failed

**Problem**: "Database Connection Failed" in sidebar

**Solutions**:
1. Verify Supabase URL and key in secrets
2. Check if `execute_sql` function exists in Supabase
3. Ensure database tables are created
4. Check Supabase project is active

### Module Import Errors

**Problem**: `ModuleNotFoundError` or import errors

**Solutions**:
1. Verify all dependencies in `requirements.txt`
2. Check for typos in package names
3. Ensure version compatibility
4. Redeploy the app

### AI Query Not Working

**Problem**: Natural language queries fail

**Solutions**:
1. Verify Groq API key in secrets
2. Check API key is valid and has credits
3. Review error messages in logs
4. Test with simple queries first

### Secrets Not Loading

**Problem**: Environment variables not found

**Solutions**:
1. Use `st.secrets` instead of `os.getenv()` in Streamlit Cloud
2. Verify secrets format in dashboard
3. Ensure no extra spaces in TOML format
4. Redeploy after updating secrets

## Code Modifications for Streamlit Cloud

If you encounter issues with environment variables, update the code to use Streamlit secrets:

**In `src/db_manager.py` and `src/agents.py`:**

```python
import streamlit as st

# Instead of:
# self.url = os.getenv('SUPABASE_URL')

# Use:
try:
    self.url = st.secrets["supabase"]["url"]
    self.key = st.secrets["supabase"]["key"]
except:
    # Fallback to .env for local development
    self.url = os.getenv('SUPABASE_URL')
    self.key = os.getenv('SUPABASE_KEY')
```

## Maintenance

### Updating the App

```bash
# Make changes locally
git add .
git commit -m "Description of changes"
git push origin main
```

Streamlit Cloud will automatically redeploy on push!

### Monitoring

- [ ] Check app usage in Streamlit Cloud dashboard
- [ ] Monitor Supabase database usage
- [ ] Track Groq API usage and credits

## Security Notes

- ✅ Never commit `.env` or `secrets.toml` to GitHub
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Rotate API keys if accidentally exposed
- ✅ Use Supabase Row Level Security (RLS) for production
- ✅ Review privacy audit logs regularly

---

**Ready to Deploy?** Follow the checklist step by step! 🚀
