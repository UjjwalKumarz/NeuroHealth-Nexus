import streamlit as st

def render_metric_card(label, value, delta=None, help_text=None):
    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text
    )

def render_info_box(title, content, box_type="info"):
    if box_type == "success":
        st.success(f"**{title}**\n\n{content}")
    elif box_type == "warning":
        st.warning(f"**{title}**\n\n{content}")
    elif box_type == "error":
        st.error(f"**{title}**\n\n{content}")
    else:
        st.info(f"**{title}**\n\n{content}")

def render_sql_display(sql_query):
    with st.expander("View Generated SQL Query"):
        st.code(sql_query, language="sql")

def render_disclaimer():
    st.caption(
        "Medical Disclaimer: This tool is for informational purposes only and should not be used "
        "as a substitute for professional medical advice, diagnosis, or treatment."
    )

def render_sidebar_filters(db):
    st.sidebar.header("Filters")
    
    age_range = st.sidebar.slider(
        "Age Range",
        min_value=18,
        max_value=100,
        value=(18, 100)
    )
    
    sex_filter = st.sidebar.multiselect(
        "Gender",
        options=["Male", "Female"],
        default=["Male", "Female"]
    )
    
    ckd_filter = st.sidebar.checkbox("Show only CKD patients", value=False)
    
    return {
        "age_range": age_range,
        "sex_filter": sex_filter,
        "ckd_filter": ckd_filter
    }

def render_query_result(result):
    if not result['success']:
        st.error(result['error'])
        if result.get('sql'):
            render_sql_display(result['sql'])
        return
    
    # st.success(f"Query Intent: **{result['intent']}**")
    
    render_sql_display(result['sql'])
    
    if result['data'] is not None and not result['data'].empty:
        st.subheader("Results")
        st.dataframe(result['data'], use_container_width=True)
        
        st.download_button(
            label="Download Results as CSV",
            data=result['data'].to_csv(index=False),
            file_name="query_results.csv",
            mime="text/csv"
        )
    else:
        st.info("No data returned from query")
