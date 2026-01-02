import streamlit as st
import duckdb

# --- Configuration ---
st.set_page_config(page_title="🕸️ DeepDark Intelligence Graph", page_icon="🕸️", layout="wide")

with st.expander("ℹ️ How to use & Data Sources"):
    st.markdown("""
    **What is this?**
    Visualizes the connections between **Threat Groups** and their **Dark Web Infrastructure** (Mirrors, Chat panels, Blog sites).
    
    **Where is the data from?**
    - **Sources:** DeepDarkCTI and direct RansomLook site crawls.
    
    **How to use:**
    - **Graph:** Zoom and drag nodes. Groups are **Red**, Sites are **Blue**.
    - **Asset Browser:** Search or filter the raw table of .onion addresses.
    """)

st.markdown("# 🕸️ DeepDark Intelligence")
st.caption("Raw monitoring of dark web marketplaces, forums, and ransomware groups.")

# --- Database Connection ---
@st.cache_resource
def get_db_connection():
    try:
        token = st.secrets.get("MOTHERDUCK_TOKEN")
        if token:
            return duckdb.connect(f'md:?motherduck_token={token}')
        else:
            return duckdb.connect('ransomstat.duckdb', read_only=True)
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

con = get_db_connection()

import shared_utils
shared_utils.render_analyst_tools(con)

if con:
    # --- Metrics ---
    try:
        stats = con.execute("""
            SELECT 
                count(*) as total,
                count(CASE WHEN category='Ransomware Group' THEN 1 END) as groups,
                count(CASE WHEN category='Market' THEN 1 END) as markets
            FROM darkweb_assets
        """).fetchone()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Assets", stats[0])
        c2.metric("Active Groups", stats[1])
        c3.metric("Marketplaces", stats[2])
    except:
        pass

    st.divider()

    # --- Intelligence Graph ---
    st.header("🔗 Intelligence Graph (Victim <-> Infra)")
    st.info("Live correlation between known victims, threat actors, and their active Tor infrastructure.")
    try:
        graph_df = con.execute("SELECT * FROM v_intel_graph").df()
        st.dataframe(graph_df, width="stretch", hide_index=True)
    except Exception as e:
        st.error(f"Graph View Unavailable: {e}")

    st.divider()

    # --- Asset Browser ---
    st.header("📂 Asset Browser")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        cat_filter = st.selectbox("Filter by Category", ["All", "Ransomware Group", "Market", "Forum", "MaaS"])
    
    with col2:
        search_filter = st.text_input("Search Assets", placeholder="Name or URL...")
        
    query = "SELECT name, url, category, ingest_time FROM darkweb_assets"
    params = []
    
    conditions = []
    if cat_filter != "All":
        conditions.append("category = ?")
        params.append(cat_filter)
        
    if search_filter:
        conditions.append("name ILIKE ?")
        params.append(f"%{search_filter}%")
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY ingest_time DESC LIMIT 100"
    
    assets_df = con.execute(query, params).df()
    st.dataframe(
        assets_df, 
        width="stretch",
        column_config={
            "url": st.column_config.LinkColumn("Onion Link"),
            "ingest_time": st.column_config.DatetimeColumn("Discovered")
        },
        hide_index=True
    )
