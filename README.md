# 🚀 RansomStat CTI v2.0

**RansomStat CTI** is a next-generation threat intelligence dashboard designed for analysts, researchers, and defenders. It aggregates data from multiple high-fidelity sources to provide a real-time view of the ransomware landscape, actionable offensive dorks, and intelligence correlations.

## 🌟 Key Features

### 📡 Threat Ticker
*   **Real-Time Data**: Live feed of confirmed victims ingested from [RansomLook](https://www.ransomlook.io).
*   **Drill-Down Profiles**: Analyze Threat Groups (LockBit, Qilin, Play) with detailed activity logs and .onion mirror status.
*   **Advanced Search**: Robust searching of victims and groups with time-window filtering (Lookback Days).

### 🧙‍♂️ Google Dork Generator
*   **Offensive Intel**: Automated generation of Google Dorks based on [Exploit-DB (GHDB)](https://www.exploit-db.com/google-hacking-database) categories.
*   **One-Click Hunting**: Direct "Search 🔍" links to execute queries instantly.
*   **Sanitized Output**: Clean, copy-paste ready queries stripped of HTML artifacts.

### 🕸️ DeepDark Intelligence Graph
*   **Infrastructure Correlation**: Visualize connections between Threat Groups and their dark web assets (Chat panels, leak sites).
*   **Data Sources**: Fuses data from RansomLook Direct Crawls and [DeepDarkCTI](https://github.com/fastfire/deepdarkCTI).

### 📚 Analyst Wiki
*   **TTPs & Defense**: Detailed "Senior Analyst" breakdown of Tactics, Techniques, and Procedures.
*   **Threat Profiles**: In-depth profiles of Tier 1 ransomware groups.
*   **Strategic Analysis**: Insight into the RaaS economy and geopolitical drivers.

---

## 🛠️ Installation & Setup

### Prerequisites
*   Python 3.10+
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/qepting91/streamlitransomware.git
cd streamlitransomware
```

### 2. Set up Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.streamlit/secrets.toml` file for database connections (Optional if using local Mode):

```toml
# .streamlit/secrets.toml
[database]
MOTHERDUCK_TOKEN = "your-token-here"
```

---

## 🚀 Usage

Run the application using Streamlit:

```bash
streamlit run Threat_Ticker.py
```

*Note: The main entry point was renamed from `app.py` to `Threat_Ticker.py` in v2.0.*

---

## 🏗️ Architecture

*   **Frontend**: Streamlit 1.52
*   **Engine**: Python 3.13 (AsyncIO)
*   **Database**: DuckDB (Local / MotherDuck Serverless)
*   **ETL**: Custom `etl_engine.py` crawler.

---

## 👨‍💻 Credits

Developed by **[qepting91](https://github.com/qepting91)**.  
Powered by Open Source Intelligence.

> **Disclaimer**: This tool is for educational and defensive research purposes only.
