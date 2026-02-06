import streamlit as st

import shared_utils

# --- Configuration & Styling ---
st.set_page_config(
    page_title="RansomStat CTI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Navigation Setup ---
# Define the pages
dashboard_page = st.Page("views/dashboard.py", title="War Room", icon="🚀", default=True)
dork_page = st.Page("views/dork_generator.py", title="Dork Generator", icon="🔍")
deepdark_page = st.Page("views/deepdark.py", title="DeepDark Intelligence", icon="🕸️")
wiki_page = st.Page("views/wiki.py", title="Tradecraft Wiki", icon="📚")
about_page = st.Page("views/about.py", title="About", icon="ℹ️")

# Build the navigation
pg = st.navigation({
    "Operations": [dashboard_page, dork_page],
    "Intelligence": [deepdark_page, wiki_page],
    "System": [about_page]
})

# --- Shared Sidebar ---
# We render the shared sidebar tools HERE so they persist across all pages
con = shared_utils.get_db_connection()
if con:
    shared_utils.render_analyst_tools(con)

# --- Run the App ---
pg.run()
