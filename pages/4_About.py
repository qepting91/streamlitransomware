import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

import duckdb
import shared_utils

@st.cache_resource
def get_db_connection():
    try:
        token = st.secrets.get("MOTHERDUCK_TOKEN")
        if token:
            return duckdb.connect(f'md:?motherduck_token={token}')
        else:
            return duckdb.connect('ransomstat.duckdb', read_only=True)
    except Exception as e:
        return None

con = get_db_connection()
shared_utils.render_analyst_tools(con)

st.markdown("# ℹ️ About RansomStat CTI v2.0")

st.markdown("""
### 🛡️ Mission
**RansomStat CTI** provides analysts, researchers, and defenders with a real-time, consolidated view of the ransomware landscape. By aggregating high-fidelity data from leak sites, dark web forums, and offensive dorks, it enables proactive threat hunting and infrastructure monitoring.

### 🌟 Key Capabilities
*   **📡 Threat Ticker**: Real-time feed of confirmed victims from the [RansomLook API](https://www.ransomlook.io).
*   **🧙‍♂️ Dork Generator**: Automated offensive search queries from the [Google Hacking Database](https://www.exploit-db.com/google-hacking-database) to discover exposed assets.
*   **🕸️ Intelligence Graph**: Visual correlation between Threat Groups and their Dark Web infrastructure (Tor sites, mirrors, chat panels).
*   **📚 Wiki**: Curated knowledge base of ransomware families and TTPs.

### 🏗️ Architecture
*   **Frontend**: Streamlit 1.52 (Python 3.13)
*   **Database**: MotherDuck (Serverless DuckDB) / Local DuckDB
*   **Ingestion**: Custom AsyncIO Crawler (`etl_engine.py`)
*   **Data Sources**: RansomLook, DeepDarkCTI, Exploit-DB

### ⚖️ Disclaimer
> *This tool is intended for **educational and defensive research purposes only**. The developers assume no liability and are not responsible for any misuse or damage caused by this program. access to dark web content should be performed with caution and assumed risk.*

### 👨‍💻 Project Hub
**Source Code**: [qepting91/streamlitransomware](https://github.com/qepting91/streamlitransomware)  
**Maintained By**: [qepting91](https://github.com/qepting91)
""")
