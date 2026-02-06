
import datetime
import re
from pathlib import Path

import duckdb
import httpx
import tomllib

# --- Configuration ---
SECRETS_PATH = Path(".streamlit/secrets.toml")
DEEPDARK_BASE_URL = "https://raw.githubusercontent.com/fastfire/deepdarkCTI/main/"
DEEPDARK_FILES = {
    "markets.md": "Market",
    "ransomware_gang.md": "Ransomware Group",
    "forum.md": "Forum",
    "maas.md": "MaaS"
}
GHDB_URL = "https://www.exploit-db.com/google-hacking-database"
RANSOMLOOK_LATEST = "https://www.ransomlook.io/api/recent"
RANSOMLOOK_GROUP = "https://www.ransomlook.io/api/group/"

GHDB_CATEGORY_MAP = {
    "1": "Footholds",
    "2": "Files Containing Usernames",
    "3": "Sensitive Directories",
    "4": "Web Server Detection",
    "5": "Vulnerable Files",
    "6": "Vulnerable Servers",
    "7": "Error Messages",
    "8": "Files Containing Juicy Info",
    "9": "Files Containing Passwords",
    "10": "Sensitive Online Shopping Info",
    "11": "Network or Vulnerability Data",
    "12": "Pages Containing Login Portals",
    "13": "Various Online Devices",
    "14": "Advisories and Vulnerabilities"
}


def get_db_connection():
    """Connects to MotherDuck if token exists, else local DuckDB."""
    token = None
    if SECRETS_PATH.exists():
        try:
            with open(SECRETS_PATH, "rb") as f:
                secrets = tomllib.load(f)
                # Handle nested [database] section
                if "database" in secrets:
                    token = secrets["database"].get("motherduck_token")
                else:
                    token = secrets.get("MOTHERDUCK_TOKEN")
        except Exception as e:
            print(f"Warning: Could not read secrets.toml: {e}")
    
    if token:
        print("🔌 Connecting to MotherDuck...")
        return duckdb.connect(f'md:?motherduck_token={token}')
    else:
        print("⚠️ No MotherDuck token found. Using local 'ransomstat.duckdb'.")
        return duckdb.connect('ransomstat.duckdb', read_only=True)

def init_db(con):
    """Initializes tables and views. Non-destructive for Assets/Dorks."""
    print("🏗️ Initializing Database Schema...")
    
    # Enable Jaccard for linking
    con.execute("INSTALL fts; LOAD fts;")
    
    # 1. Dark Web Assets (Persistent - Do not DROP)
    con.execute("""
        CREATE TABLE IF NOT EXISTS darkweb_assets (
            name VARCHAR,
            url VARCHAR,
            category VARCHAR,
            source_file VARCHAR,
            ingest_time TIMESTAMP
        )
    """)
    
    # 2. Dorks (Persistent - Do not DROP)
    con.execute("""
        CREATE TABLE IF NOT EXISTS dorks (
            ghdb_id INTEGER,
            date DATE,
            dork_string VARCHAR,
            category VARCHAR,
            description VARCHAR
        )
    """)
    
    # 3. Victims (Volatile - Always Refresh for Latest Ticker)
    con.execute("""
        DROP TABLE IF EXISTS fts_main_victims_index;
    """)
    con.execute("DROP TABLE IF EXISTS victims")
    con.execute("""
        CREATE TABLE victims (
            victim_name VARCHAR,
            group_name VARCHAR,
            discovered_date DATE,
            country VARCHAR,
            leak_site_url VARCHAR
        )
    """)
    
    # Create FTS Index for Threat Ticker search
    try:
        con.execute("PRAGMA drop_fts_index('victims')")
    except Exception:
        pass
    con.execute("PRAGMA create_fts_index('victims', 'victim_name', 'group_name', 'country')")
    
    print("✅ Schema created (Assets/Dorks Preserved, Victims Refreshed).")

def ingest_deepdark(con):
    """Ingests data from DeepDarkCTI markdown files."""
    print("🕵️ Ingesting DeepDarkCTI...")
    
    # Check if already ingested
    try:
        sql = """
            SELECT count(*) FROM darkweb_assets 
            WHERE category IN ('Market', 'Ransomware Group', 'Forum', 'MaaS')
        """
        count = con.execute(sql).fetchone()[0]
        if count > 0:
            print(f"   ℹ️ Skipping DeepDarkCTI (Found {count} existing records).")
            return
    except Exception:
        pass
    
    regex = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    # Use follow_redirects=True because GitHub raw links sometimes redirect? 
    # Actually raw links usually don't, but good practice.
    with httpx.Client(follow_redirects=True) as client:
        for filename, category in DEEPDARK_FILES.items():
            print(f"   Fetching {filename}...")
            try:
                resp = client.get(DEEPDARK_BASE_URL + filename)
                resp.raise_for_status()
                lines = resp.text.splitlines()
                
                rows = []
                for line in lines:
                    # Logic: Must contain '|' and not be a separator line '---'
                    if '|' in line and '---' not in line:
                         # Apply regex to extract clean Name and URL
                         # The line format is typically | [Name](Url) | Description | ...
                         match = regex.search(line)
                         if match:
                             name = match.group(1).strip()
                             url = match.group(2).strip()
                             rows.append((
                                 name, url, category, filename, 
                                 datetime.datetime.now()
                             ))
                
                if rows:
                    con.executemany("INSERT INTO darkweb_assets VALUES (?, ?, ?, ?, ?)", rows)
                    print(f"   -> Inserted {len(rows)} assets from {filename}")
                    
            except Exception as e:
                print(f"   ❌ Failed to ingest {filename}: {e}")

def ingest_ghdb(con):
    """Ingests Google Dorks from Exploit-DB hidden API."""
    print("🕵️ Ingesting GHDB Dorks...")
    
    # Check if already ingested
    try:
        count = con.execute("SELECT count(*) FROM dorks").fetchone()[0]
        if count > 0:
            print(f"   ℹ️ Skipping GHDB (Found {count} existing records).")
            return
    except Exception:
        pass
    
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    
    # The directives implies fetching the main DB. 
    # The URL provided is the HTML page. 
    # Usually the XHR endpoint is different or the paging defaults to returning 
    # JSON if that header is set on the main URL?
    # Directive says: "This site returns HTML by default. You need the Hidden JSON API." and gives the main URL.
    # We will try hitting the main URL with the headers.
    
    with httpx.Client(headers=headers, timeout=30.0) as client:
        try:
             # Often these 'hidden APIs' are query parameters on the main URL or a 
             # specific endpoint like /google-hacking-database?draw=1...
             # However, based on the prompt "Use these exact headers to trigger "
             # "the JSON response", I will trust the prompt.
             resp = client.get(GHDB_URL)
             if resp.status_code != 200:
                 print(f"   ❌ GHDB returned status {resp.status_code}")
                 return

             # The response might be direct JSON or valid JSON.
             try:
                 data = resp.json()
             except Exception:
                 print(
                     "   ❌ GHDB did not return JSON. The directive might refer "
                     "to a specific datatables endpoint behavior."
                 )
                 # Fallback: Sometimes it's embedded or requires parameters. 
                 # But I must follow "using only public web access" and the info.
                 # Let's assume the prompt is correct that HEADERS trigger it.
                 return

             # Expected JSON format for DataTables often has 'data' key
             dorks_list = data.get('data', [])
             if not dorks_list:
                  # Maybe it's a top level list
                  if isinstance(data, list):
                      dorks_list = data
            
             # Mapping fields. This is guess-work without seeing the exact JSON structure, 
             # but standard GHDB fields are ID, Date, Title (Dork), Category, Author.
             # Prompt Schema: (ghdb_id, date, dork_string, category, description)
             
             rows = []
             for item in dorks_list:
                 # Adjust parsing based on typical ExploitDB structure if we can.
                 # Often: { "id": "5351", "date": "2023-08-01", "url_title": "...", "cat_id": "..." }
                 # Note: The prompt is very specific about using the header. I will try to extract generic fields.
                 
                 ghdb_id = item.get('id', 0)
                 date_str = item.get('date', '1970-01-01')
                 # Description is often the title payload? Or query?
                 # Usually 'url_title' is the description/title. The actual dork code is sometimes separate.
                 # Let's map loosely:
                 dork_string = item.get('url_title', '') # Often the title IS the dork or summary
                 # If there is a separate 'dork' field use it, otherwise use title as placeholder
                 
                 # Parse Category
                 is_cat_dict = isinstance(item.get('category'), dict)
                 if is_cat_dict:
                     raw_cat = item.get('category', {}).get('cat_id', 'Unknown')
                 else:
                     raw_cat = str(item.get('category', 'Unknown'))
                 category = GHDB_CATEGORY_MAP.get(str(raw_cat), f"Category {raw_cat}")
                 
                 # Parse Author
                 is_auth_dict = isinstance(item.get('author'), dict)
                 if is_auth_dict:
                     description = item.get('author', {}).get('name', '')
                 else:
                     description = "Unknown Author"
                 
                 rows.append((ghdb_id, date_str, dork_string, category, description))
                 
             if rows:
                 con.executemany("INSERT INTO dorks VALUES (?, CAST(? AS DATE), ?, ?, ?)", rows)
                 print(f"   -> Inserted {len(rows)} dorks.")

        except Exception as e:
            print(f"   ❌ GHDB Error: {e}")

def ingest_ransomlook(con, days=7):
    """Ingests recent victims from RansomLook for the last N days."""
    print(f"🕵️ Ingesting RansomLook (Last {days} Days)...")
    
    url = f"https://www.ransomlook.io/api/last/{days}"
    
    with httpx.Client(follow_redirects=True) as client:
        try:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            # Data structure: usually a list of dicts
            rows = []
            for item in data:
                # Schema: victim_name, group_name, discovered_date, country, leak_site_url
                victim = item.get('post_title', 'Unknown')
                group = item.get('group_name', 'Unknown')
                date_discovered = item.get('discovered', '1970-01-01') # Adjust if needed
                # Country might not be in 'last' endpoint, usually 'country' or inferred
                country = item.get('country', 'Unknown') 
                # Leak site might need lookup, or provided in a different field
                # For this MVP, we leave leak_site_url null if not present
                raw_link = item.get('link', '') or ''
                leak_site = f"https://www.ransomlook.io{raw_link}" if raw_link.startswith("/") else raw_link
                
                rows.append((victim, group, date_discovered, country, leak_site))
            
            if rows:
                # We want to refresh the victims table completely or upsert?
                # User said "handle database updates".
                # Safest for "Ticker" is to replace or merge.
                # Given init_db clears it, we can just clear and insert if it's a "Reload".
                # But here we might want to append?
                # Simpler: Delete all victims and re-insert to avoid dups if we are syncing "last N days".
                # Or Use INSERT OR IGNORE logic if we had Primary Key.
                # Let's wipe and reload for this specific feature request "update how many days they want to see".
                con.execute("DELETE FROM victims") 
                con.executemany("INSERT INTO victims VALUES (?, ?, CAST(? AS DATE), ?, ?)", rows)
                print(f"   -> Inserted {len(rows)} victims from last {days} days.")
                 
        except Exception as e:
            print(f"   ❌ RansomLook Error: {e}")

def ingest_ransomlook_groups(con):
    """Crawls all groups from RansomLook to get high-fidelity onion links."""
    print("🕵️ Ingesting RansomLook Groups (High Fidelity)...")

    # Check if already ingested
    try:
        sql = "SELECT count(*) FROM darkweb_assets WHERE source_file = 'api_group_crawl'"
        count = con.execute(sql).fetchone()[0]
        if count > 0:
            print(f"   ℹ️ Skipping Group Crawl (Found {count} existing records).")
            return
    except Exception:
        pass

    with httpx.Client(follow_redirects=True, timeout=60.0) as client:
        try:
            # 1. Get List of Groups
            resp = client.get("https://www.ransomlook.io/api/groups")
            resp.raise_for_status()
            groups = resp.json()  # List of names

            print(f"   -> Found {len(groups)} groups. Crawling profiles...")

            assets = []
            for idx, group_name in enumerate(groups):  # noqa: B007
                try:
                    g_url = f"https://www.ransomlook.io/api/group/{group_name}"
                    g_resp = client.get(g_url)
                    if g_resp.status_code == 200:
                        g_data = g_resp.json()
                        locations = g_data.get('locations', [])

                        for loc in locations:
                            onion_url = loc.get('slug') or loc.get('location')
                            if onion_url:
                                assets.append((
                                    group_name, onion_url,
                                    "RansomLook Profile", "api_group_crawl",
                                    datetime.datetime.now()
                                ))
                except Exception:
                    pass

                # Progress every 50
                if idx > 0 and idx % 50 == 0:
                    print(f"      Crawled {idx} groups...")

            if assets:
                sql = "INSERT INTO darkweb_assets VALUES (?, ?, ?, ?, ?)"
                con.executemany(sql, assets)
                print(f"   -> Inserted {len(assets)} high-fidelity assets.")

        except Exception as e:
            print(f"   ❌ RansomLook Group Crawl Error: {e}")

def create_intel_view(con):
    """Creates the graph view linking datasets."""
    print("🧠 Building Intelligence Graph...")
    
    # Updated View: Prefer Exact Matches (RansomLook Profile) > Fuzzy Matches (DeepDarkCTI)
    con.execute("""
        CREATE OR REPLACE VIEW v_intel_graph AS
        SELECT 
            v.group_name AS threat_actor,
            v.victim_name AS recent_victim,
            d.name AS infrastructure_name,
            d.url AS onion_link
        FROM victims v
        JOIN darkweb_assets d 
          ON (
              -- Priority 1: Exact Match (RansomLook Crawl)
              (d.source_file = 'api_group_crawl' AND LOWER(v.group_name) = LOWER(d.name))
              OR 
              -- Priority 2: Fuzzy Match (DeepDarkCTI)
              (jaccard(LOWER(v.group_name), LOWER(d.name)) > 0.6)
          )
        -- Deduplicate if needed? For now, list all.
    """)
    print("✅ Logic Graph Built.")

def fetch_group_details(group_name):
    """
    Fetches live group details from RansomLook API on demand.
    Returns parsed metadata and victim list.
    """
    clean_name = group_name.lower().replace(" ", "") # Basic normalization
    url = f"https://www.ransomlook.io/api/group/{clean_name}"
    print(f"🔎 Fetching details for: {group_name} ({url})")

    try:
        with httpx.Client(follow_redirects=True, timeout=10) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            if not data or not isinstance(data, list):
                return None, []

            # Parse Index 0: Group Metadata
            group_meta = None
            try:
                group_meta = data[0]
            except IndexError:
                pass

            # Parse Index 1: Victim Array
            # Structure: [MetaDict, [Victim1, Victim2, ...]]
            victims = []
            if len(data) > 1 and isinstance(data[1], list):
                for item in data[1]:
                    if isinstance(item, dict) and "post_title" in item:
                        victims.append(item)
            
            return group_meta, victims

    except Exception as e:
        print(f"   ❌ Group Fetch Error: {e}")
        return None, []

def main():
    con = get_db_connection()
    try:
        init_db(con)
        ingest_deepdark(con)
        ingest_ghdb(con)
        ingest_ransomlook(con)
        ingest_ransomlook_groups(con)
        create_intel_view(con)
        
        # Verify
        count = con.execute("SELECT COUNT(*) FROM v_intel_graph").fetchone()[0]
        print(f"🎉 ETL Complete. {count} intelligence links generated.")
        
    finally:
        con.close()

if __name__ == "__main__":
    main()
