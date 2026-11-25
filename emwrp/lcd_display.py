import logging
import signal
import time

import adafruit_character_lcd.character_lcd as characterlcd
import board
import digitalio

from emwrp.config import DatabaseConfig, LOG_INTERVAL_SECONDS
from emwrp.database import DatabaseHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

LCD_COLUMNS = 16
LCD_ROWS = 2
DEGREE_SYMBOL = chr(223)


def init_lcd() -> characterlcd.Character_LCD_Mono:
    return characterlcd.Character_LCD_Mono(
        rs=digitalio.DigitalInOut(board.D22),
        en=digitalio.DigitalInOut(board.D17),
        d4=digitalio.DigitalInOut(board.D25),
        d5=digitalio.DigitalInOut(board.D24),
        d6=digitalio.DigitalInOut(board.D23),
        d7=digitalio.DigitalInOut(board.D18),
        columns=LCD_COLUMNS,
        lines=LCD_ROWS,
    )


def format_lcd_message(row: dict) -> str:
    line1 = f"{row['temp']:.1f}{DEGREE_SYMBOL}C  {row['hum']:.1f}%"
    line2 = f"{row['pressure']:.0f}hPa {row['cputemp']:.1f}{DEGREE_SYMBOL}C"
    return f"{line1[:LCD_COLUMNS]}\n{line2[:LCD_COLUMNS]}"


def main() -> None:
    running = True

    def handle_signal(signum, _frame):
        nonlocal running
        logger.info("Received signal %s, shutting down LCD...", signum)
        running = False

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    db = DatabaseHandler(DatabaseConfig())
    lcd = init_lcd()
    lcd.clear()

    try:
        while running:
            try:
                latest = db.get_latest_measurement()
                lcd.clear()
                if latest is None:
                    lcd.message = "Waiting for\nsensor data..."
                else:
                    lcd.message = format_lcd_message(latest)
            except Exception:
                logger.exception("Failed to refresh LCD.")
                lcd.clear()
                lcd.message = "DB Error\nRetrying..."

            for _ in range(LOG_INTERVAL_SECONDS):
                if not running:
                    break
                time.sleep(1)
    finally:
        lcd.clear()
        db.close()
        logger.info("LCD display stopped cleanly.")


if __name__ == "__main__":
    main()
