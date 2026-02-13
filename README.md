# 🧠 NeuroHealth Nexus

A privacy-preserving health analytics platform powered by GenAI and multi-agent architecture.

## 🌟 Features

### 🏥 Clinical Command Center
- **Reactive Care & Disease Monitoring**
- Patient demographics visualization
- Disease cohort analysis
- High-risk patient identification and triage

### 💪 Proactive Life Engine
- **Preventive Wellness & Lifestyle Optimization**
- Lifestyle risk modeling with what-if scenarios
- Physical activity trend analysis with interactive filters
- Stress level management insights

### 📊 Strategic Health Intelligence
- **Advanced Multi-Agent Reasoning**: Decomposes complex questions into multi-step analytical plans.
- **Natural Language Insights**: Returns strategic narratives and actionable recommendations, not just raw data.
- **Federated Execution**: Seamlessly joins secure cloud data (Supabase) with local uploaded files (DuckDB) in-memory.
- **Compliance Guardrails**: Dedicated AI agent audits every query for safety and privacy before execution.
- **Population Analytics**: Dynamic cohort segmentation and risk heatmaps.

## 🔒 Privacy Protection

All data displayed is **aggregated and anonymized**. The platform implements:
- **LLM-Based Compliance Auditing**: Context-aware blocking of unsafe queries.
- **Local Data Isolation**: Uploaded files are processed locally via DuckDB and never sent to the cloud.
- Aggregation-only data access
- PII protection mechanisms

## 🚀 Deployment

### Prerequisites
- Python 3.8+
- Supabase account
- Groq API key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd NeuroHealth_Nexus
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your credentials:
     ```
     GROQ_API_KEY=your_groq_api_key
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     ```

5. **Set up database**
   - Create a Supabase project
   - Run the SQL schema from `supabase_schema.sql`
   - Seed the database (optional):
     ```bash
     python -m src.seed_db
     ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. **Push to GitHub**
   - Ensure all files are committed
   - Push to your GitHub repository

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository, branch, and `app.py`
   - Add secrets in the Streamlit Cloud dashboard:
     ```toml
     [supabase]
     url = "your_supabase_url"
     key = "your_supabase_key"
     
     [groq]
     api_key = "your_groq_api_key"
     ```
   - Click "Deploy"

## 📁 Project Structure

```
NeuroHealth_Nexus/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   └── secrets.toml               # Local secrets (not in git)
├── src/
│   ├── agents.py                  # AI agent workflow (Decomposer, SQL Gen, Compliance, Insights)
│   ├── db_manager.py              # Database connection manager
│   ├── query_executor.py          # Federated Execution (Supabase + DuckDB)
│   ├── session_db.py              # DuckDB session manager
│   ├── visualizer.py              # Chart creation functions
│   ├── ui_components.py           # Reusable UI components
│   └── seed_db.py                 # Database seeding script
├── data/
│   └── *.csv                      # Sample health datasets
├── supabase_schema.sql            # Database schema
├── SETUP_INSTRUCTIONS.md          # Detailed setup guide
└── PRIVACY.md                     # Privacy implementation details
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Database**: Supabase (PostgreSQL) + DuckDB (Local Session)
- **AI/LLM**: Groq (Qwen 3 32B)
- **Agent Framework**: LangChain
- **Data Processing**: Pandas, NumPy

## 📊 Database Schema

The platform uses two main tables:
- **patients**: Patient demographics and health conditions
- **activity**: Daily physical activity tracking

See `SCHEMA_README.md` for detailed schema information.

## 🤝 Contributing

This is a case study project for Infogain. For questions or suggestions, please contact the project maintainer.

## 📄 License

This project is developed as a part of Infogain's case study.

## ⚠️ Disclaimer

This application is for demonstration and educational purposes only. It should not be used for actual medical diagnosis or treatment decisions.
