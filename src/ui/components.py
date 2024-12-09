import streamlit as st

def setup_page_config():
    """Configure the Streamlit page with Apple-inspired styling."""
    st.set_page_config(
        page_title="Marketing Impact Simulator",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply custom CSS for Apple-inspired styling and reduced spacing
    st.markdown("""
        <style>
        .stApp {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .stButton button {
            border-radius: 8px;
            background-color: #007AFF;
        }
        .stTextInput input {
            border-radius: 8px;
        }
        .stNumberInput input {
            border-radius: 8px;
        }
        .stSlider div {
            color: #007AFF;
        }
        .stProgress div {
            background-color: #007AFF;
        }
        
        /* Reduce header spacing */
        .main .block-container {
            padding-top: 2rem;
        }
        header {
            display: none;
        }
        
        /* Reduce sidebar spacing */
        section[data-testid="stSidebar"] {
            padding-top: 0;
            background-color: #0E1117;
        }
        [data-testid="stSidebarContent"] {
            padding-top: 3rem;
        }
        [data-testid="stSidebarContent"] > div {
            padding-top: 0;
        }
        [data-testid="stSidebarContent"] .block-container {
            padding-top: 0;
        }
        
        /* Adjust title margins */
        .main .block-container h1:first-child {
            margin-top: 0;
            padding-top: 0;
        }
        [data-testid="stSidebarContent"] h1:first-child {
            margin-top: 0;
            padding-top: 1rem;
        }
        
        /* Adjust sidebar elements spacing */
        .element-container {
            margin-bottom: 0;
        }
        .stSlider {
            padding-top: 0;
            padding-bottom: 0;
        }
        </style>
    """, unsafe_allow_html=True)
