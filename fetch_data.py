import json
import time
from datetime import datetime
import requests

# KONFIGURASI
API_URL = "https://api.example.com/v1/telemetry"  # Ganti dengan URL API target
DEVICE_ID = "860987054243453"
OUTPUT_FILE = "data.json"
TIMEOUT_SECONDS = 10

# Header request (tambahkan Token jika API butuh autentikasi)
HEADERS = {
    "User-Agent": "SmartE-Fetcher/1.0",
    "Content-Type": "application/json",
    # "Authorization": "Bearer TOKEN_KAMU_DI_SINI"
}


def get_default_dates():
    """Mengembalikan tanggal hari ini format YYYY-MM-DD"""
    today = datetime.now().strftime("%Y-%m-%d")
    return today, today


def fetch_and_save_data(start_date=None, end_date=None):
    """Mengambil data dari API backend dan menyimpannya ke data.json"""

    if not start_date or not end_date:
        start_date, end_date = get_default_dates()

    # Parameter query string yang dikirim ke API
    params = {
        "device_id": DEVICE_ID,
        "start_date": start_date,
        "end_date": end_date,
        "limit": 100,
    }

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Mengambil data dari API...")

    try:
        response = requests.get(
            API_URL, headers=HEADERS, params=params, timeout=TIMEOUT_SECONDS
        )

        # Cek status HTTP (200 OK)
        response.raise_for_status()

        data = response.json()

        # Normalisasi struktur data jika API mengembalikan wrap objek {'data': [...]}
        if isinstance(data, dict) and "data" in data:
            telemetry_list = data["data"]
        elif isinstance(data, list):
            telemetry_list = data
        else:
            telemetry_list = []

        # Simpan hasil fetch ke file data.json
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(telemetry_list, f, indent=4, ensure_ascii=False)

        print(
            f"✅ Berhasil! {len(telemetry_list)} record disimpan ke '{OUTPUT_FILE}'."
        )
        return True

    except requests.exceptions.Timeout:
        print("❌ Error: Request Timeout. Server tidak merespons.")
    except requests.exceptions.HTTPError as err:
        print(f"❌ Error HTTP {response.status_code}: {err}")
    except requests.exceptions.RequestException as err:
        print(f"❌ Error Koneksi: {err}")
    except json.JSONDecodeError:
        print("❌ Error: Respon dari server bukan format JSON yang valid.")
    except Exception as err:
        print(f"❌ Error Tidak Terduga: {err}")

    return False


def run_scheduler(interval_seconds=10):
    """Jalankan fetcher secara terus menerus tiap N detik"""
    print(
        f"Memulai Service Fetcher untuk Device [{DEVICE_ID}] (Interval: {interval_seconds}s)..."
    )
    print("Tekan Ctrl+C untuk menghentikan.\n")

    try:
        while True:
            fetch_and_save_data()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nService Fetcher dihentikan.")


if __name__ == "__main__":
    # Jalankan sekali langsung fetch data hari ini:
    fetch_and_save_data()

    # Jika ingin jalankan otomatis terus-menerus tiap 10 detik,
    # hapus tanda baris di bawah ini:
    # run_scheduler(interval_seconds=10)
