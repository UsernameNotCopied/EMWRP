from flask import Flask, jsonify

from emwrp.config import DatabaseConfig
from emwrp.dashboard import create_dash_application
from emwrp.database import DatabaseHandler

app = Flask(__name__)
db = DatabaseHandler(DatabaseConfig())

create_dash_application(app)


@app.route("/lastMeasurement")
def last_measurement():
    latest = db.get_latest_measurement()
    if latest is None:
        return jsonify({"error": "No measurements available"}), 404

    package = [
        {"Item": "Temperature", "Value": latest["temp"]},
        {"Item": "Humidity", "Value": latest["hum"]},
        {"Item": "Pressure", "Value": latest["pressure"]},
        {"Item": "cpuTemperature", "Value": latest["cputemp"]},
    ]
    return jsonify({"Package": package}), 200


server = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=False)
