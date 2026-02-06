import streamlit as st

import shared_utils

# --- Configuration ---
st.set_page_config(page_title="Google Dork Generator", page_icon="🔧", layout="wide")

st.title("🚀 RansomStat CTI // DORK GENERATOR")

# We need 'con' to be defined before passing it, but 'con' is defined later in this file (line 36).
# I should move the sidebar usage AFTER 'con' is defined, or move 'con' definition up.
# Let's check where 'con' is defined. Line 36.
# I will edit the file to insert the sidebar call AFTER line 36.
with st.expander("ℹ️ How to use & Data Sources"):
    st.markdown("""
    **What is this?**
    **Google Dorks** are advanced search queries used to find exposed files, 
    vulnerable servers, and sensitive data indexed by Google.
    
    **Where is the data from?**
    - **Source:** Scraped from the [Google Hacking Database (GHDB)](https://www.exploit-db.com/google-hacking-database).
    
    **How to use:**
    1. **Filter:** Choose a category (e.g., *Sensitive Directories*).
    2. **Select:** Click a row to see the Dork details.
    3. **Copy & Hunt:** Copy the query and test it on Google to identify exposures.
    """)
st.info(
    "Select a GHDB Category matching your target profile. This will "
    "generate Google Dorks to find sensitive exposed assets."
)

con = shared_utils.get_db_connection()

# --- Logic ---
target_domain = st.text_input("Target Domain", "example.com")

categories = ["Select Category"]
if con:
    try:
        cats = con.execute("SELECT DISTINCT category FROM dorks ORDER BY category").fetchall()
        categories += [c[0] for c in cats]
    except Exception:
        pass
        
selected_cat = st.selectbox("GHDB Category", categories)

if selected_cat and selected_cat != "Select Category":
    # Fetch templates for this category
    templates = con.execute(
        "SELECT dork_string, description FROM dorks WHERE category = ? LIMIT 5", 
        [selected_cat]
    ).fetchall()
    
    if templates:
        import urllib.parse

        import pandas as pd

        st.markdown("### Generated Dorks")
        
        import re
        
        dork_data = []
        for tmpl, _desc in templates:
            # Clean template: Remove HTML tags if present (scraped artifact)
            clean_tmpl = re.sub(r'<[^>]+>', '', tmpl).strip()
            
            # Construct the final dork
            final_dork = f"site:{target_domain} {clean_tmpl}"
            # Encode for URL
            encoded_dork = urllib.parse.quote(final_dork)
            google_url = f"https://www.google.com/search?q={encoded_dork}"
            
            dork_data.append({
                "Dork Query": final_dork,
                "Action": google_url
            })
        
        df = pd.DataFrame(dork_data)
        
        st.dataframe(
            df,
            column_config={
                "Dork Query": st.column_config.TextColumn("Dork Query", width="large"),
                "Action": st.column_config.LinkColumn(
                    "Launch",
                    help="Click to run this dork on Google",
                    display_text="Search 🔍"
                )
            },
            hide_index=True,
            use_container_width=True
        )

    else:
        st.info("No templates found for this category.")
