from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import time
import threading
from datetime import datetime

app = Flask(__name__)
CORS(app)

energy_data = []
MAX_RECORDS = 100


def generate_reading():
    voltage = round(random.uniform(218, 242), 2)
    current = round(random.uniform(0.5, 14.5), 2)
    power = round(voltage * current, 2)
    energy = round(power / 1000, 4)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "voltage": voltage,
        "current": current,
        "power": power,
        "energy_kwh": energy,
        "status": "normal" if power < 2500 else "high"
    }


def background_simulator():
    while True:
        try:
            reading = generate_reading()
            energy_data.append(reading)
            if len(energy_data) > MAX_RECORDS:
                energy_data.pop(0)
        except Exception as e:
            print("Error in simulator:", e)
        time.sleep(5)


threading.Thread(target=background_simulator, daemon=True).start()

# Pre-fill data
for _ in range(20):
    energy_data.append(generate_reading())


# ── ROUTES ─────────────────────────────

@app.route("/")
def home():
    return jsonify({"message": "Smart Energy API running"})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "smart-energy-backend"})


@app.route("/api/readings")
def get_readings():
    try:
        limit = int(request.args.get("limit", 20))
    except:
        limit = 20

    limit = min(limit, MAX_RECORDS)

    return jsonify({
        "count": limit,
        "readings": energy_data[-limit:]
    })


@app.route("/api/latest")
def get_latest():
    if not energy_data:
        return jsonify({"error": "No data"}), 404
    return jsonify(energy_data[-1])


@app.route("/api/summary")
def get_summary():
    if not energy_data:
        return jsonify({"error": "No data"}), 404

    voltages = [r["voltage"] for r in energy_data]
    currents = [r["current"] for r in energy_data]
    powers = [r["power"] for r in energy_data]

    return jsonify({
        "total_readings": len(energy_data),
        "voltage": {
            "avg": round(sum(voltages) / len(voltages), 2),
            "min": min(voltages),
            "max": max(voltages)
        },
        "current": {
            "avg": round(sum(currents) / len(currents), 2),
            "min": min(currents),
            "max": max(currents)
        },
        "power": {
            "avg": round(sum(powers) / len(powers), 2),
            "min": min(powers),
            "max": max(powers)
        },
        "total_energy_kwh": round(sum(r["energy_kwh"] for r in energy_data), 4)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)