import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_age_distribution(df):
    if 'age_group' in df.columns and 'patient_count' in df.columns:
        # Grouped age data - create a copy to avoid modifying original
        df_copy = df.copy()
        age_order = ['< 30', '30-39', '40-49', '50-59', '60+']
        df_copy['age_group'] = pd.Categorical(df_copy['age_group'], categories=age_order, ordered=True)
        df_copy = df_copy.sort_values('age_group')
        
        fig = px.bar(
            df_copy,
            x='age_group',
            y='patient_count',
            title='Age Distribution by Group',
            labels={'age_group': 'Age Group', 'patient_count': 'Number of Patients'},
            color_discrete_sequence=['#636EFA']
        )
    elif 'patient_count' in df.columns:
        # Individual age data
        fig = px.bar(
            df,
            x='age',
            y='patient_count',
            title='Age Distribution',
            labels={'age': 'Age', 'patient_count': 'Number of Patients'},
            color_discrete_sequence=['#636EFA']
        )
    else:
        # Raw data
        fig = px.histogram(
            df, 
            x='age', 
            nbins=20,
            title='Age Distribution',
            labels={'age': 'Age', 'count': 'Number of Patients'},
            color_discrete_sequence=['#636EFA']
        )
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_bmi_distribution(df):
    if 'bmi_category' in df.columns and 'patient_count' in df.columns:
        # Grouped BMI data - create a copy to avoid modifying original
        df_copy = df.copy()
        bmi_order = ['Underweight', 'Normal', 'Overweight', 'Obese']
        df_copy['bmi_category'] = pd.Categorical(df_copy['bmi_category'], categories=bmi_order, ordered=True)
        df_copy = df_copy.sort_values('bmi_category')
        
        # Color code by BMI category
        colors = ['#FFA15A', '#00CC96', '#FECB52', '#EF553B']
        
        fig = px.bar(
            df_copy,
            x='bmi_category',
            y='patient_count',
            labels={'bmi_category': 'BMI Category', 'patient_count': 'Number of Patients'},
            color='bmi_category',
            color_discrete_sequence=colors
        )
    elif 'patient_count' in df.columns:
        # Individual BMI data
        fig = px.bar(
            df,
            x='bmi',
            y='patient_count',
            labels={'bmi': 'BMI', 'patient_count': 'Number of Patients'},
            color_discrete_sequence=['#EF553B']
        )
    else:
        # Raw data
        fig = px.histogram(
            df, 
            x='bmi', 
            nbins=25,
            labels={'bmi': 'BMI', 'count': 'Number of Patients'},
            color_discrete_sequence=['#EF553B']
        )
    fig.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_gender_distribution(df):
    if df is None or df.empty:
        return None
    
    if 'gender' not in df.columns or 'patient_count' not in df.columns:
        return None
    
    # Gender-specific colors
    colors = ['#636EFA', '#EF553B']  # Blue for Male, Red/Pink for Female
    
    fig = px.pie(
        df,
        values='patient_count',
        names='gender',
        title='Gender Distribution',
        color='gender',
        color_discrete_map={'Male': '#636EFA', 'Female': '#EF553B'},
        hole=0.3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    return fig

def create_disease_prevalence(df):
    if 'ckd_count' in df.columns:
        diseases = {
            'Chronic Kidney Disease': df['ckd_count'].iloc[0],
            'Thyroid Disorders': df['thyroid_count'].iloc[0],
            'Blood Pressure Abnormality': df['bp_count'].iloc[0]
        }
    else:
        diseases = {
            'Chronic Kidney Disease': df['chronic_kidney_disease'].sum() if 'chronic_kidney_disease' in df.columns else 0,
            'Thyroid Disorders': df['adrenal_and_thyroid_disorders'].sum() if 'adrenal_and_thyroid_disorders' in df.columns else 0,
            'Blood Pressure Abnormality': df['blood_pressure_abnormality'].sum() if 'blood_pressure_abnormality' in df.columns else 0
        }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(diseases.keys()),
            y=list(diseases.values()),
            marker_color=['#00CC96', '#AB63FA', '#FFA15A']
        )
    ])
    
    fig.update_layout(
        title='Disease Prevalence',
        xaxis_title='Condition',
        yaxis_title='Number of Patients',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def create_activity_trend(df):
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Check if min/max columns exist for confidence band
    if 'min_activity' in df.columns and 'max_activity' in df.columns:
        # Create shaded band for min-max range
        fig.add_trace(go.Scatter(
            x=pd.concat([df['day_number'], df['day_number'][::-1]]),
            y=pd.concat([df['max_activity'], df['min_activity'][::-1]]),
            fill='toself',
            fillcolor='rgba(0, 204, 150, 0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=False,
            name='Range'
        ))
        
        y_col = 'avg_activity'
        title = 'Average Daily Physical Activity (with Min/Max Range)'
    elif 'avg_activity' in df.columns:
        y_col = 'avg_activity'
        title = 'Average Daily Physical Activity'
    else:
        # Raw data aggregation if needed
        if 'physical_activity' in df.columns:
            df = df.groupby('day_number')['physical_activity'].mean().reset_index()
            y_col = 'physical_activity'
            title = 'Average Daily Physical Activity'
        else:
            return None

    # Add main trend line
    fig.add_trace(go.Scatter(
        x=df['day_number'],
        y=df[y_col],
        mode='lines+markers',
        name='Avg Steps',
        line=dict(color='#00CC96', width=3),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title=title,
        xaxis_title='Day Number',
        yaxis_title='Steps',
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig

def create_stress_distribution(df):
    if df is None or df.empty:
        return None
    
    if 'level_of_stress' not in df.columns or 'patient_count' not in df.columns:
        return None
    
    # Map stress levels to labels
    stress_labels = {1: 'Low', 2: 'Normal', 3: 'High'}
    df_plot = df.copy()
    df_plot['stress_label'] = df_plot['level_of_stress'].map(stress_labels)
    
    # Define colors for each stress level
    color_map = {
        'Low': '#00CC96',      # Green
        'Normal': '#FFA15A',   # Orange
        'High': '#EF553B'      # Red
    }
    
    colors = [color_map.get(label, '#636EFA') for label in df_plot['stress_label']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_plot['stress_label'],
            y=df_plot['patient_count'],
            marker_color=colors,
            text=df_plot['patient_count'],
            textposition='auto',
            texttemplate='%{text:,}',
            hovertemplate='<b>%{x} Stress</b><br>Patient Count: %{y:,}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='Stress Level Distribution',
        xaxis_title='Stress Category',
        yaxis_title='Number of Patients',
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(
            categoryorder='array',
            categoryarray=['Low', 'Normal', 'High']
        )
    )
    
    return fig

def create_metric_comparison(df, metric_col, group_col):
    if metric_col not in df.columns or group_col not in df.columns:
        return None
    
    fig = px.box(
        df,
        x=group_col,
        y=metric_col,
        title=f'{metric_col.replace("_", " ").title()} by {group_col.replace("_", " ").title()}',
        color=group_col
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    return fig

def create_risk_heatmap(df):
    if df is None or df.empty:
        return None
    
    if 'age_group' not in df.columns or 'bmi_category' not in df.columns or 'patient_count' not in df.columns:
        return None
    
    # Pivot the data for heatmap
    pivot_df = df.pivot(index='age_group', columns='bmi_category', values='patient_count').fillna(0)
    
    # Define order for age groups and BMI categories
    age_order = ['< 30', '30-39', '40-49', '50-59', '60+']
    bmi_order = ['Underweight', 'Normal', 'Overweight', 'Obese']
    
    # Reindex to ensure proper ordering
    pivot_df = pivot_df.reindex(index=age_order, columns=bmi_order, fill_value=0)
    
    fig = px.imshow(
        pivot_df,
        labels=dict(x="BMI Category", y="Age Group", color="Patient Count"),
        title="Patient Distribution: Age vs BMI (Aggregated)",
        color_continuous_scale='Blues',
        aspect="auto",
        text_auto=True
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig
