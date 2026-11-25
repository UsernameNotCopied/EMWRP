import logging
import signal
import time
from typing import Optional

import adafruit_bmp3xx
import adafruit_dht
import board
from gpiozero import CPUTemperature

from emwrp.config import DatabaseConfig, LOG_INTERVAL_SECONDS
from emwrp.database import DatabaseHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

HUMIDITY_OUTLIER_THRESHOLD = 15.0
MAX_CONSECUTIVE_OUTLIERS = 3
DHT_MAX_RETRIES = 5


def read_dht_humidity(sensor: adafruit_dht.DHT22) -> Optional[float]:
    for attempt in range(1, DHT_MAX_RETRIES + 1):
        try:
            humidity = sensor.humidity
            if humidity is not None:
                return float(humidity)
        except RuntimeError as exc:
            logger.debug("DHT22 read attempt %d failed: %s", attempt, exc)
        time.sleep(2.0)
    return None


def main() -> None:
    running = True

    def handle_signal(signum, _frame):
        nonlocal running
        logger.info("Received signal %s, shutting down...", signum)
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    db = DatabaseHandler(DatabaseConfig())
    dht = adafruit_dht.DHT22(board.D4)
    bmp = adafruit_bmp3xx.BMP3XX_I2C(board.I2C())
    cpu = CPUTemperature()

    consecutive_outliers = 0

    try:
        while running:
            humidity = read_dht_humidity(dht)
            temperature = bmp.temperature
            pressure = bmp.pressure
            cpu_temp = cpu.temperature

            if None in (humidity, temperature, pressure, cpu_temp):
                logger.warning("Incomplete sensor reading; skipping insert.")
            else:
                try:
                    latest = db.get_latest_measurement()
                    if latest is not None and latest["hum"] is not None:
                        prev_hum = float(latest["hum"])
                        if abs(humidity - prev_hum) > HUMIDITY_OUTLIER_THRESHOLD:
                            consecutive_outliers += 1
                            if consecutive_outliers < MAX_CONSECUTIVE_OUTLIERS:
                                logger.warning(
                                    "Humidity outlier detected (%.1f%% vs %.1f%%); keeping previous.",
                                    humidity,
                                    prev_hum,
                                )
                                humidity = prev_hum
                            else:
                                logger.info(
                                    "Accepting sustained humidity shift to %.1f%%.",
                                    humidity,
                                )
                                consecutive_outliers = 0
                        else:
                            consecutive_outliers = 0

                    db.insert_measurement(temperature, humidity, pressure, cpu_temp)
                    logger.info(
                        "Logged T=%.1fC H=%.1f%% P=%.1fhPa CPU=%.1fC",
                        temperature,
                        humidity,
                        pressure,
                        cpu_temp,
                    )
                except Exception:
                    logger.exception("Database error while logging measurement.")

            # Sleep in 1s increments so shutdown signals respond immediately
            for _ in range(LOG_INTERVAL_SECONDS):
                if not running:
                    break
                time.sleep(1)
    finally:
        dht.exit()
        db.close()
        logger.info("Logger stopped cleanly.")


if __name__ == "__main__":
    main()
