import os
import json
import urllib.request
import ssl
import re
from datetime import datetime

# Membaca URL rahasia dari GitHub Secrets
API_URL = os.environ.get('MONACOLISA_API_URL')

if not API_URL:
    print("❌ ERROR: Secret 'MONACOLISA_API_URL' tidak ditemukan!")
    exit(1)

today = datetime.now().strftime('%Y-%m-%d')

if "tanggal=" in API_URL:
    full_url = re.sub(r'tanggal=[\d-]+', f'tanggal={today}', API_URL)
else:
    full_url = f"{API_URL}&tanggal={today}"

print(f"🔄 Mengambil data telemetri Monacolisa untuk tanggal {today}...")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

try:
    req = urllib.request.Request(
        full_url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
        if response.status == 200:
            raw_data = response.read().decode('utf-8')
            new_json = json.loads(raw_data)
            new_list = new_json.get('data', [])

            # Membaca data lama jika sudah ada (agar riwayat hari sebelumnya disimpan)
            existing_data = []
            if os.path.exists('data.json'):
                try:
                    with open('data.json', 'r', encoding='utf-8') as f:
                        old_json = json.load(f)
                        existing_data = old_json.get('data', [])
                except Exception:
                    existing_data = []

            # Penggabungan data & eliminasi duplikat berdasarkan timestamp
            combined_map = {item['timestamp']: item for item in existing_data}
            for item in new_list:
                combined_map[item['timestamp']] = item

            # Urutkan data dari yang paling baru
            sorted_data = sorted(combined_map.values(), key=lambda x: x['timestamp'], reverse=True)

            final_output = {
                "status": "success",
                "total": len(sorted_data),
                "data": sorted_data
            }

            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=4)
                
            print(f"✅ BERHASIL! Total {len(sorted_data)} data telemetri tersimpan di data.json")
        else:
            print(f"❌ HTTP Error: {response.status}")
            exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    exit(1)
