
import streamlit as st
# Page config
st.set_page_config(
    page_title="EB Estimation Agent",
    page_icon="/Users/ebpearls/Desktop/Ai estimation/frontend/assets/logo.png",
    layout="wide"
)

import requests
import json
from datetime import datetime
import pandas as pd

# Configuration
API_URL = "http://localhost:8000/api/v1"




# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .epic-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .task-item {
        background-color: white;
        padding: 0.5rem;
        border-left: 3px solid #1f77b4;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header"> EB Estimation Agent</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Main content
    tab1, tab2 = st.tabs([" New Estimation", "ℹ About"])
    
    with tab1:
        show_estimation_form()
    
    with tab2:
        show_about()


def show_estimation_form():
    """Show the estimation creation form."""
    st.header("Create New Estimation")
    
    with st.form("estimation_form"):
        project_name = st.text_input(
            "Project Name *",
            placeholder="e.g., E-commerce Platform"
        )
        
        description = st.text_area(
            "Project Description *",
            placeholder="Describe your project requirements in detail...",
            height=200
        )
        
        additional_context = st.text_area(
            "Additional Context (Optional)",
            placeholder="Any additional information or specific requirements...",
            height=100
        )
        
        submitted = st.form_submit_button("🚀 Generate Estimation", use_container_width=True)
    
    # Handle form submission outside the form context
    if submitted:
        if not project_name or not description:
            st.error(" Please fill in all required fields")
        else:
            generate_estimation(project_name, description, additional_context)


def generate_estimation(project_name: str, description: str, additional_context: str):
    """Call API to generate estimation."""
    # Create progress indicators
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    with st.spinner(" AI is analyzing your requirements and generating estimation..."):
        try:
            # Show progress steps
            status_placeholder.info(" Step 1/5: Analyzing requirements...")
            
            # Prepare request
            payload = {
                "project_name": project_name,
                "description": description,
                "additional_context": additional_context
            }
            
            # Call API with no timeout (backend will handle long-running requests)
            status_placeholder.info(" Step 2/5: Processing with AI agents (this may take several minutes)...")
            response = requests.post(f"{API_URL}/estimate", json=payload, timeout=None)
            
            status_placeholder.info("Step 5/5: Finalizing estimation...")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    progress_placeholder.empty()
                    status_placeholder.empty()
                    display_estimation(result["estimation"])
                else:
                    status_placeholder.error(f" Estimation failed: {result.get('message', 'Unknown error')}")
            else:
                status_placeholder.error(f" API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            status_placeholder.error(" Request timed out. Please try again or contact support.")
        except requests.exceptions.ConnectionError:
            status_placeholder.error(" Connection error. Make sure the backend is running at http://localhost:8000")
        except Exception as e:
            status_placeholder.error(f" Error: {str(e)}")


def display_estimation(estimation: dict):
    """Display the generated estimation with editing capabilities."""
    st.success(" Estimation generated successfully!")
    
    # Store estimation in session state for editing
    if 'estimation' not in st.session_state or st.session_state.get('reload_estimation'):
        st.session_state.estimation = estimation.copy()
        st.session_state.reload_estimation = False
    
    estimation = st.session_state.estimation
    
    # Summary
    st.markdown("---")
    st.header(" Estimation Summary")
    
    # Project info
    st.subheader(f" {estimation.get('project_name', 'Project')}")
    if estimation.get('description'):
        st.markdown(f"**Description:** {estimation['description']}")
    
    # Display analyzed requirements if available
    if 'analyzed_requirement' in estimation:
        analyzed = estimation['analyzed_requirement']
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            if analyzed.get('domain'):
                st.markdown(f"**Domain:** {analyzed['domain']}")
            if analyzed.get('complexity'):
                complexity_emoji = {"simple": "S", "medium": "M", "complex": "C"}.get(analyzed['complexity'], "⚪")
                st.markdown(f"**Complexity:** {complexity_emoji} {analyzed['complexity'].title()}")
        
        with col_info2:
            if analyzed.get('platforms'):
                platforms_str = ", ".join(analyzed['platforms'])
                st.markdown(f"**Platforms:** {platforms_str}")
            if analyzed.get('user_types'):
                user_types_str = ", ".join(analyzed['user_types'])
                st.markdown(f"** User Types:** {user_types_str}")
    
    st.markdown("---")
    
    # Recalculate totals
    total_hours = sum(
        sum(sum(task['efforts'].values()) for task in epic.get('tasks', []))
        for epic in estimation.get("epics", [])
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hours", total_hours)
    
    with col2:
        st.metric("Total Epics", len(estimation.get("epics", [])))
    
    with col3:
        mandatory_count = sum(1 for e in estimation.get("epics", []) if e.get("is_mandatory"))
        st.metric("Mandatory Epics", mandatory_count)
    
    with col4:
        custom_count = sum(1 for e in estimation.get("epics", []) if not e.get("is_mandatory"))
        st.metric("Custom Epics", custom_count)
    
    # Platform breakdown
    st.markdown("---")
    st.subheader("Platform Breakdown")
    
 
    
    
    # Epics details with editing
    st.markdown("---")
    st.subheader(" Epics & Tasks Breakdown")
    
    epics = estimation.get("epics", [])
    
    # Debug: Show epic count
    if len(epics) == 0:
        st.warning(" No epics found in the estimation result.")
        st.write("Estimation data:", estimation)
        return
    
    st.info(f" Showing {len(epics)} epics")
    
    for epic_idx, epic in enumerate(epics):
        try:
            # Calculate epic hours safely
            epic_hours = sum(sum(t.get('efforts', {}).values()) for t in epic.get('tasks', []))
        except Exception as e:
            st.error(f"Error calculating hours for epic {epic_idx}: {e}")
            epic_hours = 0
        
        try:
            epic_name = epic.get('name', 'Unnamed Epic')
            is_mandatory = epic.get('is_mandatory', False)
            
            with st.expander(
                f"{'(M)' if is_mandatory else '(C)'} {epic_name} ({epic_hours} hours)",
                expanded=False
            ):
                # Epic info (read-only for now to avoid state issues)
                if epic.get("description"):
                    st.markdown(f"**Description:** {epic['description']}")
                
                if epic.get("source_template"):
                    st.markdown(f"**Source:** {epic['source_template']}")
                
                st.markdown(f"**Type:** {'Mandatory' if is_mandatory else 'Custom'}")
                
                # Tasks
                st.markdown("**Tasks:**")
                
                tasks = epic.get("tasks", [])
                if tasks:
                    for idx, task in enumerate(tasks, 1):
                        st.markdown(f"**{idx}. {task.get('description', 'No description')}**")
                        
                        # User types
                        if task.get("user_types"):
                            user_types_str = ", ".join(task["user_types"])
                            st.markdown(f"   - 👥 User Types: {user_types_str}")
                        
                        # Efforts
                        efforts = task.get("efforts", {})
                        if efforts:
                            effort_str = " | ".join([f"{platform}: {hours}h" for platform, hours in efforts.items()])
                            st.markdown(f"   -  Effort: {effort_str}")
                        
                        if task.get("source"):
                            st.markdown(f"   -  Source: {task['source']}")
                        
                        st.markdown("")
                else:
                    st.info("No tasks defined for this epic")
                    
        except Exception as e:
            st.error(f"Error displaying epic {epic_idx}: {str(e)}")
            st.write("Epic data:", epic)
    
    # Export options
    st.markdown("---")
    st.subheader(" Export Estimation")
    
    # Update estimation totals before export
    st.session_state.estimation['total_hours'] = total_hours
 
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        json_str = json.dumps(st.session_state.estimation, indent=2, default=str)
        st.download_button(
            label=" Download JSON",
            data=json_str,
            file_name=f"{st.session_state.estimation['project_name']}_estimation.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # CSV export
        csv_data = create_csv_export(st.session_state.estimation)
        st.download_button(
            label=" Download CSV",
            data=csv_data,
            file_name=f"{st.session_state.estimation['project_name']}_estimation.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Reset button
        if st.button(" Reset to Original", use_container_width=True):
            st.session_state.reload_estimation = True
            st.rerun()


def create_csv_export(estimation: dict) -> str:
    """Create CSV export of estimation."""
    rows = []
    
    for epic in estimation.get("epics", []):
        for task in epic.get("tasks", []):
            for platform, hours in task.get("efforts", {}).items():
                rows.append({
                    "Epic": epic["name"],
                    "Epic Type": "Mandatory" if epic.get("is_mandatory") else "Custom",
                    "Task": task["description"],
                    "Platform": platform,
                    "Hours": hours,
                    "Source": task.get("source", "")
                })
    
    if rows:
        df = pd.DataFrame(rows)
        return df.to_csv(index=False)
    return ""


def show_about():
    """Show about information."""
    st.header("About EB Estimation Agent")
    
    st.markdown("""
    ###  What is this?
    
    EB Estimation Agent is an AI-powered system that automates software project estimation by learning from historical data and generating structured effort estimates.
    
    ###  Features
    
    - **AI-Driven Analysis**: Uses GPT-4 mini to analyze your requirements
    - **Historical Learning**: Leverages past project data for accurate estimates
    - **Automatic Breakdown**: Decomposes projects into epics and tasks
    - **Platform-Specific**: Generates estimates for Flutter, Web App, API, and CMS
    - **Mandatory Epics**: Ensures all required epics are included
    - **Customizable**: Add, remove, or modify epics as needed
    
    ### Workflow
    
    1. **Analyze Requirements** - AI extracts features, platforms, and initial epics
    2. **Retrieve Similar Epics** - Finds matching epics from MySQL knowledge base
    3. **Generate Custom Epics** - Creates project-specific epics with tasks and effort estimates
    4. **Validate & Output** - Ensures business rules and generates final estimation
    
    ###  Mandatory Epics
    
    Every estimation includes these mandatory epics:
    - Authentication
    - Project Configuration
    - Deployment
    - Database Design
    - Elastic Search
    - Notification
    - My Profile
    
    ###  Technology Stack
    
    - **Backend**: FastAPI
    - **Workflow**: LangGraph (3-agent system)
    - **AI**: OpenAI GPT-4o-mini
    - **Vector DB**: MySQL with embeddings
    - **Frontend**: Streamlit
    
    ### Usage Tips
    
    1. Provide detailed project descriptions
    2. Mention specific features and technologies
    3. Include any special requirements
    4. Review and customize the generated estimation
    5. Export to JSON or CSV for further use
    """)


if __name__ == "__main__":
    main()
