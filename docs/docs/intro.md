---
sidebar_position: 1
---

# Getting Started

Welcome to **RansomStat CTI**. This dashboard allows you to monitor ransomware groups and victims in real-time.

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [DuckDB](https://duckdb.org/)
- [Streamlit](https://streamlit.io/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/qepting91/streamlitransomware.git
   cd streamlitransomware
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Key Features

- **Threat Ticker**: Live feed of victims.
- **Group Profiles**: Analyze specific threat actors.
- **DeepDark Intelligence**: Monitor Tor infrastructure.
- **Google Dork Generator**: OSINT search queries from GHDB.
- **Analyst Tools**: Voice intelligence, session notes, and tradecraft wiki.

## Documentation

- **[CI/CD Pipeline](./ci-cd)**: Learn about automated testing, security scanning, and deployment workflows.

Check the sidebar for more tools!
