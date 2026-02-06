# 🚀 RansomStat CTI v2.0

**RansomStat CTI** is a next-generation threat intelligence dashboard designed for analysts, researchers, and defenders. It aggregates data from multiple high-fidelity sources to provide a real-time view of the ransomware landscape, actionable offensive dorks, and intelligence correlations.

[![CI](https://github.com/qepting91/streamlitransomware/workflows/Python%20Code%20Integrity/badge.svg)](https://github.com/qepting91/streamlitransomware/actions/workflows/ci.yml)
[![Security](https://github.com/qepting91/streamlitransomware/workflows/Security%20Pipeline/badge.svg)](https://github.com/qepting91/streamlitransomware/actions/workflows/security.yml)
[![Docs](https://github.com/qepting91/streamlitransomware/workflows/Deploy%20Documentation/badge.svg)](https://github.com/qepting91/streamlitransomware/actions/workflows/deploy-docs.yml)

📖 **[View Full Documentation](https://qepting91.github.io/streamlitransomware/)** | [CI/CD Pipeline](https://qepting91.github.io/streamlitransomware/ci-cd) | [Live Dashboard](https://ransomstat.streamlit.app)

## 🌟 Key Features

### 📡 Threat Ticker
*   **Real-Time Data**: Live feed of confirmed victims ingested from [RansomLook](https://www.ransomlook.io).
*   **Drill-Down Profiles**: Analyze Threat Groups (LockBit, Qilin, Play) with detailed activity logs and .onion mirror status.
*   **Advanced Search**: Robust searching of victims and groups with time-window filtering (Lookback Days).

### 🧙‍♂️ Google Dork Generator
*   **Offensive Intel**: Automated generation of Google Dorks based on [Exploit-DB (GHDB)](https://www.exploit-db.com/google-hacking-database) categories.
*   **One-Click Hunting**: Direct "Search 🔍" links to execute queries instantly.
*   **Sanitized Output**: Clean, copy-paste ready queries stripped of HTML artifacts.

### 🕸️ DeepDark Intelligence
*   **Target Analysis**: On-demand Pivot Graphs to visualize relationships. Select a specific **Actor** to see their network, or a **Victim** to see who claimed them.
*   **Infrastructure Correlation**: Clean matrix view of known victims, threat actors, and active Tor infrastructure.
*   **Data Sources**: Fuses data from RansomLook Direct Crawls and [DeepDarkCTI](https://github.com/fastfire/deepdarkCTI).

### 🛠️ Analyst Tools
*   **Voice Intelligence**: Record voice notes directly in the browser; transcripts are auto-saved to your session.
*   **Session Notepad**: Persistent scratchpad for tracking indicators during an investigation.
*   **Export**: Download your transcripts and notes as a Markdown report.

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
streamlit run app.py
```

*Note: The main entry point is `app.py`.*

---

## 🏗️ Architecture

*   **Frontend**: Streamlit 1.52
*   **Engine**: Python 3.13 (AsyncIO)
*   **Database**: DuckDB (Local / MotherDuck Serverless)
*   **ETL**: Custom `etl_engine.py` crawler.

---

## 📖 Documentation

Full documentation is available at **https://qepting91.github.io/streamlitransomware/**

### What's Covered

- **[Getting Started](https://qepting91.github.io/streamlitransomware/)** - Installation, prerequisites, and quick start guide
- **[CI/CD Pipeline](https://qepting91.github.io/streamlitransomware/ci-cd)** - Automated testing, linting, security scanning, and deployment workflows

### For Contributors

Learn about code quality standards, security checks, and how to run tests locally:
- Ruff linting configuration and rules
- Pytest test suite structure
- Bandit security scanning
- Pre-commit hooks setup

---

## 👨‍💻 Credits

Developed by **[qepting91](https://github.com/qepting91)**.  
Powered by Open Source Intelligence.

> **Disclaimer**: This tool is for educational and defensive research purposes only.
