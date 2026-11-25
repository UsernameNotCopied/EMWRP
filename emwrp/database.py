from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Optional

from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from emwrp.config import DatabaseConfig


class DatabaseHandler:
    def __init__(self, config: DatabaseConfig, minconn: int = 1, maxconn: int = 5):
        self._pool = ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dbname=config.dbname,
            user=config.user,
            password=config.password,
            host=config.host,
            port=config.port,
        )

    @contextmanager
    def _cursor(self, commit: bool = False):
        conn = self._pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def get_last_n_measurements(self, rows: int = 1) -> list[dict[str, Any]]:
        query = """
            SELECT id, temp, hum, datetime, pressure, cputemp
            FROM sensor_data
            ORDER BY id DESC
            LIMIT %s;
        """
        with self._cursor() as cur:
            cur.execute(query, (rows,))
            return [dict(row) for row in cur.fetchall()]

    def get_latest_measurement(self) -> Optional[dict[str, Any]]:
        rows = self.get_last_n_measurements(1)
        return rows[0] if rows else None

    def get_measurements_for_date_range(
        self, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)

        query = """
            SELECT id, temp, hum, datetime, pressure, cputemp
            FROM sensor_data
            WHERE datetime >= %s AND datetime < %s
            ORDER BY id ASC;
        """
        with self._cursor() as cur:
            cur.execute(query, (start_dt, end_dt))
            return [dict(row) for row in cur.fetchall()]

    def get_first_measurement(self) -> Optional[dict[str, Any]]:
        query = """
            SELECT id, temp, hum, datetime, pressure, cputemp
            FROM sensor_data
            ORDER BY id ASC
            LIMIT 1;
        """
        with self._cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            return dict(row) if row else None

    def insert_measurement(
        self, temp: float, hum: float, pressure: float, cpu_temp: float
    ) -> None:
        query = """
            INSERT INTO sensor_data (temp, hum, pressure, cputemp)
            VALUES (%s, %s, %s, %s);
        """
        with self._cursor(commit=True) as cur:
            cur.execute(
                query,
                (
                    round(float(temp), 1),
                    round(float(hum), 1),
                    round(float(pressure), 1),
                    round(float(cpu_temp), 1),
                ),
            )

    def close(self) -> None:
        self._pool.closeall()


_db_instance: Optional[DatabaseHandler] = None


def get_db() -> DatabaseHandler:
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseHandler(DatabaseConfig())
    return _db_instance
