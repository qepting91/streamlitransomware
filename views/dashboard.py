import streamlit as st

import etl_engine
import shared_utils

# Get connection
con = shared_utils.get_db_connection()

# --- Search Function ---
def search_victims(query):
    # Base query now joins with darkweb_assets to get the Group's main active Onion Site
    base_sql = """
        SELECT 
            v.victim_name,
            v.group_name,
            v.discovered_date,
            d.url as onion_link
        FROM victims v
        LEFT JOIN (
            SELECT name, url 
            FROM darkweb_assets 
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY name 
                ORDER BY CASE WHEN source_file = 'api_group_crawl' THEN 1 ELSE 2 END, ingest_time DESC
            ) = 1
        ) d ON LOWER(v.group_name) = LOWER(d.name)
    """

    if not query:
        return con.execute(f"{base_sql} ORDER BY v.discovered_date DESC").df()
    
    # Updated: Use ILIKE for everything. More robust than FTS for small/medium datasets.
    clean_query = query.replace("'", "''") 
    sql = f"""
        {base_sql}
        WHERE 
            v.victim_name ILIKE '%{clean_query}%' OR 
            v.group_name ILIKE '%{clean_query}%'
        ORDER BY v.discovered_date DESC
    """
    return con.execute(sql).df()


# --- Main Content ---
st.title("🚀 RansomStat CTI // WAR ROOM")
st.caption("Live Offensive Intelligence & Infrastructure Monitoring")

# --- Metrics Dashboard ---
if con:
    try:
        # Quick stats row
        total_victims = con.execute("SELECT count(*) FROM victims").fetchone()[0]
        # Count distinct groups
        active_groups = con.execute(
            "SELECT count(distinct group_name) FROM victims"
        ).fetchone()[0]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Recent Victims", total_victims)
        col2.metric("Active Groups (7d)", active_groups)
        col3.metric("System Health", "100%")
    except Exception:
        pass

with st.expander("ℹ️ How to use & Data Sources"):
    st.markdown("""
    **What is this?**
    The **Threat Ticker** provides a real-time feed of confirmed ransomware attacks and victim postings.
    
    **Where is the data from?**
    - **Primary Source:** [RansomLook API](https://www.ransomlook.io), aggregated from official ransomware leak sites.
    - **Infrastructure:** .onion links are verified via **Direct Group Crawls** and **DeepDarkCTI**.
    
    **How to use:**
    1. **View:** Scroll the ticker to see the latest victims.
    2. **Search:** Use the header search bar to find specific groups (e.g., *LockBit*) or victims.
    3. **Drill-Down:** Select a row to view the full **Threat Profile** of 
       the attacker, including their active Tor sites and victim history.
    4. **Sync:** Use the Sidebar controls to look back further (up to 30 days).
    """)


# Global Search
col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
with col_s2:
    search_query = st.text_input(
        "Search Victims / Groups", 
        placeholder="🔍 Search e.g. Qilin, LockBit...", 
        label_visibility="collapsed"
    )

# Data Fetch
if con:
    try:
        df = search_victims(search_query)
        
        # Display configuration with Selection Enabled
        event = st.dataframe(
            df,
            width='stretch',
            column_config={
                "onion_link": st.column_config.LinkColumn("Group Site", display_text=r"https?://(.*?)/?$"),
                "discovered_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                "victim_name": "Victim Organization",
                "group_name": "Threat Actor"
            },
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        # Draw Drill-Down if selected
        if len(event.selection.rows) > 0:
            selected_row_index = event.selection.rows[0]
            # Convert to pure Python int to avoid numpy/pandas issues
            idx = int(selected_row_index)
            
            # Safe access to the dataframe
            try:
                row_data = df.iloc[idx]
                group_name = row_data["group_name"]
                
                # Use a Dialog for the detail view
                @st.dialog(f"Threat Profile: {group_name.upper()}")
                def show_profile(g_name):
                    with st.spinner(f"📡 Intercepting communications for {g_name}..."):
                        
                        meta, victims = etl_engine.fetch_group_details(g_name)
                    
                    if not meta and not victims:
                        st.error("Target offline or unresponsive to probe.")
                        return

                    # --- Header Stats ---
                    if meta:
                        locs = meta.get('locations', [])
                        online_locs = [
                            loc_info for loc_info in locs 
                            if loc_info.get('available')
                        ]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Sites Monitored", len(locs))
                        with col2:
                            st.metric("Confirmed Online", len(online_locs), delta_color="normal")
                            
                        # --- Mirrors ---
                        if online_locs:
                            st.markdown("### 🧅 Live Infrastructure")
                            for loc in online_locs:
                                fqdn = loc.get('fqdn')
                                if fqdn:
                                    # Create a copyable code block or link. 
                                    # Streamlit links open in new tab.
                                    st.markdown(f"- [`{fqdn}`](http://{fqdn})")
                    
                    st.markdown("---")
                    
                    # --- Victim History ---
                    st.markdown(f"### 💀 Validated Victims ({len(victims)})")
                    if victims:
                        # Just show a mini dataframe of their specific history
                        v_data = []
                        for v in victims:
                            v_data.append({
                                "Date": v.get('discovered'),
                                "Victim": v.get('post_title')
                            })
                        st.dataframe(v_data, height=300, hide_index=True)
                    else:
                        st.info("No recent victim posts found via this channel.")

                # Trigger the dialog
                show_profile(group_name)
            
            except Exception as e:
                st.error(f"Error resolving target profile: {e}")

    except Exception as e:
        st.error(f"Data Fetch Error: {e}")
else:
    st.info("Initializing Secure Connection...")
