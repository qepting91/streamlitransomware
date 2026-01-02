
import httpx
import json

url = "https://www.exploit-db.com/google-hacking-database"
headers = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

try:
    with httpx.Client(headers=headers, timeout=30.0) as client:
        print(f"Fetching {url}...")
        resp = client.get(url)
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            # print keys of first item
            items = data.get('data', [])
            if items:
                print("First item keys:", items[0].keys())
                print("First item sample:", json.dumps(items[0], indent=2))
            else:
                print("No items found in 'data'.")
        except Exception as e:
            print(f"JSON Error: {e}")
            print("Response text prefix:", resp.text[:500])
except Exception as e:
    print(f"Request Error: {e}")
