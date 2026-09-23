import urllib.request
import json

# URL API Monacolisa yang ada di tab browser Anda
API_URL = "http://monacolisa.fulindo.co.id/api/endpoint_anda_disini" # ganti dengan URL lengkapnya

try:
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            data = json.loads(response.read().decode())
            # Simpan data ke file data.json
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=4)
            print("Berhasil mengambil data dari Monacolisa!")
except Exception as e:
    print(f"Gagal mengambil data: {e}")
