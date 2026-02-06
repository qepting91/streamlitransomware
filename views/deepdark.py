import duckdb
import streamlit as st
import shared_utils

# --- Configuration ---
st.set_page_config(page_title="DeepDark Intelligence", page_icon="🕸️", layout="wide")

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

con = shared_utils.get_db_connection()


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

    # --- Intelligence Matrix ---
    # --- Intelligence Matrix (Default View) ---
    st.header("🔗 Infrastructure Correlation")
    st.info("Live correlation between known victims, threat actors, and their active Tor infrastructure.")
    
    try:
        # Default: Show the clean table
        graph_df = con.execute("SELECT * FROM v_intel_graph").df()
        st.dataframe(graph_df, width="stretch", hide_index=True)
    except Exception as e:
        st.error(f"Matrix View Unavailable: {e}")

    st.divider()

    # --- 🎯 Target Analysis (On-Demand Pivot) ---
    st.header("🎯 Target Analysis")
    st.caption("Generate a focused link analysis graph for a specific Threat Actor or Victim.")

    # 1. Selection Controls
    col_sel1, col_sel2 = st.columns([1, 2])
    with col_sel1:
        entity_type = st.radio("Entity Type", ["Threat Actor", "Victim Organization"], horizontal=True)

    with col_sel2:
        if entity_type == "Threat Actor":
            # Fetch active groups
            opts = con.execute("SELECT DISTINCT group_name FROM victims ORDER BY group_name").fetchall()
            options = [o[0] for o in opts]
            label = "Select Threat Actor"
        else:
            # Fetch recent victims
            opts = con.execute("""
                SELECT DISTINCT victim_name FROM victims 
                ORDER BY discovered_date DESC LIMIT 100
            """).fetchall()
            options = [o[0] for o in opts]
            label = "Select Victim (Last 100)"
        
        selected_entity = st.selectbox(label, options, index=None, placeholder="Choose target...")

    # 2. Dynamic Graph Generation
    if selected_entity:
        try:
            dot = """
            digraph G {
                bgcolor="#0e1117"
                rankdir=LR
                node [fontname="Helvetica", fontcolor="white", fontsize=10]
                edge [color="#555555", arrowsize=0.5]
            """
            
            if entity_type == "Threat Actor":
                actor = selected_entity
                # A. Central Node (Actor)
                dot += f'    "{actor}" [label="{actor}", shape=doublecircle, style=filled, color="#e74c3c", fillcolor="#e74c3c", fontcolor="white", penwidth=0];\n'
                
                # B. Get Victims (Right)
                vic_rows = con.execute("SELECT victim_name FROM victims WHERE group_name = ? ORDER BY discovered_date DESC LIMIT 20", [actor]).fetchall()
                if vic_rows:
                    dot += '\n    node [shape=note, style=filled, color="#2ecc71", fillcolor="#2ecc7120", penwidth=0];\n'
                    for v in vic_rows:
                        v_name = v[0]
                        v_id = f"vic_{abs(hash(v_name))}"
                        dot += f'    "{v_id}" [label="{v_name[:15]}"];\n'
                        dot += f'    "{actor}" -> "{v_id}";\n'

                # C. Get Infrastructure (Left)
                infra_rows = con.execute("SELECT url FROM darkweb_assets WHERE name = ? AND url IS NOT NULL", [actor]).fetchall()
                if infra_rows:
                    dot += '\n    node [shape=component, style=filled, color="#ff9f1c", fillcolor="#ff9f1c40", penwidth=0];\n'
                    for i in infra_rows:
                        url = i[0]
                        u_id = f"url_{abs(hash(url))}"
                        dot += f'    "{u_id}" [label="{url[:20]}..."];\n'
                        dot += f'    "{u_id}" -> "{actor}" [dir=back];\n'

            else:  # Victim Selected
                victim = selected_entity
                # A. Central Node (Victim)
                v_id = f"vic_{abs(hash(victim))}"
                dot += f'    "{v_id}" [label="{victim}", shape=note, style=filled, color="#2ecc71", fillcolor="#2ecc71", fontcolor="white", penwidth=0];\n'
                
                # B. Get Attributing Actor(s) (Left)
                act_rows = con.execute("SELECT group_name FROM victims WHERE victim_name = ?", [victim]).fetchall()
                if act_rows:
                    dot += '\n    node [shape=doublecircle, style=filled, color="#e74c3c", fillcolor="#e74c3c40", fontcolor="white", penwidth=0];\n'
                    for a in act_rows:
                        actor = a[0]
                        dot += f'    "{actor}" [label="{actor}"];\n'
                        dot += f'    "{actor}" -> "{v_id}";\n'

            dot += "}"
            st.graphviz_chart(dot, use_container_width=True)

        except Exception as e:
            st.error(f"Visualization Error: {e}")
    else:
        st.info("👆 Select a target above to generate intelligence graph.")

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
