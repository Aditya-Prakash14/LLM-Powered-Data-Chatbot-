import streamlit as st
import pandas as pd
import json
import os
import uuid
import time
import base64
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

# ============= ENHANCED STYLING =============
st.markdown("""
<style>
    :root {
        --primary: #8A2BE2;
        --primary-dark: #6A1B92;
        --secondary: #00D2C4;
        --bg-dark: #0E1117;
        --bg-light: #161B22;
        --text-primary: #E8EAED;
        --text-secondary: #8B949E;
        --success: #3FB950;
        --warning: #D29922;
        --error: #F85149;
        --border: #30363D;
    }
    
    /* Main app styling */
    body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0E1117 0%, #1a1f2e 100%);
        color: var(--text-primary);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    /* Headers with gradient */
    h1, h2, h3 {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* Cards and containers */
    [data-testid="stMetricValue"] {
        color: var(--secondary) !important;
        font-size: 2em !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }
    
    /* Buttons */
    button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(138, 43, 226, 0.3) !important;
    }
    
    /* Input fields */
    input, textarea, select {
        background: var(--bg-light) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }
    
    input:focus, textarea:focus {
        border-color: var(--secondary) !important;
        box-shadow: 0 0 10px rgba(0, 210, 196, 0.2) !important;
    }
    
    /* Chat messages */
    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    }
    
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, var(--secondary) 0%, #00a8a0 100%) !important;
    }
    
    /* Badges and indicators */
    .indicator-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85em;
        margin: 4px 0;
    }
    
    .badge-success {
        background: rgba(63, 185, 80, 0.15);
        color: var(--success);
        border: 1px solid var(--success);
    }
    
    .badge-error {
        background: rgba(248, 81, 73, 0.15);
        color: var(--error);
        border: 1px solid var(--error);
    }
    
    .badge-warning {
        background: rgba(210, 153, 34, 0.15);
        color: var(--warning);
        border: 1px solid var(--warning);
    }
    
    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    
    /* Dividers */
    hr {
        border-color: var(--border) !important;
    }
    
    /* Tabs */
    [role="tablist"] {
        border-bottom: 2px solid var(--border) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary);
    }
    
    /* Loading spinner */
    .stSpinner {
        color: var(--secondary) !important;
    }
    
    /* Success/Error messages */
    [data-testid="stAlert"] {
        border-radius: 8px !important;
    }
    
    .reset-btn-container {
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)
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
from utils.database import (
    init_database,
    get_or_create_user,
    save_conversation,
    get_conversations,
    load_conversation,
    log_query,
    get_query_history,
    save_user_preferences,
    get_user_preferences,
    get_conversation_stats,
    create_user_account,
    get_user_by_username,
    update_last_login,
    save_query_template,
    get_saved_queries,
    use_saved_query,
    get_query_patterns,
    track_query_pattern,
    get_dataset_usage,
    get_query_analytics,
    get_response_time_stats,
    get_chart_usage_stats
)
from utils.export import (
    generate_pdf_report,
    generate_excel_report,
    send_email_report
)
from utils.auth import (
    hash_password,
    verify_password,
    encrypt_api_key,
    decrypt_api_key,
    generate_session_token
)

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

# Initialize database
init_database()

# ============= AUTHENTICATION SESSION STATE =============
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.show_login = True

# ============= SESSION STATE INIT -----------------
if st.session_state.authenticated:
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.session_state.user_id = str(uuid.uuid4())
        st.session_state.user = get_or_create_user(st.session_state.user_id)

    if "conv_id" not in st.session_state:
        st.session_state.conv_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "active_df" not in st.session_state:
        st.session_state.active_df = get_default_df()
        st.session_state.dataset_name = "Default Retail Sales Dataset (12 Months)"
        st.session_state.is_custom_dataset = False

    if "suggestion_clicked" not in st.session_state:
        st.session_state.suggestion_clicked = None
    
    if "page" not in st.session_state:
        st.session_state.page = "chat"

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
# ============= AUTHENTICATION PAGE =============
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-top: 100px;'>🤖 DataBot</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #8A2BE2;'>AI Data Analyst Chatbot</h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Tab for login/register
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with tab1:
            st.markdown("### Welcome Back!")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    user = get_user_by_username(username)
                    if user and verify_password(password, user["password_hash"]):
                        st.session_state.authenticated = True
                        st.session_state.user_id = user["user_id"]
                        st.session_state.username = username
                        st.session_state.user = get_or_create_user(user["user_id"])
                        update_last_login(user["user_id"])
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        
        with tab2:
            st.markdown("### Create New Account")
            new_username = st.text_input("Choose Username", key="register_username")
            new_email = st.text_input("Email Address", key="register_email")
            new_password = st.text_input("Password", type="password", key="register_password")
            new_password_confirm = st.text_input("Confirm Password", type="password", key="register_password_confirm")
            
            if st.button("Register", use_container_width=True, type="primary"):
                if not new_username or not new_password or not new_email:
                    st.error("❌ Please fill in all fields")
                elif new_password != new_password_confirm:
                    st.error("❌ Passwords do not match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    user_id = str(uuid.uuid4())
                    password_hash = hash_password(new_password)
                    
                    if create_user_account(user_id, new_username, password_hash, new_email):
                        st.success("✅ Account created! Please log in.")
                        st.rerun()
                    else:
                        st.error("❌ Username already exists. Please choose another.")
        
        st.markdown("---")
        st.markdown("### Demo Access")
        if st.button("Continue as Demo User 👥", use_container_width=True):
            demo_id = "demo_user_" + str(hash("demo"))[:8]
            st.session_state.authenticated = True
            st.session_state.user_id = demo_id
            st.session_state.username = "Demo User"
            st.session_state.user = get_or_create_user(demo_id, "demo@example.com")
            st.rerun()
    
    st.stop()

# ============= MAIN APP (AUTHENTICATED USERS ONLY) =============
# Only code below this line runs for authenticated users

# Top navigation bar
col1, col2, col3 = st.columns([3, 1, 1])
with col3:
    st.markdown(f"**👤 {st.session_state.username}**")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()

# Page navigation tabs
st.markdown("---")
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.page = "chat"
with nav_col2:
    if st.button("📊 Analytics", use_container_width=True):
        st.session_state.page = "analytics"
with nav_col3:
    if st.button("💾 Saved Queries", use_container_width=True):
        st.session_state.page = "saved_queries"
with nav_col4:
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.page = "settings"

st.markdown("---")

# Page content routing
if st.session_state.page == "analytics":
    st.markdown("# 📊 Analytics Dashboard")
    
    stats = get_conversation_stats(st.session_state.user_id)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Conversations", stats["total_conversations"])
    with col2:
        st.metric("Queries", stats["total_queries"])
    with col3:
        st.metric("Charts", stats["charts_generated"])
    with col4:
        st.metric("Avg Response (ms)", f"{stats['avg_execution_time_ms']:.0f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🔥 Most Asked Patterns")
        patterns = get_query_patterns(st.session_state.user_id, 5)
        if patterns:
            for i, p in enumerate(patterns, 1):
                st.markdown(f"{i}. **{p['keyword']}** ({p['frequency']}x)")
    
    with col2:
        st.markdown("### 📂 Dataset Usage")
        datasets = get_dataset_usage(st.session_state.user_id)
        if datasets:
            st.bar_chart(pd.DataFrame(list(datasets.items()), columns=["Dataset", "Count"]).set_index("Dataset"))

elif st.session_state.page == "saved_queries":
    st.markdown("# 💾 Saved Queries")
    
    if st.button("➕ Add New Query"):
        st.session_state.show_save_form = True
    
    if st.session_state.get("show_save_form"):
        with st.form("save_query"):
            title = st.text_input("Title")
            query = st.text_area("Query")
            dataset = st.text_input("Dataset (optional)")
            
            if st.form_submit_button("Save"):
                if title and query:
                    save_query_template(st.session_state.user_id, title, query, dataset or "Any")
                    st.success("✅ Saved!")
                    st.rerun()
    
    queries = get_saved_queries(st.session_state.user_id)
    for q in queries:
        with st.expander(f"📌 {q['title']} ({q['usage_count']}x)"):
            st.write(q['query_text'])
            if st.button(f"Use", key=f"q{q['query_id']}"):
                use_saved_query(q['query_id'])
                st.session_state.page = "chat"
                st.rerun()

elif st.session_state.page == "settings":
    st.markdown("# ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email", value=st.session_state.user.get("email", ""))
    with col2:
        theme = st.selectbox("Theme", ["Dark", "Light"])
    
    st.markdown("---")
    st.markdown("### 📧 Email Export Settings")
    sender_email = st.text_input("Gmail Address", type="password")
    sender_password = st.text_input("App Password", type="password")
    
    if st.button("Save Settings"):
        prefs = get_user_preferences(st.session_state.user_id)
        prefs.update({"theme": theme, "sender_email": sender_email, "sender_password": sender_password})
        save_user_preferences(st.session_state.user_id, prefs)
        st.success("✅ Saved!")

else:  # Chat page
    st.markdown("# 💬 DataBot Chat")
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
    
    # ============ ADVANCED SETTINGS ============
    with st.expander("⚙️ Advanced Settings", expanded=False):
        st.markdown("#### 👤 User Profile")
        user_email = st.text_input("Email Address", value=st.session_state.user.get("email", ""), help="Used for report exports")
        
        if user_email:
            st.session_state.user["email"] = user_email
        
        st.markdown("#### 📧 Email Settings")
        sender_email = st.text_input("Sender Email", type="password", help="Gmail address for sending reports")
        sender_password = st.text_input("Email Password", type="password", help="Gmail app password (not regular password)")
        
        if sender_email and sender_password:
            prefs = get_user_preferences(st.session_state.user_id)
            prefs["sender_email"] = sender_email
            prefs["sender_password"] = sender_password
            save_user_preferences(st.session_state.user_id, prefs)
    
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
    
    st.markdown("---")
    st.markdown("### 📚 Conversation History")
    
    conversations = get_conversations(st.session_state.user_id)
    
    if conversations:
        selected_conv = st.selectbox(
            "Load Previous Conversation",
            options=[f"{c['title']} ({c['created_at'][:10]})" for c in conversations],
            help="Select a conversation to load it"
        )
        
        if selected_conv:
            conv_index = [f"{c['title']} ({c['created_at'][:10]})" for c in conversations].index(selected_conv)
            if st.button("📂 Load Conversation", use_container_width=True):
                loaded_conv = load_conversation(conversations[conv_index]["conv_id"])
                if loaded_conv:
                    st.session_state.messages = loaded_conv["messages"]
                    st.session_state.conv_id = loaded_conv["conv_id"]
                    st.session_state.dataset_name = loaded_conv["dataset_name"]
                    st.success(f"✅ Loaded: {loaded_conv['title']}")
                    st.rerun()
    else:
        st.info("💡 No previous conversations. Start a new one!")
    
    st.markdown("---")
    st.markdown("### 📈 Analytics")
    
    stats = get_conversation_stats(st.session_state.user_id)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Conversations", stats["total_conversations"])
        st.metric("Avg Response (ms)", f"{stats['avg_execution_time_ms']:.0f}")
    with col2:
        st.metric("Total Queries", stats["total_queries"])
        st.metric("Charts Generated", stats["charts_generated"])
    
    st.markdown("---")
    st.markdown("### 💾 Export & Actions")
    
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        if st.button("📄 Export PDF", use_container_width=True) and st.session_state.messages:
            pdf_data = generate_pdf_report(st.session_state.messages, st.session_state.dataset_name)
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name=f"report_{st.session_state.conv_id[:8]}.pdf",
                mime="application/pdf"
            )
    
    with export_col2:
        if st.button("📊 Export Excel", use_container_width=True) and st.session_state.messages:
            excel_data = generate_excel_report(st.session_state.messages, st.session_state.dataset_name)
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"report_{st.session_state.conv_id[:8]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # Email export
    if st.session_state.messages:
        prefs = get_user_preferences(st.session_state.user_id)
        if prefs.get("sender_email") and prefs.get("sender_password"):
            if st.button("📧 Send Report via Email", use_container_width=True):
                with st.spinner("Sending email..."):
                    success = send_email_report(
                        recipient_email=st.session_state.user.get("email", ""),
                        sender_email=prefs["sender_email"],
                        sender_password=prefs["sender_password"],
                        subject=f"DataBot Report - {st.session_state.dataset_name}",
                        messages=st.session_state.messages
                    )
                    if success:
                        st.success("✅ Email sent successfully!")
                    else:
                        st.error("❌ Failed to send email. Check your credentials.")
        else:
            st.info("⚙️ Configure email in Advanced Settings to enable email export")
    
    # Reset conversation button in the sidebar
    st.markdown('<div class="reset-btn-container">', unsafe_allow_html=True)
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conv_id = str(uuid.uuid4())
        st.session_state.suggestion_clicked = None
        st.success("New conversation started!")
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
                    # Track execution time
                    start_time = time.time()
                    
                    # Call Groq API
                    raw_response = query_groq(groq_key, st.session_state.active_df, st.session_state.messages)
                    
                    execution_time_ms = (time.time() - start_time) * 1000
                    
                    # Clean the response and extract chart JSON if present
                    display_content, chart_data = extract_chart_data(raw_response)
                    
                    # Render text response
                    st.markdown(display_content)
                    
                    # Show execution time
                    st.caption(f"⏱️ Response time: {execution_time_ms:.0f}ms")
                    
                    # If chart was generated, render the interactive Plotly layout
                    if chart_data:
                        chart_fig = render_plotly_chart(chart_data)
                        st.plotly_chart(chart_fig, use_container_width=True)
                        
                    # Save response inside message history (including chart JSON)
                    assistant_msg = {"role": "assistant", "content": display_content}
                    if chart_data:
                        assistant_msg["chart"] = chart_data
                    st.session_state.messages.append(assistant_msg)
                    
                    # Log query to database
                    log_query(
                        user_id=st.session_state.user_id,
                        conv_id=st.session_state.conv_id,
                        query=user_prompt,
                        response=display_content,
                        has_chart=chart_data is not None,
                        execution_time_ms=execution_time_ms
                    )
                    
                except Exception as e:
                    error_msg = f"⚠️ **DataBot Error**: Could not connect to API or parse response. Details: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
    # Save conversation to database
    save_conversation(
        user_id=st.session_state.user_id,
        conv_id=st.session_state.conv_id,
        title=user_prompt[:50] if user_prompt else "Untitled",
        dataset_name=st.session_state.dataset_name,
        messages=st.session_state.messages
    )
    
    # Force refresh to keep visual flow smooth
    st.rerun()
