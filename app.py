import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv

# Load local environment variables if present
load_dotenv()

# Set page configuration with custom title and icon
st.set_page_config(
    page_title="DataBot — AI Data Analyst Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom modular imports
from utils.data_loader import (
    get_default_df,
    validate_uploaded_csv
)
from utils.llm import (
    query_groq,
    test_groq_key,
    extract_chart_data
)
from utils.charts import render_plotly_chart

# Custom Premium CSS Injector
# Employs curated dark mode themes, glowing outline buttons, custom chat bubble aesthetics
# and smooth transition delays.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Apply globally */
    html, body, [class*="ViewContainer"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        color: #FFFFFF !important;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Info box styling */
    .info-box {
        background-color: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: #93C5FD;
    }
    
    /* Main Layout background refinement */
    .stApp {
        background-color: #080A10;
        color: #E2E8F0;
    }
    
    /* Sidebar styling refinement */
    [data-testid="stSidebar"] {
        background-color: #0E121E !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Custom header title card - Glassmorphism */
    .header-container {
        padding: 2rem;
        background: linear-gradient(135deg, rgba(14, 18, 30, 0.6) 0%, rgba(8, 10, 16, 0.8) 100%);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(12px);
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    .header-title {
        font-size: 2.5rem;
        margin: 0;
        background: linear-gradient(90deg, #A855F7 0%, #6366F1 50%, #00D2C4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 0.6rem;
        line-height: 1.5;
        font-weight: 300;
    }
    
    /* Custom Chip Button Suggestion styling */
    .suggestion-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        color: #94A3B8;
        margin-bottom: 0.75rem;
        font-size: 0.95rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    
    /* Premium button custom styles for Streamlit standard buttons */
    div.stButton > button {
        background-color: #121724 !important;
        color: #CBD5E1 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.02em !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #1E293B !important;
        border-color: rgba(99, 102, 241, 0.6) !important;
        color: #A5B4FC !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.15) !important;
    }
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    /* Specific styling for the Clear Chat History button */
    .reset-btn-container div.stButton > button {
        background-color: #1A1215 !important;
        border-color: rgba(239, 68, 68, 0.25) !important;
        color: #FCA5A5 !important;
    }
    .reset-btn-container div.stButton > button:hover {
        background-color: #2D1418 !important;
        border-color: rgba(239, 68, 68, 0.6) !important;
        color: #FEE2E2 !important;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.15) !important;
    }
    
    /* Native Chat Message Component override */
    [data-testid="stChatMessage"] {
        background-color: #0E121E !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 14px !important;
        margin-bottom: 1.2rem !important;
        padding: 1.2rem 1.6rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
        transition: border 0.3s ease;
    }
    [data-testid="stChatMessage"]:hover {
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* Distinct User message styling */
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
        background-color: rgba(20, 26, 42, 0.95) !important;
        border: 1px solid rgba(99, 102, 241, 0.2) !important;
    }
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"]:hover {
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
    }
    
    /* Avatars customizations */
    [data-testid="stChatMessage"] [data-testid="stAvatar"] {
        background-color: #6366F1 !important;
        border-radius: 50% !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.3) !important;
    }
    [data-testid="stChatMessage"]:nth-child(even) [data-testid="stAvatar"] {
        background-color: #A855F7 !important;
        box-shadow: 0 0 10px rgba(168, 85, 247, 0.3) !important;
    }
    
    /* Form input element refinements */
    [data-testid="stTextInput"] input, [data-testid="stSelectbox"] > div {
        background-color: #121724 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #8A2BE2 !important;
        box-shadow: 0 0 0 2px rgba(138, 43, 226, 0.25) !important;
    }
    
    /* Dynamic file uploader customizations */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.01) !important;
        border: 1px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #A855F7 !important;
        background-color: rgba(168, 85, 247, 0.03) !important;
    }
    
    /* Config indicator badge */
    .indicator-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0.5rem;
        width: 100%;
        box-sizing: border-box;
    }
    .badge-success {
        background-color: rgba(16, 185, 129, 0.08);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .badge-error {
        background-color: rgba(244, 63, 94, 0.08);
        color: #FB7185;
        border: 1px solid rgba(244, 63, 94, 0.2);
    }
    
    /* Plotly container adjustments */
    .plotly-container {
        background: #0E121E;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1.2rem;
        margin-top: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Scrollbar enhancements */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE INIT -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_df" not in st.session_state:
    st.session_state.active_df = get_default_df()
    st.session_state.dataset_name = "Default Retail Sales Dataset (12 Months)"
    st.session_state.is_custom_dataset = False

if "suggestion_clicked" not in st.session_state:
    st.session_state.suggestion_clicked = None

# Helper to clear chat history
def reset_conversation():
    st.session_state.messages = []
    st.session_state.suggestion_clicked = None

# Helper to reset to default dataset
def reset_dataset():
    st.session_state.active_df = get_default_df()
    st.session_state.dataset_name = "Default Retail Sales Dataset (12 Months)"
    st.session_state.is_custom_dataset = False
    reset_conversation()

# ----------------- SIDEBAR CONFIG PANEL -----------------
with st.sidebar:
    st.markdown("### 🚀 Groq API Setup")
    
    # Check for keys in environment variables
    env_groq_key = os.getenv("GROQ_API_KEY", "")
    
    # Input override fields (default to environment values)
    groq_key = st.text_input("Groq API Key", value=env_groq_key, type="password", help="Input Groq API key. Get it from https://console.groq.com")
    
    # Status badges
    st.markdown("##### 🔌 Connection Status")
    
    groq_active = len(groq_key.strip()) > 0
    
    if groq_active:
        st.markdown('<div class="indicator-badge badge-success">Groq Active (Llama 3.3 70B)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="indicator-badge badge-error">Groq Offline</div>', unsafe_allow_html=True)
        
    if not groq_active:
        st.warning("⚠️ No Groq API key detected. Please provide a key in a local .env file or input one above to activate the model.")
        
    st.markdown("---")
    st.markdown("### 📊 Dataset Manager")
    st.markdown(f"**Loaded:** *{st.session_state.dataset_name}*")
    
    # CSV Uploader for custom datasets
    uploaded_file = st.file_uploader(
        "Upload Custom CSV Dataset",
        type=["csv"],
        help="Upload your own structured CSV. The chatbot will dynamically clean, auto-detect column structures, and answer questions about it."
    )
    
    if uploaded_file is not None:
        try:
            custom_df = validate_uploaded_csv(uploaded_file)
            st.session_state.active_df = custom_df
            st.session_state.dataset_name = f"Uploaded CSV ({uploaded_file.name})"
            st.session_state.is_custom_dataset = True
            st.success("✅ CSV uploaded and mapped successfully!")
        except Exception as e:
            st.error(f"Failed to parse CSV: {str(e)}")
            
    # Button to restore defaults
    if st.session_state.is_custom_dataset:
        if st.button("Restore Default Dataset", help="Reverts back to the retail monthly sales dataset."):
            reset_dataset()
            st.rerun()
            
    # Collapsible table viewer for loaded data
    with st.expander("🔍 View Active Dataset Table", expanded=False):
        st.dataframe(
            st.session_state.active_df,
            use_container_width=True,
            height=250
        )
        st.markdown(f"**Records:** {len(st.session_state.active_df)} rows")
        
    # Reset conversation button in the sidebar
    st.markdown('<div class="reset-btn-container">', unsafe_allow_html=True)
    if st.button("🔄 Clear Chat History", use_container_width=True):
        reset_conversation()
        st.success("Conversation cleared!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- MAIN UI CONTENT -----------------
# Header Brand Panel
st.markdown("""
<div class="header-container">
    <h1 class="header-title">DataBot — AI Data Analyst</h1>
    <div class="header-subtitle">Have a plain English conversation with your retail sales or custom uploaded datasets to instantly extract text insights and dynamic Plotly charts.</div>
</div>
""", unsafe_allow_html=True)

# Main container for suggestion prompts (Only render if conversation is empty)
if len(st.session_state.messages) == 0:
    st.markdown('<div class="suggestion-title">💡 Try asking one of these questions:</div>', unsafe_allow_html=True)
    
    # Suggestion boxes layout
    col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)
    
    suggestions = [
        ("📈 Sales Trend", "Show the sales trend over time as a line chart."),
        ("🥇 Best Sales Month", "Which month had the highest sales and what was the revenue?"),
        ("👥 Customer Average", "What is the average number of customers per month?"),
        ("📦 Fewest Returns", "Which month had the fewest product returns?"),
        ("📊 Compare Q1 vs Q4", "Compare Q1 (Jan-Mar) and Q4 (Oct-Dec) sales performance.")
    ]
    
    # If custom dataset is active, provide general suggestion chips
    if st.session_state.is_custom_dataset:
        cols = list(st.session_state.active_df.columns)
        numeric_cols = st.session_state.active_df.select_dtypes(include=['number']).columns.tolist()
        
        suggestions = [
            ("📊 Overall Stats", f"Summarize the key metrics and stats for this dataset."),
            ("📈 Column Distribution", f"Show a bar chart of the distributions in this dataset."),
            ("🔍 Columns Info", f"What columns are present in this dataset and what are their types?"),
            ("⭐ Row Count", f"How many total records are there in this dataset?"),
            ("💡 Summarize Numeric", f"Provide the total sum and averages for numeric columns.")
        ]
        
    with col_s1:
        if st.button(suggestions[0][0], use_container_width=True, help=suggestions[0][1]):
            st.session_state.suggestion_clicked = suggestions[0][1]
    with col_s2:
        if st.button(suggestions[1][0], use_container_width=True, help=suggestions[1][1]):
            st.session_state.suggestion_clicked = suggestions[1][1]
    with col_s3:
        if st.button(suggestions[2][0], use_container_width=True, help=suggestions[2][1]):
            st.session_state.suggestion_clicked = suggestions[2][1]
    with col_s4:
        if st.button(suggestions[3][0], use_container_width=True, help=suggestions[3][1]):
            st.session_state.suggestion_clicked = suggestions[3][1]
    with col_s5:
        if st.button(suggestions[4][0], use_container_width=True, help=suggestions[4][1]):
            st.session_state.suggestion_clicked = suggestions[4][1]

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- CHAT THREAD RENDERING -----------------
# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # If there is parsed chart data, render it inline
        if "chart" in msg and msg["chart"]:
            chart_fig = render_plotly_chart(msg["chart"])
            st.plotly_chart(chart_fig, use_container_width=True)

# ----------------- USER INPUT & PROCESSING -----------------
# Grab prompt: either standard input or suggestion click
user_prompt = st.chat_input("Ask a question about the active dataset...")

if st.session_state.suggestion_clicked:
    user_prompt = st.session_state.suggestion_clicked
    st.session_state.suggestion_clicked = None  # Reset chip latch

if user_prompt:
    # 1. Show user message instantly
    with st.chat_message("user"):
        st.markdown(user_prompt)
        
    # Append to state history
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # 2. Call the active model
    if not groq_active:
        st.error("❌ No Groq API key configured. Please add your key in the sidebar configuration panel to execute.")
    else:
        with st.chat_message("assistant"):
            with st.spinner("🚀 Consulting Groq Llama models..."):
                try:
                    # Call Groq API
                    raw_response = query_groq(groq_key, st.session_state.active_df, st.session_state.messages)
                    
                    # Clean the response and extract chart JSON if present
                    display_content, chart_data = extract_chart_data(raw_response)
                    
                    # Render text response
                    st.markdown(display_content)
                    
                    # If chart was generated, render the interactive Plotly layout
                    if chart_data:
                        chart_fig = render_plotly_chart(chart_data)
                        st.plotly_chart(chart_fig, use_container_width=True)
                        
                    # Save response inside message history (including chart JSON)
                    assistant_msg = {"role": "assistant", "content": display_content}
                    if chart_data:
                        assistant_msg["chart"] = chart_data
                    st.session_state.messages.append(assistant_msg)
                    
                except Exception as e:
                    error_msg = f"⚠️ **DataBot Error**: Could not connect to API or parse response. Details: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
        # Force refresh to keep visual flow smooth
        st.rerun()
