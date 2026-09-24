import json
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# ==========================================
# KONFIGURASI MQTT (Sesuaikan dengan Broker Mas Fikri / PDF)
# ==========================================
MQTT_BROKER = "broker.hivemq.com"  # Ganti IP/Host broker (contoh: 103.xxx.xxx.xxx)
MQTT_PORT = 1883
MQTT_TOPIC = "smarte/tps_lidah_wetan/telemetry"  # Topic MQTT sensor
MQTT_USER = ""  # Isi jika broker butuh username
MQTT_PASS = ""  # Isi jika broker butuh password

OUTPUT_FILE = "data.json"
MAX_RECORDS = 100  # Maksimal simpan N data terakhir agar file tetap ringan


def load_existing_data():
    """Membaca data lama dari file JSON jika ada"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def save_data(data_list):
    """Menyimpan list data ke data.json"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=2, ensure_ascii=False)


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback saat berhasil konek ke MQTT Broker"""
    if rc == 0:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Terhubung ke MQTT Broker ({MQTT_BROKER})"
        )
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Mendengarkan real-time data di topic: '{MQTT_TOPIC}'...")
    else:
        print(f"❌ Gagal konek ke broker. Code: {rc}")


def on_message(client, userdata, msg):
    """Callback saat ada payload telemetri baru masuk dari sensor"""
    try:
        payload_str = msg.payload.decode("utf-8")
        payload_json = json.loads(payload_str)

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Data Real-Time Masuk!"
        )

        # Ambil data lama, sisipkan data terbaru ke urutan paling atas (index 0)
        existing_data = load_existing_data()
        existing_data.insert(0, payload_json)

        # Batasi jumlah array
        existing_data = existing_data[:MAX_RECORDS]

        # Simpan pembaruan ke data.json
        save_data(existing_data)
        print(f"💾 Data tersimpan di '{OUTPUT_FILE}'.")

    except json.JSONDecodeError:
        print("⚠️ Payload yang masuk bukan format JSON yang valid.")
    except Exception as e:
        print(f"❌ Error pemrosesan data: {e}")


def main():
    # Inisialisasi MQTT Client
    client_id = f"SmartE_Fetcher_{int(time.time())}"
    client = mqtt.Client(client_id=client_id)

    if MQTT_USER and MQTT_PASS:
        client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.on_connect = on_connect
    client.on_message = on_message

    print("🚀 Memulai Real-Time Fetcher...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        # loop_forever membuat script terus berjalan & memproses data secara real-time
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Service real-time dihentikan.")
    except Exception as e:
        print(f"❌ Koneksi terputus/error: {e}")


if __name__ == "__main__":
    main()
