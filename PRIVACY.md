# Privacy & Security Implementation

## Overview
NeuroHealth Nexus implements a **Privacy-First Architecture** ensuring that no raw patient data is exposed through the application interface or AI queries.

## Privacy Principles

### 1. No Raw Data Exposure
- **Prohibited**: `SELECT * FROM patients`
- **Prohibited**: Individual patient records with identifiable information
- **Required**: All queries must return aggregated statistics only

### 2. Compliance Auditor Agent (LLM-Based)
The **Compliance Agent** (`src/agents.py`) uses a specialized LLM prompt to review every generated SQL query *before* execution. Unlike simple keyword blocking, it understands context to ensure:
- **Context-Aware Safety**: Distinguishes between safe aggregations and unsafe raw data access.
- **Privacy Enforcement**: Blocks queries that attempt to infer PII even without explicit column selection.
- **Strict Read-Only**: Ensures no state-changing commands (`DROP`, `INSERT`) are ever executed.

#### Blocked Patterns:
- ✗ `SELECT *` - Exposes all raw columns
- ✗ `SELECT patient_number, age, bmi FROM patients LIMIT 100` - Individual records
- ✗ Dangerous operations: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE
- ✗ PII columns without aggregation: name, email, ssn, phone

#### Allowed Patterns:
- ✓ `SELECT COUNT(*) FROM patients WHERE chronic_kidney_disease = 1`
- ✓ `SELECT AVG(age), AVG(bmi) FROM patients GROUP BY sex`
- ✓ `SELECT age, COUNT(*) as patient_count FROM patients GROUP BY age`

### 3. Federated Data Privacy (Supabase + Local Files)
The **Federated Query Executor** (`src/query_executor.py`) allows analysis of uploaded local files (Excel/CSV) combined with Supabase data *without* compromising privacy:

1.  **Local Processing**: Uploaded files are processed in-memory using **DuckDB**. Raw data from these files is **NEVER** uploaded to the cloud database or sent to the LLM.
2.  **Schema Only**: Only the *column names* (schema) are shared with the AI to generate queries.
3.  **Secure Joining**: Data joining happens locally in the application's memory space, ensuring that your private local datasets remain private.

### 4. Data Aggregation Requirements

All visualizations and statistics must use aggregated data:

**Example - Age Distribution:**
```sql
-- ✓ CORRECT: Aggregated
SELECT 
    age,
    COUNT(*) as patient_count
FROM patients
GROUP BY age
ORDER BY age

-- ✗ WRONG: Raw data
SELECT age FROM patients LIMIT 1000
```

**Example - Risk Analysis:**
```sql
-- ✓ CORRECT: Aggregated statistics
SELECT 
    risk_score,
    COUNT(*) as patient_count,
    AVG(age) as avg_age,
    AVG(bmi) as avg_bmi
FROM patients
GROUP BY risk_score

-- ✗ WRONG: Individual patient records
SELECT 
    patient_number,
    age,
    bmi,
    risk_score
FROM patients
LIMIT 100
```

## Implementation Details

### App-Level Privacy Controls

**File: `app.py`**

1. **Clinical Command Center**
   - Demographics: Aggregated age/BMI distributions
   - Disease Cohorts: Statistical summaries (AVG, COUNT)
   - Patient Triage: Risk score distributions (no patient_number)

2. **Proactive Life Engine**
   - Activity Analysis: Daily aggregated averages
   - Stress Management: Grouped statistics

3. **Strategic Intelligence**
   - Natural Language Queries: **Audited by LLM Compliance Agent**
   - Population Metrics: Aggregated counts and percentages
   - Risk Heatmap: Categorized age groups and BMI ranges

### Agent-Level Privacy Controls

**File: `src/agents.py`**

The `agent_workflow` enforces a strict pipeline:
1.  **Decomposition**: Breaks down the user's intent.
2.  **SQL Generation**: Generates a candidate query.
3.  **Compliance Check**: A dedicated LLM step reviews the query against HIPAA/GDPR rules. **If this step fails, the query is blocked immediately.**
4.  **Execution**: Only approved queries reach the `MultiSourceQueryExecutor`.

### Visualization Privacy

**File: `src/ui_components.py` & `src/visualizer.py`**

All visualization functions accept aggregated data:
- `create_age_distribution(df)` - Expects: age, patient_count
- `create_bmi_distribution(df)` - Expects: bmi, patient_count
- `create_disease_prevalence(df)` - Expects: ckd_count, thyroid_count, bp_count

## Privacy Notices

### User-Facing Notices

1. **Sidebar Banner:**
   ```
   🔒 Privacy Protected
   All data displayed is aggregated.
   No individual patient records are exposed.
   ```

2. **Medical Disclaimer:**
   ```
   Medical Disclaimer: This tool is for informational purposes only 
   and should not be used as a substitute for professional medical 
   advice, diagnosis, or treatment.
   ```

3. **Natural Language Query Info Box:**
   ```
   The AI will generate SQL queries and return aggregated insights 
   while protecting patient privacy.
   ```

## Testing Privacy Compliance

### Test Cases

**Test 1: Block SELECT ***
```python
sql = "SELECT * FROM patients"
result = audit_query(sql)
assert result['safe'] == False
assert "SELECT *" in result['reason']
```

**Test 2: Block LIMIT without Aggregation**
```python
sql = "SELECT age, bmi FROM patients LIMIT 100"
result = audit_query(sql)
assert result['safe'] == False
assert "LIMIT" in result['reason']
```

**Test 3: Allow Aggregated Query**
```python
sql = "SELECT AVG(age), COUNT(*) FROM patients WHERE chronic_kidney_disease = 1"
result = audit_query(sql)
assert result['safe'] == True
```

**Test 4: Block Individual Patient Numbers**
```python
sql = "SELECT patient_number, age FROM patients WHERE age > 50"
result = audit_query(sql)
assert result['safe'] == False
assert "patient_number" in result['reason']
```

## Compliance Checklist

- [x] No `SELECT *` queries in application
- [x] No individual patient_number exposure
- [x] All visualizations use aggregated data
- [x] Compliance Auditor blocks raw data queries
- [x] Privacy notices displayed to users
- [x] Medical disclaimer included
- [x] LIMIT clause requires aggregation
- [x] PII columns protected
- [x] Dangerous SQL operations blocked

## Future Enhancements

1. **Row-Level Security (RLS)** in Supabase
2. **Audit Logging** for all queries
3. **Data Anonymization** for exported results
4. **Role-Based Access Control (RBAC)**
5. **Differential Privacy** for statistical queries

## References

- HIPAA Compliance Guidelines
- GDPR Data Protection Requirements
- Healthcare Data Privacy Best Practices
- Supabase Row Level Security Documentation
