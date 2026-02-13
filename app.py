import streamlit as st
import pandas as pd
from src.db_manager import DatabaseManager
from src.agents import agent_workflow
from src.visualizer import (
    create_age_distribution,
    create_bmi_distribution,
    create_gender_distribution,
    create_disease_prevalence,
    create_activity_trend,
    create_stress_distribution,
    create_risk_heatmap
)
from src.ui_components import (
    render_metric_card,
    render_info_box,
    render_sql_display,
    render_disclaimer,
    render_query_result
)

st.set_page_config(
    page_title="NeuroHealth Nexus",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 60px;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 24px;
        color: #666;
        margin-bottom: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.sidebar.markdown("### 📋 Navigation")
    st.sidebar.markdown("---")
    
    try:
        db = DatabaseManager()
        st.sidebar.success("Database Connected")
    except Exception as e:
        st.sidebar.error(f"Database Connection Failed: {str(e)}")
        st.error("Unable to connect to database. Please check your configuration.")
        return
    
    module = st.sidebar.radio(
        "Select Module",
        [
            "🏥 Clinical Command Center",
            "💪 Proactive Life Engine",
            "📊 Strategic Intelligence"
        ],
        label_visibility="visible"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📤 Upload Data Sources")
    
    from src.session_db import SessionDatabaseManager
    from src.data_preprocessor import DataPreprocessor
    from src.file_reader import DataFileReader
    
    session_db = SessionDatabaseManager()
    preprocessor = DataPreprocessor()
    file_reader = DataFileReader()
    
    st.sidebar.markdown("#### 👥 Patients Data")
    patients_files = st.sidebar.file_uploader(
        "Upload Patients Files",
        type=file_reader.get_supported_formats(),
        accept_multiple_files=True,
        help="Upload one or more patients data files (CSV, Excel, JSON, TXT)",
        key="patients_upload"
    )
    
    if patients_files:
        for uploaded_file in patients_files:
            file_name = uploaded_file.name.rsplit('.', 1)[0].replace(' ', '_')
            
            if not session_db.table_exists(file_name):
                try:
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    sheet_msg = ""
                    
                    if file_ext in ['xlsx', 'xls']:
                        result = file_reader.read_file(uploaded_file)
                        df, file_info, sheet_names = result
                        df, file_info, _ = file_reader.read_file(uploaded_file, sheet_name=sheet_names[0])
                        if len(sheet_names) > 1:
                            sheet_msg = f" (Used sheet: '{sheet_names[0]}')"
                    else:
                        df, file_info = file_reader.read_file(uploaded_file)
                    
                    
                    # 1. Smart Header Detection
                    promoted_msg = ""
                    row_idx, df_promoted = preprocessor.find_best_header_row(df)
                    if row_idx != -1:
                        df = df_promoted
                        promoted_msg = f" (Auto-detected header at row {row_idx+1})"
                    
                    # 2. Normalize columns
                    df, mapping_log = preprocessor.normalize_columns(df)
                    
                    is_valid, msg = preprocessor.validate_patients_schema(df)
                    if is_valid:
                        df_clean = preprocessor.preprocess_patients_data(df)
                        session_db.create_table_from_df(df_clean, file_name, 'patients')
                        st.sidebar.success(f"✅ {uploaded_file.name}: {len(df_clean)} patients{sheet_msg}{promoted_msg}")
                        with st.sidebar.expander("🔍 Column Mapping Details"):
                            st.json(mapping_log)
                    else:
                        st.sidebar.error(f"❌ {uploaded_file.name}: {msg}")
                        st.sidebar.warning(f"Found columns: {list(df.columns)}")
                        with st.sidebar.expander("🔍 Column Mapping Details", expanded=True):
                            st.write("Original -> Mapped")
                            st.json(mapping_log)
                
                except Exception as e:
                    st.sidebar.error(f"❌ {uploaded_file.name}: {str(e)}")
    
    st.sidebar.markdown("#### 🏃 Activity Data")
    activity_files = st.sidebar.file_uploader(
        "Upload Activity Files",
        type=file_reader.get_supported_formats(),
        accept_multiple_files=True,
        help="Upload one or more activity data files (CSV, Excel, JSON, TXT)",
        key="activity_upload"
    )
    
    if activity_files:
        for uploaded_file in activity_files:
            file_name = uploaded_file.name.rsplit('.', 1)[0].replace(' ', '_')
            
            if not session_db.table_exists(file_name):
                try:
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    sheet_msg = ""
                    
                    if file_ext in ['xlsx', 'xls']:
                        result = file_reader.read_file(uploaded_file)
                        df, file_info, sheet_names = result
                        df, file_info, _ = file_reader.read_file(uploaded_file, sheet_name=sheet_names[0])
                        if len(sheet_names) > 1:
                            sheet_msg = f" (Used sheet: '{sheet_names[0]}')"
                    else:
                        df, file_info = file_reader.read_file(uploaded_file)
                    
                    # 1. Smart Header Detection
                    promoted_msg = ""
                    row_idx, df_promoted = preprocessor.find_best_header_row(df)
                    if row_idx != -1:
                        df = df_promoted
                        promoted_msg = f" (Auto-detected header at row {row_idx+1})"
                    
                    # 2. Normalize columns
                    df, mapping_log = preprocessor.normalize_columns(df)
                    
                    is_valid, msg = preprocessor.validate_activity_schema(df)
                    if is_valid:
                        df_clean = preprocessor.preprocess_activity_data(df)
                        session_db.create_table_from_df(df_clean, file_name, 'activity')
                        st.sidebar.success(f"✅ {uploaded_file.name}: {len(df_clean)} records{sheet_msg}{promoted_msg}")
                        with st.sidebar.expander("🔍 Column Mapping Details"):
                            st.json(mapping_log)
                    else:
                        st.sidebar.error(f"❌ {uploaded_file.name}: {msg}")
                        st.sidebar.warning(f"Found columns: {list(df.columns)}")
                        with st.sidebar.expander("🔍 Column Mapping Details", expanded=True):
                            st.write("Original -> Mapped")
                            st.json(mapping_log)
                
                except Exception as e:
                    st.sidebar.error(f"❌ {uploaded_file.name}: {str(e)}")
    
    
    uploaded_sources = session_db.get_uploaded_sources()
    
    # Toggle for including uploaded data in charts
    include_uploaded_data = False
    if uploaded_sources:
        st.sidebar.markdown("---")
        include_uploaded_data = st.sidebar.checkbox(
            "📊 Include Uploaded Data in Charts",
            value=True,
            help="When enabled, all charts will combine Supabase data with uploaded sources"
        )
        st.session_state['include_uploaded_data'] = include_uploaded_data
    
    if uploaded_sources:
        st.sidebar.markdown("**Loaded Sources:**")
        
        patients_sources = {k: v for k, v in uploaded_sources.items() if v['type'] == 'patients'}
        activity_sources = {k: v for k, v in uploaded_sources.items() if v['type'] == 'activity'}
        
        if patients_sources:
            st.sidebar.markdown("*👥 Patients:*")
            for table_name, info in patients_sources.items():
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    st.sidebar.caption(f"• {table_name} ({info['rows']} rows)")
                with col2:
                    if st.sidebar.button("🗑️", key=f"remove_{table_name}", help=f"Remove {table_name}"):
                        session_db.remove_table(table_name)
                        st.rerun()
        
        if activity_sources:
            st.sidebar.markdown("*🏃 Activity:*")
            for table_name, info in activity_sources.items():
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    st.sidebar.caption(f"• {table_name} ({info['rows']} rows)")
                with col2:
                    if st.sidebar.button("🗑️", key=f"remove_{table_name}", help=f"Remove {table_name}"):
                        session_db.remove_table(table_name)
                        st.rerun()
        
        if st.sidebar.button("🗑️ Clear All Sources", key="clear_all_btn", use_container_width=True):
            session_db.clear_all()
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "NeuroHealth Nexus is a privacy-preserving health analytics platform "
        "powered by GenAI and multi-agent architecture."
    )
    
    st.sidebar.markdown("---")
    st.sidebar.success(
        "🔒 **Privacy Protected**\n\n"
        "All data displayed is aggregated. "
        "No individual patient records are exposed."
    )
    
    if "Clinical" in module:
        module_clinical()
    elif "Proactive" in module:
        module_preventive()
    else:
        module_strategic()
    
    st.sidebar.markdown("---")
    render_disclaimer()

def module_clinical():
    st.markdown("<h1 style='text-align: center; margin-top: 0;'>🧠 NeuroHealth Nexus</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>🏥 Clinical Command Center - Reactive Care & Disease Monitoring</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    db = DatabaseManager()
    from src.query_executor import MultiSourceQueryExecutor
    executor = MultiSourceQueryExecutor()
    
    include_uploaded = st.session_state.get('include_uploaded_data', False)
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        total_patients = executor.execute_combined_query(
            "SELECT COUNT(*) as count FROM patients",
            include_uploaded=include_uploaded
        )
        ckd_patients = executor.execute_combined_query(
            "SELECT COUNT(*) as count FROM patients WHERE chronic_kidney_disease = 1",
            include_uploaded=include_uploaded
        )
        avg_age = executor.execute_combined_query(
            "SELECT AVG(age) as avg_age FROM patients",
            include_uploaded=include_uploaded
        )
        bp_patients = executor.execute_combined_query(
            "SELECT COUNT(*) as count FROM patients WHERE blood_pressure_abnormality = 1",
            include_uploaded=include_uploaded
        )
        
        with col1:
            render_metric_card("Total Patients", f"{total_patients['count'].iloc[0]:,}")
        with col2:
            render_metric_card("CKD Patients", f"{ckd_patients['count'].iloc[0]:,}")
        with col3:
            render_metric_card("Avg Age", f"{avg_age['avg_age'].iloc[0]:.1f} years")
        with col4:
            render_metric_card("BP Patients", f"{bp_patients['count'].iloc[0]:,}")
    except Exception as e:
        st.error(f"Error loading metrics: {str(e)}")
    
    st.markdown("---")
    
    # 1. Inject Custom CSS
    # This specific selector targets the tab labels
    css = '''
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.5rem; /* Adjust font size here */
            font-weight: bold; /* Optional: Make it bold */
        }
    </style>
    '''

    st.markdown(css, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Disease Cohorts", "🚨 Patient Triage"])
    
    with tab1:
        st.subheader("Patient Demographics")
        
        col1, col2, col3 = st.columns(3)
        
        try:
            # Privacy-preserving aggregated queries with grouped intervals
            age_dist_query = """
            SELECT 
                CASE 
                    WHEN age < 30 THEN '< 30'
                    WHEN age < 40 THEN '30-39'
                    WHEN age < 50 THEN '40-49'
                    WHEN age < 60 THEN '50-59'
                    ELSE '60+'
                END as age_group,
                COUNT(*) as patient_count
            FROM patients
            GROUP BY age_group
            ORDER BY age_group
            """
            age_df = executor.execute_combined_query(age_dist_query, include_uploaded=include_uploaded)
            
            bmi_dist_query = """
            SELECT 
                CASE 
                    WHEN bmi < 18.5 THEN 'Underweight'
                    WHEN bmi < 25 THEN 'Normal'
                    WHEN bmi < 30 THEN 'Overweight'
                    ELSE 'Obese'
                END as bmi_category,
                COUNT(*) as patient_count,
                MIN(CASE 
                    WHEN bmi < 18.5 THEN 1
                    WHEN bmi < 25 THEN 2
                    WHEN bmi < 30 THEN 3
                    ELSE 4
                END) as sort_order
            FROM patients
            GROUP BY bmi_category
            ORDER BY sort_order
            """
            bmi_df = executor.execute_combined_query(bmi_dist_query, include_uploaded=include_uploaded)
            
            gender_query = """
            SELECT 
                CASE 
                    WHEN sex = 0 THEN 'Male'
                    WHEN sex = 1 THEN 'Female'
                END as gender,
                COUNT(*) as patient_count
            FROM patients
            GROUP BY gender
            ORDER BY gender
            """
            gender_df = executor.execute_combined_query(gender_query, include_uploaded=include_uploaded)
            
            disease_query = """
            SELECT 
                SUM(chronic_kidney_disease) as ckd_count,
                SUM(adrenal_and_thyroid_disorders) as thyroid_count,
                SUM(blood_pressure_abnormality) as bp_count
            FROM patients
            """
            disease_df = executor.execute_combined_query(disease_query, include_uploaded=include_uploaded)
            
            with col1:
                fig_age = create_age_distribution(age_df)
                st.plotly_chart(fig_age, use_container_width=True)
            
            with col2:
                fig_bmi = create_bmi_distribution(bmi_df)
                st.plotly_chart(fig_bmi, use_container_width=True)
            
            with col3:
                fig_gender = create_gender_distribution(gender_df)
                st.plotly_chart(fig_gender, use_container_width=True)
            
            st.subheader("Condition Distribution")
            fig_disease = create_disease_prevalence(disease_df)
            st.plotly_chart(fig_disease, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading visualizations: {str(e)}")
    
    with tab2:
        st.subheader("Disease Cohort Analysis")
        
        disease_option = st.selectbox(
            "Select Disease",
            ["Chronic Kidney Disease", "Thyroid Disorders", "Blood Pressure Abnormality"]
        )
        
        disease_map = {
            "Chronic Kidney Disease": "chronic_kidney_disease",
            "Thyroid Disorders": "adrenal_and_thyroid_disorders",
            "Blood Pressure Abnormality": "blood_pressure_abnormality"
        }
        
        selected_disease = disease_map[disease_option]
        
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_patients,
                AVG(age) as avg_age,
                AVG(bmi) as avg_bmi,
                AVG(level_of_stress) as avg_stress,
                SUM(CASE WHEN smoking = 1 THEN 1 ELSE 0 END) as smokers
            FROM patients
            WHERE {selected_disease} = 1
            """
            
            cohort_stats = executor.execute_combined_query(query, include_uploaded=include_uploaded)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_metric_card("Cohort Size", f"{cohort_stats['total_patients'].iloc[0]:,}")
            with col2:
                render_metric_card("Avg Age", f"{cohort_stats['avg_age'].iloc[0]:.1f} yrs")
            with col3:
                render_metric_card("Avg BMI", f"{cohort_stats['avg_bmi'].iloc[0]:.1f}")
            with col4:
                render_metric_card("Smokers", f"{cohort_stats['smokers'].iloc[0]:,}")
            
            render_sql_display(query)
            
        except Exception as e:
            st.error(f"Error loading cohort data: {str(e)}")
    
    with tab3:
        st.subheader("High-Risk Patient Identification")
        
        # Risk Score Definition
        with st.expander("ℹ️ Risk Score Definition", expanded=False):
            st.markdown("""
            **Risk Score Calculation (0-5 Scale)**
            
            Each patient receives 1 point for each of the following risk factors:
            - Chronic Kidney Disease (CKD)
            - Adrenal & Thyroid Disorders
            - Blood Pressure Abnormality
            - Smoking
            - High Stress Level (Level 3)
            
            **Maximum Risk Score**: 5 points
            
            **Risk Categories**:
            - **Low Risk**: 0-1 points
            - **Moderate Risk**: 2 points
            - **High Risk**: ≥3 points
            """)
        
        risk_threshold = st.slider("Risk Score Threshold", 0, 5, 3, 
                                   help="Show patients with risk score >= this threshold")
        
        try:
            # Privacy-preserving aggregated risk analysis with corrected formula
            query = f"""
            SELECT 
                (chronic_kidney_disease + 
                 adrenal_and_thyroid_disorders +
                 blood_pressure_abnormality + 
                 CASE WHEN smoking = 1 THEN 1 ELSE 0 END +
                 CASE WHEN level_of_stress = 3 THEN 1 ELSE 0 END) as risk_score,
                COUNT(*) as patient_count,
                AVG(age) as avg_age,
                AVG(bmi) as avg_bmi,
                AVG(level_of_stress) as avg_stress
            FROM patients
            WHERE (chronic_kidney_disease + 
                   adrenal_and_thyroid_disorders +
                   blood_pressure_abnormality + 
                   CASE WHEN smoking = 1 THEN 1 ELSE 0 END +
                   CASE WHEN level_of_stress = 3 THEN 1 ELSE 0 END) >= {risk_threshold}
            GROUP BY risk_score
            ORDER BY risk_score DESC
            """
            
            high_risk_stats = executor.execute_combined_query(query, include_uploaded=include_uploaded)
            
            if not high_risk_stats.empty:
                st.markdown("**High-Risk Patient Statistics (Aggregated)**")
                st.dataframe(high_risk_stats, use_container_width=True)
                
                total_high_risk = int(high_risk_stats['patient_count'].sum())
                st.info(f"📊 Total high-risk patients (score >= {risk_threshold}): **{total_high_risk:,}**")
            else:
                st.info(f"No patients found with risk score >= {risk_threshold}")
            
            render_sql_display(query)
            
        except Exception as e:
            st.error(f"Error loading triage data: {str(e)}")

def module_preventive():
    st.markdown("<h1 style='text-align: center; margin-top: 0;'>🧠 NeuroHealth Nexus</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>💪 Proactive Life Engine - Preventive Wellness & Lifestyle Optimization</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    db = DatabaseManager()
    from src.query_executor import MultiSourceQueryExecutor
    executor = MultiSourceQueryExecutor()
    
    include_uploaded = st.session_state.get('include_uploaded_data', False)
    
    # 1. Inject Custom CSS
    # This specific selector targets the tab labels
    css = '''
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.5rem; /* Adjust font size here */
            font-weight: bold; /* Optional: Make it bold */
        }
    </style>
    '''

    st.markdown(css, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎯 What-If Scenarios", "📈 Activity Analysis", "🧘 Stress Level Analysis"])
    
    with tab1:
        st.subheader("Lifestyle Risk Modeling")
        
        # Risk Score Definition and Calculation
        with st.expander("ℹ️ Risk Score Definition & Calculation", expanded=False):
            st.markdown("""
            ### Risk Score Calculation (0-4 Scale)
            
            Your risk score is calculated by adding 1 point for each of the following risk factors:
            
            **Risk Factors:**
            1. **Smoking** = Yes → +1 point
            2. **BMI** > 30 (Obese) → +1 point
            3. **Stress Level** = High (Level 3) → +1 point
            4. **Physical Activity** < 5,000 steps/day → +1 point
            
            ---
            
            ### Risk Score Interpretation
            
            | Score | Risk Level | Description |
            |-------|-----------|-------------|
            | **0** | Very Low | Excellent health habits, minimal risk factors |
            | **1** | Low | Good health habits, one area for improvement |
            | **2** | Moderate | Some concerning factors, lifestyle changes recommended |
            | **3** | High | Multiple risk factors, immediate intervention needed |
            | **4** | Very High | Critical risk level, urgent lifestyle changes required |
            
            ---
            
            ### Example Calculation
            
            **Scenario**: Person with BMI=32, Smoker, High Stress, 8,000 steps/day
            
            - Smoking = Yes → **+1**
            - BMI > 30 → **+1**
            - High Stress → **+1**
            - Steps < 5,000 → **0** (they walk 8,000 steps)
            
            **Total Risk Score = 3** (High Risk)
            """)
        
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Current Lifestyle")
            current_bmi = st.number_input("Current BMI", 15, 50, 35)
            current_smoking = st.selectbox("Smoking Status", ["No", "Yes"])
            current_stress = st.radio(
                "Stress Level",
                options=["Low", "Normal", "High"],
                horizontal=True,
                help="Select your current stress level"
            )
            current_activity = st.number_input("Daily Steps", 0, 50000, 20000)
        
        with col2:
            st.markdown("#### Target Lifestyle")
            target_bmi = st.number_input("Target BMI", 15, 50, 25)
            target_smoking = st.selectbox("Target Smoking", ["No", "Yes"], key="target_smoking")
            target_stress = st.radio(
                "Target Stress",
                options=["Low", "Normal", "High"],
                horizontal=True,
                key="target_stress",
                help="Select your target stress level"
            )
            target_activity = st.number_input("Target Steps", 0, 50000, 30000, key="target_activity")
        
        if st.button("Calculate Risk Reduction"):
            # Map stress levels to numeric values
            stress_map = {"Low": 1, "Normal": 2, "High": 3}
            
            current_risk = (
                (1 if current_smoking == "Yes" else 0) +
                (1 if current_bmi > 30 else 0) +
                (1 if stress_map[current_stress] == 3 else 0) +  # Only High stress counts as risk
                (1 if current_activity < 5000 else 0)
            )
            
            target_risk = (
                (1 if target_smoking == "Yes" else 0) +
                (1 if target_bmi > 30 else 0) +
                (1 if stress_map[target_stress] == 3 else 0) +  # Only High stress counts as risk
                (1 if target_activity < 5000 else 0)
            )
            
            risk_reduction = ((current_risk - target_risk) / max(current_risk, 1)) * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                render_metric_card("Current Risk Score", current_risk)
            with col2:
                render_metric_card("Target Risk Score", target_risk)
            with col3:
                render_metric_card("Risk Reduction", f"{risk_reduction:.1f}%", delta=f"{risk_reduction:.1f}%")
    
    with tab2:
        st.subheader("Physical Activity Trends")
        
        # Filters in sidebar-style column
        col_filter, col_main = st.columns([1, 3])
        
        with col_filter:
            st.markdown("#### Filters")
            
            # Get max day from database
            try:
                max_day_query = "SELECT MAX(day_number) as max_day FROM activity"
                max_day_result = executor.execute_combined_query(max_day_query, include_uploaded=include_uploaded)
                max_day = int(max_day_result['max_day'].iloc[0]) if not max_day_result.empty else 90
            except:
                max_day = 90  # Fallback
            
            day_range = st.slider(
                "Day Range",
                min_value=1,
                max_value=max_day,
                value=(1, min(30, max_day)),
                key="activity_day_range",
                help=f"Select day range (max: {max_day} days available)"
            )
            
            age_groups = st.multiselect(
                "Age Groups",
                options=["< 30", "30-39", "40-49", "50-59", "60+"],
                default=["< 30", "30-39", "40-49", "50-59", "60+"],
                key="activity_age_groups"
            )
            
            bmi_cats = st.multiselect(
                "BMI Categories",
                options=["Underweight", "Normal", "Overweight", "Obese"],
                default=["Underweight", "Normal", "Overweight", "Obese"],
                key="activity_bmi_cats"
            )
            
            st.markdown("**Health Conditions**")
            include_ckd = st.checkbox("Include CKD", value=True, key="activity_ckd")
            include_thyroid = st.checkbox("Include Thyroid", value=True, key="activity_thyroid")
            include_bp = st.checkbox("Include BP Abnormality", value=True, key="activity_bp")
            
            smoking_filter = st.radio("Smoking Status", ["All", "Smokers", "Non-smokers"], key="activity_smoking")
            
            stress_levels = st.multiselect(
                "Stress Levels",
                options=["Low", "Normal", "High"],
                default=["Low", "Normal", "High"],
                key="activity_stress"
            )
        
        with col_main:
            try:
                # Build dynamic WHERE clause for patients table
                patient_conditions = []
                
                # Age filter
                age_conditions = []
                if "< 30" in age_groups:
                    age_conditions.append("p.age < 30")
                if "30-39" in age_groups:
                    age_conditions.append("(p.age >= 30 AND p.age < 40)")
                if "40-49" in age_groups:
                    age_conditions.append("(p.age >= 40 AND p.age < 50)")
                if "50-59" in age_groups:
                    age_conditions.append("(p.age >= 50 AND p.age < 60)")
                if "60+" in age_groups:
                    age_conditions.append("p.age >= 60")
                
                if age_conditions:
                    patient_conditions.append(f"({' OR '.join(age_conditions)})")
                
                # BMI filter
                bmi_conditions = []
                if "Underweight" in bmi_cats:
                    bmi_conditions.append("p.bmi < 18.5")
                if "Normal" in bmi_cats:
                    bmi_conditions.append("(p.bmi >= 18.5 AND p.bmi < 25)")
                if "Overweight" in bmi_cats:
                    bmi_conditions.append("(p.bmi >= 25 AND p.bmi < 30)")
                if "Obese" in bmi_cats:
                    bmi_conditions.append("p.bmi >= 30")
                
                if bmi_conditions:
                    patient_conditions.append(f"({' OR '.join(bmi_conditions)})")
                
                # Disease filters
                disease_conditions = []
                if include_ckd:
                    disease_conditions.append("p.chronic_kidney_disease = 1")
                if include_thyroid:
                    disease_conditions.append("p.adrenal_and_thyroid_disorders = 1")
                if include_bp:
                    disease_conditions.append("p.blood_pressure_abnormality = 1")
                
                if disease_conditions:
                    patient_conditions.append(f"({' OR '.join(disease_conditions)})")
                
                # Smoking filter
                if smoking_filter == "Smokers":
                    patient_conditions.append("p.smoking = 1")
                elif smoking_filter == "Non-smokers":
                    patient_conditions.append("p.smoking = 0")
                
                # Stress filter
                stress_conditions = []
                if "Low" in stress_levels:
                    stress_conditions.append("p.level_of_stress = 1")
                if "Normal" in stress_levels:
                    stress_conditions.append("p.level_of_stress = 2")
                if "High" in stress_levels:
                    stress_conditions.append("p.level_of_stress = 3")
                
                if stress_conditions:
                    patient_conditions.append(f"({' OR '.join(stress_conditions)})")
                
                # Combine all conditions
                where_clause = " AND ".join(patient_conditions) if patient_conditions else "1=1"
                
                # Activity trend query
                activity_query = f"""
                SELECT 
                    a.day_number,
                    AVG(a.physical_activity) as avg_activity,
                    MIN(a.physical_activity) as min_activity,
                    MAX(a.physical_activity) as max_activity,
                    COUNT(DISTINCT a.patient_number) as patient_count
                FROM activity a
                JOIN patients p ON a.patient_number = p.patient_number
                WHERE a.day_number BETWEEN {day_range[0]} AND {day_range[1]}
                  AND {where_clause}
                GROUP BY a.day_number
                ORDER BY a.day_number
                """
                
                activity_df = executor.execute_combined_query(activity_query, include_uploaded=include_uploaded)
                
                if not activity_df.empty:
                    # Metrics
                    total_patients = activity_df['patient_count'].iloc[0]
                    avg_steps = activity_df['avg_activity'].mean()
                    max_day = activity_df.loc[activity_df['avg_activity'].idxmax(), 'day_number']
                    min_day = activity_df.loc[activity_df['avg_activity'].idxmin(), 'day_number']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        render_metric_card("Patients in Cohort", f"{int(total_patients):,}")
                    with col2:
                        render_metric_card("Avg Daily Steps", f"{avg_steps:.0f}")
                    with col3:
                        render_metric_card("Most Active Day", f"Day {int(max_day)}")
                    with col4:
                        render_metric_card("Least Active Day", f"Day {int(min_day)}")
                    
                    st.markdown("---")
                    
                    # Activity trend chart
                    fig_activity = create_activity_trend(activity_df)
                    st.plotly_chart(fig_activity, use_container_width=True)
                    
                    # Activity distribution
                    st.markdown("#### Activity Level Distribution")
                    
                    distribution_query = f"""
                    SELECT 
                        CASE 
                            WHEN a.physical_activity < 5000 THEN 'Sedentary (<5k)'
                            WHEN a.physical_activity < 10000 THEN 'Light (5k-10k)'
                            WHEN a.physical_activity < 15000 THEN 'Moderate (10k-15k)'
                            ELSE 'Active (15k+)'
                        END as activity_level,
                        COUNT(*) as count
                    FROM activity a
                    JOIN patients p ON a.patient_number = p.patient_number
                    WHERE a.day_number BETWEEN {day_range[0]} AND {day_range[1]}
                      AND {where_clause}
                    GROUP BY 
                        CASE 
                            WHEN a.physical_activity < 5000 THEN 'Sedentary (<5k)'
                            WHEN a.physical_activity < 10000 THEN 'Light (5k-10k)'
                            WHEN a.physical_activity < 15000 THEN 'Moderate (10k-15k)'
                            ELSE 'Active (15k+)'
                        END
                    ORDER BY 
                        MIN(CASE 
                            WHEN a.physical_activity < 5000 THEN 1
                            WHEN a.physical_activity < 10000 THEN 2
                            WHEN a.physical_activity < 15000 THEN 3
                            ELSE 4
                        END)
                    """
                    
                    dist_df = executor.execute_combined_query(distribution_query, include_uploaded=include_uploaded)
                    
                    if not dist_df.empty:
                        import plotly.graph_objects as go
                        colors = ['#EF553B', '#FFA15A', '#FECB52', '#00CC96']
                        
                        fig_dist = go.Figure(data=[
                            go.Bar(
                                x=dist_df['activity_level'],
                                y=dist_df['count'],
                                marker_color=colors,
                                text=dist_df['count'],
                                textposition='auto'
                            )
                        ])
                        
                        fig_dist.update_layout(
                            title='Distribution of Activity Levels',
                            xaxis_title='Activity Level',
                            yaxis_title='Number of Records',
                            height=350,
                            margin=dict(l=20, r=20, t=60, b=20),
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig_dist, use_container_width=True)
                    
                    render_sql_display(activity_query)
                else:
                    st.info("No activity data found for the selected filters.")
                
            except Exception as e:
                st.error(f"Error loading activity data: {str(e)}")
    
    with tab3:
        st.subheader("Stress Level Analysis")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown("#### Filters")
            
            stress_levels = st.multiselect(
                "Select Stress Levels",
                options=[1, 2, 3],
                default=[1, 2, 3],
                format_func=lambda x: {1: "Low", 2: "Normal", 3: "High"}[x]
            )
            
            show_smokers_only = st.checkbox("Show Smokers Only", value=False)
            show_disease = st.selectbox(
                "Filter by Disease",
                ["All Patients", "Chronic Kidney Disease", "Thyroid Disorders", "Blood Pressure Abnormality"]
            )
        
        with col2:
            try:
                if not stress_levels:
                    st.warning("Please select at least one stress level.")
                else:
                    # Build dynamic WHERE clause
                    stress_filter = f"level_of_stress IN ({','.join(map(str, stress_levels))})"
                    where_conditions = [stress_filter]
                    
                    if show_smokers_only:
                        where_conditions.append("smoking = 1")
                    
                    if show_disease != "All Patients":
                        disease_map = {
                            "Chronic Kidney Disease": "chronic_kidney_disease = 1",
                            "Thyroid Disorders": "adrenal_and_thyroid_disorders = 1",
                            "Blood Pressure Abnormality": "blood_pressure_abnormality = 1"
                        }
                        where_conditions.append(disease_map[show_disease])
                    
                    where_clause = " AND ".join(where_conditions)
                    
                    stress_query = f"""
                    SELECT 
                        level_of_stress,
                        COUNT(*) as patient_count,
                        AVG(bmi) as avg_bmi,
                        AVG(age) as avg_age,
                        SUM(CASE WHEN smoking = 1 THEN 1 ELSE 0 END) as smoker_count
                    FROM patients
                    WHERE {where_clause}
                    GROUP BY level_of_stress
                    ORDER BY level_of_stress
                    """
                    
                    stress_df = executor.execute_combined_query(stress_query, include_uploaded=include_uploaded)
                    
                    if not stress_df.empty:
                        # Summary metrics - only for selected stress levels
                        total_patients = stress_df['patient_count'].sum()
                        
                        # Create dynamic metric cards based on selected stress levels
                        stress_label_map = {1: 'Low Stress', 2: 'Normal Stress', 3: 'High Stress'}
                        
                        # Create columns based on number of selected stress levels
                        num_cols = len(stress_levels)
                        metric_cols = st.columns(num_cols)
                        
                        for idx, stress_level in enumerate(sorted(stress_levels)):
                            count = stress_df[stress_df['level_of_stress'] == stress_level]['patient_count'].sum() if stress_level in stress_df['level_of_stress'].values else 0
                            percentage = (count / total_patients * 100) if total_patients > 0 else 0
                            
                            with metric_cols[idx]:
                                st.markdown(f"""
                                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
                                    <h3 style="margin: 0; color: #666; font-size: 14px;">{stress_label_map[stress_level]}</h3>
                                    <h1 style="margin: 10px 0; color: #1f77b4; font-size: 32px;">{int(count):,}</h1>
                                    <p style="margin: 0; color: #888; font-size: 14px;">{percentage:.1f}% of filtered patients</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Visualization
                        fig_stress = create_stress_distribution(stress_df)
                        if fig_stress:
                            st.plotly_chart(fig_stress, use_container_width=True)
                        
                        # Data table with formatting
                        st.markdown("**Detailed Statistics by Stress Level**")
                        display_df = stress_df.copy()
                        display_df['stress_label'] = display_df['level_of_stress'].map({1: 'Low', 2: 'Normal', 3: 'High'})
                        display_df['avg_bmi'] = display_df['avg_bmi'].round(1)
                        display_df['avg_age'] = display_df['avg_age'].round(1)
                        display_df = display_df[['stress_label', 'patient_count', 'avg_bmi', 'avg_age', 'smoker_count']]
                        display_df.columns = ['Stress Level', 'Patient Count', 'Avg BMI', 'Avg Age', 'Smokers']
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                        
                        render_sql_display(stress_query)
                    else:
                        st.info("No patients found matching the selected filters.")
                
            except Exception as e:
                st.error(f"Error loading stress data: {str(e)}")

def module_strategic():
    st.markdown("<h1 style='text-align: center; margin-top: 0;'>🧠 NeuroHealth Nexus</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>📊 Strategic Intelligence - Natural Language Query Interface</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    db = DatabaseManager()
    from src.query_executor import MultiSourceQueryExecutor
    executor = MultiSourceQueryExecutor()
    
    include_uploaded = st.session_state.get('include_uploaded_data', False)

    # 1. Inject Custom CSS
    # This specific selector targets the tab labels
    css = '''
    <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.5rem; /* Adjust font size here */
            font-weight: bold; /* Optional: Make it bold */
        }
    </style>
    '''

    st.markdown(css, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💬 Natural Language Query", "📈 Population Insights"])
    
    with tab1:
        st.subheader("Ask Questions About Your Data")
        
        render_info_box(
            "How to Use",
            "Ask questions in natural language about patient populations, health trends, or risk factors. "
            "The AI will generate SQL queries and return aggregated insights while protecting patient privacy.",
            "info"
        )
        
        example_queries = [
            "What is the average BMI of patients with chronic kidney disease?",
            "How many patients have both high stress and smoking habits?",
            "What is the correlation between age and chronic kidney disease?",
            "Show me the distribution of patients by stress level",
            "What percentage of patients have blood pressure abnormalities?"
        ]
        
        with st.expander("**Example Queries:**", expanded=True):
            for i, example in enumerate(example_queries, 1):
                st.caption(f"{i}. {example}")
        
        user_query = st.text_area(
            "Enter your question:",
            height=100,
            placeholder="e.g., What is the average age of patients with chronic kidney disease?"
        )
        
        if st.button("Run Query", type="primary"):
            if user_query:
                with st.spinner("Processing your query..."):
                    include_uploaded = st.session_state.get('include_uploaded_data', False)
                    # Pass the executor and checkbox state to the agent workflow
                    result = agent_workflow(user_query, executor, include_uploaded)
                    
                    if result["success"]:
                        # 1. Main Insight & Recommendations (Prominent)
                        st.markdown(f"""
                        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
                            <h3 style="color: #1b5e20; margin-top: 0;">💡 Strategic Insights</h3>
                            <p style="font-size: 1.1em; color: #333;">{result["insight"]}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # 2. Key Insights (Hidden by default)
                        if result.get("key_insights", []):
                            with st.expander("🔍 View Key Insights", expanded=False):
                                st.markdown("**Key Insights:**")
                                for insight in result.get("key_insights", []):
                                    st.markdown(f"- {insight}")
                        
                        if result.get("recommendations"):
                            rec_items = "".join([f"<li style='margin-bottom: 8px;'>{rec}</li>" for rec in result['recommendations']])
                            st.markdown(f"""
                            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #1565c0; margin-bottom: 20px;">
                                <h3 style="color: #0d47a1; margin-top: 0;">📋 Recommendations</h3>
                                <ul style="color: #333; font-size: 1.05em; margin-bottom: 0; padding-left: 20px;">
                                    {rec_items}
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 2. Technical Details (Hidden by default)
                        with st.expander("🔍 View Technical Details (SQL & Data)", expanded=False):
                            st.markdown("**Execution Steps:**")
                            for i, step in enumerate(result.get("steps", []), 1):
                                st.markdown(f"---")
                                st.markdown(f"**Step {i}:** {step['description']}")
                                st.code(step['sql'], language="sql")
                                
                                if step['data'] is not None and not step['data'].empty:
                                    st.dataframe(step['data'], use_container_width=True)
                                else:
                                    st.write("No data returned for this step.")
                    else:
                        st.error(result["error"])
            else:
                st.warning("Please enter a question")
    
    with tab2:
        st.subheader("Population Health Metrics")
        
        # Filters in sidebar-style column
        col_filter, col_main = st.columns([1, 3])
        
        with col_filter:
            st.markdown("#### Filters")
            
            age_range = st.slider(
                "Age Range",
                min_value=18,
                max_value=100,
                value=(18, 100),
                key="pop_age_range"
            )
            
            bmi_categories = st.multiselect(
                "BMI Categories",
                options=["Underweight", "Normal", "Overweight", "Obese"],
                default=["Underweight", "Normal", "Overweight", "Obese"],
                key="pop_bmi_cats"
            )
        
        with col_main:
            try:
                # Build dynamic WHERE clause
                where_conditions = [f"age BETWEEN {age_range[0]} AND {age_range[1]}"]
                
                # BMI filter
                bmi_conditions = []
                if "Underweight" in bmi_categories:
                    bmi_conditions.append("bmi < 18.5")
                if "Normal" in bmi_categories:
                    bmi_conditions.append("(bmi >= 18.5 AND bmi < 25)")
                if "Overweight" in bmi_categories:
                    bmi_conditions.append("(bmi >= 25 AND bmi < 30)")
                if "Obese" in bmi_categories:
                    bmi_conditions.append("bmi >= 30")
                
                if bmi_conditions:
                    where_conditions.append(f"({' OR '.join(bmi_conditions)})")
                
                where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
                
                population_query = f"""
                SELECT 
                    COUNT(*) as total_patients,
                    AVG(age) as avg_age,
                    AVG(bmi) as avg_bmi,
                    SUM(CASE WHEN chronic_kidney_disease = 1 THEN 1 ELSE 0 END) as ckd_count,
                    SUM(CASE WHEN smoking = 1 THEN 1 ELSE 0 END) as smoker_count,
                    AVG(level_of_stress) as avg_stress,
                    SUM(CASE WHEN adrenal_and_thyroid_disorders = 1 THEN 1 ELSE 0 END) as thyroid_count,
                    SUM(CASE WHEN blood_pressure_abnormality = 1 THEN 1 ELSE 0 END) as bp_count
                FROM patients
                WHERE {where_clause}
                """
                
                pop_stats = executor.execute_combined_query(population_query, include_uploaded=include_uploaded)
                
                if not pop_stats.empty and pop_stats['total_patients'].iloc[0] > 0:
                    total = pop_stats['total_patients'].iloc[0]
                    avg_stress_val = pop_stats['avg_stress'].iloc[0]
                    
                    # Map average stress to category
                    stress_label = "Low" if avg_stress_val < 1.5 else ("Normal" if avg_stress_val < 2.5 else "High")
                    
                    # Metrics display
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        render_metric_card("Total Population", f"{int(total):,}")
                        render_metric_card("Avg Age", f"{pop_stats['avg_age'].iloc[0]:.1f} years")
                    
                    with col2:
                        render_metric_card("CKD Prevalence", f"{(pop_stats['ckd_count'].iloc[0] / total * 100):.1f}%")
                        render_metric_card("Smoking Rate", f"{(pop_stats['smoker_count'].iloc[0] / total * 100):.1f}%")
                    
                    with col3:
                        render_metric_card("Avg BMI", f"{pop_stats['avg_bmi'].iloc[0]:.1f}")
                        render_metric_card("Avg Stress", f"{stress_label} ({avg_stress_val:.1f})")
                    
                    st.markdown("---")
                    
                    # Disease Prevalence Chart
                    st.subheader("Disease Prevalence")
                    
                    disease_data = {
                        'Disease': ['Chronic Kidney Disease', 'Thyroid Disorders', 'Blood Pressure Abnormality'],
                        'Count': [
                            int(pop_stats['ckd_count'].iloc[0]),
                            int(pop_stats['thyroid_count'].iloc[0]),
                            int(pop_stats['bp_count'].iloc[0])
                        ],
                        'Percentage': [
                            pop_stats['ckd_count'].iloc[0] / total * 100,
                            pop_stats['thyroid_count'].iloc[0] / total * 100,
                            pop_stats['bp_count'].iloc[0] / total * 100
                        ]
                    }
                    
                    import plotly.graph_objects as go
                    fig_disease = go.Figure(data=[
                        go.Bar(
                            x=disease_data['Disease'],
                            y=disease_data['Percentage'],
                            text=[f"{p:.1f}%<br>({c:,})" for p, c in zip(disease_data['Percentage'], disease_data['Count'])],
                            textposition='auto',
                            marker_color=['#EF553B', '#FFA15A', '#00CC96']
                        )
                    ])
                    
                    fig_disease.update_layout(
                        title='Disease Prevalence in Filtered Population',
                        yaxis_title='Percentage of Patients (%)',
                        xaxis_title='',
                        height=350,
                        margin=dict(l=20, r=20, t=60, b=20)
                    )
                    
                    st.plotly_chart(fig_disease, use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("Risk Distribution Heatmap")
                    
                    # Privacy-preserving heatmap with aggregated data
                    heatmap_query = f"""
                    SELECT 
                        CASE 
                            WHEN age < 30 THEN '< 30'
                            WHEN age < 40 THEN '30-39'
                            WHEN age < 50 THEN '40-49'
                            WHEN age < 60 THEN '50-59'
                            ELSE '60+'
                        END as age_group,
                        CASE 
                            WHEN bmi < 18.5 THEN 'Underweight'
                            WHEN bmi < 25 THEN 'Normal'
                            WHEN bmi < 30 THEN 'Overweight'
                            ELSE 'Obese'
                        END as bmi_category,
                        COUNT(*) as patient_count
                    FROM patients
                    WHERE {where_clause}
                    GROUP BY age_group, bmi_category
                    ORDER BY age_group, bmi_category
                    """
                    heatmap_df = executor.execute_combined_query(heatmap_query, include_uploaded=include_uploaded)
                    
                    if not heatmap_df.empty:
                        from src.visualizer import create_risk_heatmap
                        fig_heatmap = create_risk_heatmap(heatmap_df)
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    render_sql_display(population_query)
                else:
                    st.info("No patients found matching the selected filters.")
                
            except Exception as e:
                st.error(f"Error loading population data: {str(e)}")

if __name__ == "__main__":
    main()
