# 🧠 NeuroHealth Nexus: Architecture & Flow Diagrams

This document contains all the visual flowcharts and architecture diagrams for the NeuroHealth Nexus project.

---

## 1. High-Level System Architecture

This diagram shows the overall system architecture with the three main layers: UI, Intelligence, and Data.

![System Architecture](diagrams/1_system_architecture.png)

**Description:** The architecture is built in layers. The Streamlit UI communicates with the LangChain Orchestrator, which coordinates between the Groq LLM for inference and the dual data sources (Supabase for persistent cloud storage and DuckDB for in-memory session data).

---

## 2. Data Ingestion & Preprocessing Pipeline

This flowchart illustrates how uploaded files are processed, normalized, and validated before being stored.

![Data Ingestion Pipeline](diagrams/2_data_ingestion_pipeline.png)

**Description:** The preprocessing engine scans the first 10 rows to detect headers, applies fuzzy matching to normalize column names (e.g., "Body Mass" → "bmi"), validates the schema, and stores valid data in the session database.

---

## 3. Multi-Source Query Execution Flow

This diagram shows how a single SQL query is executed across both Supabase and DuckDB, then merged and re-aggregated.

![Multi-Source Execution](diagrams/3_multi_source_execution.png)

**Description:** The Multi-Source Query Executor receives a standard SQL query, splits it to execute on both Supabase (cloud) and DuckDB (local), adapts table names dynamically, merges the results, and re-aggregates metrics mathematically to produce a unified result.

---

## 4. AI Agent Workflow (Complete Process)

This comprehensive diagram shows the entire agent workflow from user query to final insight.

![Agent Workflow](diagrams/4_agent_workflow.png)

**Description:** The advanced agent workflow employs a "Decomposer-Executor-Insight" pattern. 
1. **Decomposition Agent**: Breaks down complex user queries into a logical plan of analytical steps.
2. **SQL Generator Agent**: Generates specific, safe SQL queries for each step.
3. **Multi-Source Query Executor**: Executes these queries against both Supabase (cloud) and DuckDB (session files).
4. **Insights Agent**: Synthesizes the results into a strategic narrative with actionable recommendations.

---

## 5. Privacy & Safety Audit Layer (Detailed)

This diagram focuses specifically on the audit layer's decision-making process.

![Audit Layer](diagrams/5_audit_layer.png)

**Description:** The audit layer implements multiple safety checks: blocks SELECT * queries, prevents PII column access, requires aggregation functions, and blocks dangerous SQL operations (DROP, DELETE, UPDATE, etc.).

---

## 6. End-to-End User Journey

This diagram shows the complete user journey from login to insight generation.

![User Journey](diagrams/6_user_journey.png)

**Description:** Users open the app, connect to the database, and can choose to upload files, explore modules, or ask natural language questions. All paths converge at the visualization layer, which displays the final insights.

---

## 7. Module Architecture

This diagram shows the three main modules and their relationships.

![Module Architecture](diagrams/7_module_architecture.png)

**Description:** The main application orchestrates three modules: Clinical Command Center (reactive care), Proactive Life Engine (preventive wellness), and Strategic Intelligence (AI-powered queries). All modules access the database layer and use the visualization layer for output.

---

## Usage Notes

**For presentations:**
1. All diagrams are available as PNG files in the `diagrams/` folder
2. Simply insert these images into PowerPoint/Google Slides
3. Images are high-resolution and suitable for projection

**Regenerating diagrams:**
- Run `python generate_diagrams.py` to create .mmd files
- Run `python convert_to_png.py` to convert to PNG images
