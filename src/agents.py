import os
import pandas as pd
import json
import re
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
try:
    import streamlit as st
    groq_api_key = st.secrets["groq"]["api_key"]
except:
    groq_api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    api_key=groq_api_key
)

# --- Pydantic Models for Structured Output ---

class QueryStep(BaseModel):
    step_id: int = Field(description="Step number")
    description: str = Field(description="Description of what this step analyzes")
    needed_columns: List[str] = Field(description="List of columns needed for this analysis")

class DecompositionPlan(BaseModel):
    steps: List[QueryStep] = Field(description="List of analytical steps to answer the user query")

class SQLQuery(BaseModel):
    sql: str = Field(description="The SQL query to execute")
    explanation: str = Field(description="Brief explanation of the query logic")

class ComplianceReview(BaseModel):
    allowed: bool = Field(description="Whether the query is safe to execute")
    reason: str = Field(description="Reason for allowing or rejecting the query")

class InsightOutput(BaseModel):
    summary: str = Field(description="Direct answer to the user's question")
    key_insights: List[str] = Field(description="Bulleted list of interesting findings from the data")
    recommendations: List[str] = Field(description="Actionable recommendations based on the findings")

# --- Prompts & Parsers ---

decomposition_parser = JsonOutputParser(pydantic_object=DecompositionPlan)
sql_parser = JsonOutputParser(pydantic_object=SQLQuery)
compliance_parser = JsonOutputParser(pydantic_object=ComplianceReview)
insight_parser = JsonOutputParser(pydantic_object=InsightOutput)

decomposition_prompt = ChatPromptTemplate.from_template("""
You are a Senior Healthcare Data Analyst.
Your task is to break down a complex user query into simple, logical analytical steps that can be executed via SQL.

User Query: {query}

Data Schema:
Table: patients
- patient_number (INT)
- age, bmi, sex, pregnancy, smoking, alcohol_consumption_per_day
- blood_pressure_abnormality, chronic_kidney_disease, adrenal_and_thyroid_disorders
- level_of_hemoglobin, genetic_pedigree_coefficient, level_of_stress, salt_content_in_the_diet

Table: activity
- patient_number (INT)
- day_number, physical_activity

Instructions:
1. Break the query into distinct parts if it asks about multiple things (e.g., "avg BMI" AND "activity trends").
2. Each step should result in a specific dataset or metric.
3. Return the plan as a JSON object with a list of steps.

Format Instructions:
{format_instructions}

IMPORTANT: Return ONLY the JSON object. Do not add any explanation or text outside the JSON.
""")

sql_gen_prompt = ChatPromptTemplate.from_template("""
You are a PostgreSQL Expert. Generate a SQL query for the following task.

Task: {step_description}

Database Schema:
- Table `patients`: patient_number, age, bmi, sex (0=M,1=F), pregnancy, smoking (0=No,1=Yes), alcohol_consumption_per_day, blood_pressure_abnormality (0/1), chronic_kidney_disease (0/1), adrenal_and_thyroid_disorders (0/1), level_of_stress (1=Low, 2=Normal, 3=High), salt_content_in_the_diet.
- Table `activity`: patient_number, day_number, physical_activity.

Constraints:
1. **Focus**: Generate SQL *ONLY* for the specific "Task" above. Do NOT address other parts of the original user request.
2. **Safety**: NEVER use `SELECT *`. Always select specific columns or aggregations.
3. **Aggregation**: Use AVG, COUNT, SUM, etc., unless listing specific IDs is requested (avoid if possible).
4. **Joins**: Use `LEFT JOIN` on `patient_number` if needed.
5. **Syntax**: Standard PostgreSQL.
6. **Output**: Return ONLY the SQL query in a JSON object.

Format Instructions:
{format_instructions}

IMPORTANT: Return ONLY the JSON object. No markdown formatting.
""")

compliance_prompt = ChatPromptTemplate.from_template("""
You are a strict HIPAA & GDPR Compliance Officer.
Review the following SQL query to ensure it meets safety and privacy standards for a healthcare application.

SQL Query: {sql}
Task Description: {step_description}

Rules:
1. **No Modification**: The query must NOT contain DROP, DELETE, INSERT, UPDATE, TRUNCATE, ALTER, GRANT.
2. **Privacy First**: 
   - `SELECT *` is STRICTLY FORBIDDEN.
   - Accessing PII (like patient names, if they existed) is forbidden.
   - `patient_number` is allowed ONLY for joins or specific cohort identification if functionality requires it, but Aggregations (COUNT, AVG) are preferred.
3. **Relevance**: The query must be relevant to the Task Description.

Output:
Return a JSON object with:
- "allowed": boolean (true/false)
- "reason": string (explanation of the decision)

Format Instructions:
{format_instructions}

IMPORTANT: Return ONLY the JSON object.
""")

insight_prompt = ChatPromptTemplate.from_template("""
You are a Chief Medical Officer and Data Scientist.
Analyze the following data results and answer the user's question with strategic insights and actionable recommendations.

User Query: {query}

Analytical Steps & Results:
{results_summary}

Instructions:
1. **Summary**: Provide a direct, data-backed answer to the question.
2. **Key Insights**: Highlight trends, correlations, or alarming stats.
3. **Recommendations**: Suggest clinical or lifestyle interventions based on the risk factors found (e.g., if high stress/smoking found, suggest cessation programs).
4. **Tone**: Professional, encouraging, and evidence-based.

Output Format: JSON with keys "summary", "key_insights" (list), "recommendations" (list).

Format Instructions:
{format_instructions}
""")

# --- Helper Functions ---

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Robustly extracts JSON from LLM output, handling <think> blocks and markdown.
    """
    try:
        # 1. Remove <think> blocks
        clean_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
        
        # 2. Try to find JSON block in markdown
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', clean_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
            
        # 3. Try to find the first outer-most JSON object
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = clean_text[start_idx:end_idx+1]
            return json.loads(json_str)
            
        # 4. Fallback: try loading the whole string
        return json.loads(clean_text)
        
    except Exception as e:
        print(f"JSON Parsing Error: {e}\nInput text: {text}")
        return {}

# --- Main Workflow ---

def agent_workflow(user_query: str, executor: Any, include_uploaded: bool = True) -> Dict[str, Any]:
    """
    Orchestrates the multi-step agent workflow with robust manual parsing.
    """
    results_accumulator = []
    step_infos = []
    
    try:
        # 1. Decomposition
        decomposer_chain = decomposition_prompt | llm | StrOutputParser()
        raw_plan = decomposer_chain.invoke({
            "query": user_query,
            "format_instructions": decomposition_parser.get_format_instructions()
        })
        
        plan_dict = extract_json_from_text(raw_plan)
        
        if not plan_dict or "steps" not in plan_dict:
             return {"success": False, "error": f"Failed to understand query. Raw output: {raw_plan}"}
             
        # Convert to objects
        try:
            steps = [QueryStep(**s) for s in plan_dict["steps"]]
            plan_obj = DecompositionPlan(steps=steps)
        except:
             return {"success": False, "error": "Failed to parse plan structure."}

        # 2. Execution Loop
        sql_chain = sql_gen_prompt | llm | StrOutputParser()
        compliance_chain = compliance_prompt | llm | StrOutputParser()
        
        combined_df = pd.DataFrame()
        
        for step in plan_obj.steps:
            # Generate SQL
            raw_sql_response = sql_chain.invoke({
                "step_description": step.description,
                "format_instructions": sql_parser.get_format_instructions()
            })
            
            sql_response = extract_json_from_text(raw_sql_response)
            sql = sql_response.get("sql", "").strip().rstrip(';')
            
            if not sql:
                 results_accumulator.append(f"Step {step.step_id} Failed: No SQL generated.\n")
                 continue
            
            # --- COMPLIANCE CHECK ---
            try:
                raw_compliance = compliance_chain.invoke({
                    "sql": sql,
                    "step_description": step.description,
                    "format_instructions": compliance_parser.get_format_instructions()
                })
                compliance_result = extract_json_from_text(raw_compliance)
                
                if not compliance_result.get("allowed", False):
                    reason = compliance_result.get("reason", "Unknown safety violation")
                    results_accumulator.append(f"Step {step.step_id} BLOCKED by Compliance Agent: {reason}\n")
                    continue
            except Exception as e:
                 # Fail safe: if compliance check fails, assume unsafe
                 results_accumulator.append(f"Step {step.step_id} Failed: Compliance Audit Error ({str(e)})\n")
                 continue
            
            # Execute
            try:
                # Use the passed flag
                df = executor.execute_combined_query(sql, include_uploaded=include_uploaded)
                
                step_infos.append({
                    "step": step.step_id,
                    "description": step.description,
                    "sql": sql,
                    "data": df
                })
                
                results_text = f"Step {step.step_id}: {step.description}\nSQL: {sql}\nResult Data:\n{df.to_string(index=False)}\n\n"
                results_accumulator.append(results_text)
                    
            except Exception as e:
                results_accumulator.append(f"Step {step.step_id} Failed: {str(e)}\n")

        # 3. Insights Generation
        insight_chain = insight_prompt | llm | StrOutputParser()
        raw_insight = insight_chain.invoke({
            "query": user_query,
            "results_summary": "".join(results_accumulator),
            "format_instructions": insight_parser.get_format_instructions()
        })
        
        final_insights = extract_json_from_text(raw_insight)
        
        return {
            "success": True,
            "insight": final_insights.get("summary", "No summary generated"),
            "key_insights": final_insights.get("key_insights", []),
            "recommendations": final_insights.get("recommendations", []),
            "steps": step_infos
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Workflow Error: {str(e)}"
        }
