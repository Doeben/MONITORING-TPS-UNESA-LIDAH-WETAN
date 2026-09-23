import os
import urllib.request
import json
from datetime import datetime

# Membaca URL lengkap + API Key Rahasia dari GitHub Secrets
BASE_URL = os.environ.get('MONACOLISA_API_URL')

if not BASE_URL:
    print("Error: MONACOLISA_API_URL Secret tidak ditemukan!")
    exit(1)

# Mengambil tanggal hari ini secara otomatis (format: YYYY-MM-DD)
today_date = datetime.now().strftime('%Y-%m-%d')
full_url = f"{BASE_URL}&tanggal={today_date}"

print(f"Mengambil data telemetri dari Monacolisa untuk tanggal: {today_date}...")

try:
    req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            raw_response = response.read().decode('utf-8')
            data = json.loads(raw_response)
            
            # Simpan hasil data yang sudah diambil ke file data.json lokal
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)
                
            print("Berhasil! Data telah diunduh dan diamankan ke data.json")
except Exception as e:
    print(f"Gagal mengambil data dari server Monacolisa: {e}")
