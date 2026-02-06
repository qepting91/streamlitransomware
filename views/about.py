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
    except Exception:
        return None

con = get_db_connection()

st.markdown("# ℹ️ About RansomStat CTI v2.0")

st.markdown("""
### 🛡️ Operational Objective
**RansomStat CTI** provides offensive security researchers and defenders with a consolidated, real-time operating picture of the ransomware landscape. By aggregating high-fidelity signals from criminal leak sites, dark web infrastructure, and OSINT vectors, it enables **proactive threat hunting** rather than reactive monitoring.

### 🌟 Usage & Capabilities
*   **📡 Threat Ticker**: Live telemetry of confirmed victims via the [RansomLook API](https://www.ransomlook.io).
*   **🧙‍♂️ Dork Generator**: Automated offensive queries (Google Hacking) to identify exposed attack surfaces before adversaries do.
*   **🕸️ Infrastructure Correlation**: Visual correlation of Threat Actors to their active Dark Web nodes (Mirrors, Chat Panels, C2).
*   **📚 Tradecraft Wiki**: Field manual for RaaS TTPs and economic models.

### 🏗️ Engineering Stack
*   **Core**: Streamlit 1.54 (Python 3.13)
*   **Data Warehouse**: MotherDuck (Serverless DuckDB)
*   **Ingestion**: AsyncIO Multi-Source Crawler (`etl_engine.py`)
*   **Cyber Threat Intel**: RansomLook, DeepDarkCTI, GHDB

### ⚖️ Rules of Engagement
> *This platform is engineered for **Defensive Research & Education**. Accessing Dark Web content carries inherent risks. The developers assume no liability for misuse. Operate with OPSEC.*

### 👨‍💻 Maintainer
**Source Code**: [qepting91/streamlitransomware](https://github.com/qepting91/streamlitransomware)  
**Lead Dev**: [qepting91](https://github.com/qepting91)
""")
