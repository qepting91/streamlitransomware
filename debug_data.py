import duckdb
import tomli

try:
    with open('.streamlit/secrets.toml', 'rb') as f:
        msg = tomli.load(f)
        token = msg['MOTHERDUCK_TOKEN']
        
    con = duckdb.connect(f'md:?motherduck_token={token}')
    print("Finding 'play' or 'qilin' or 'Dragonforce'...")
    res = con.execute("SELECT name, category, source_file FROM darkweb_assets WHERE name ILIKE 'play' OR name ILIKE 'qilin' OR name ILIKE 'dragonforce'").fetchall()
    print(res)
except Exception as e:
    print(e)
