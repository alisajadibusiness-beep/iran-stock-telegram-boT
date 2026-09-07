import sqlite3
from datetime import datetime

from config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            quantity REAL NOT NULL,
            buy_price REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            target_price REAL,
            enabled INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            signal TEXT NOT NULL,
            score REAL NOT NULL,
            price REAL NOT NULL,
            stop_loss REAL,
            target1 REAL,
            target2 REAL,
            target3 REAL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def register_user(
    telegram_id,
    username=None,
    first_name=None
):

    connection = get_connection()

    connection.execute("""
        INSERT OR IGNORE INTO users (
            telegram_id,
            username,
            first_name,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        telegram_id,
        username,
        first_name,
        datetime.utcnow().isoformat()
    ))

    connection.commit()
    connection.close()


def add_position(
    telegram_id,
    symbol,
    quantity,
    buy_price
):

    connection = get_connection()

    connection.execute("""
        INSERT INTO portfolio (
            telegram_id,
            symbol,
            quantity,
            buy_price,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        telegram_id,
        symbol.upper(),
        quantity,
        buy_price,
        datetime.utcnow().isoformat()
    ))

    connection.commit()
    connection.close()


def get_portfolio(telegram_id):

    connection = get_connection()

    rows = connection.execute("""
        SELECT *
        FROM portfolio
        WHERE telegram_id = ?
        ORDER BY created_at DESC
    """, (
        telegram_id,
    )).fetchall()

    connection.close()

    return rows


def save_signal(
    symbol,
    signal,
    score,
    price,
    stop_loss,
    target1,
    target2,
    target3
):

    connection = get_connection()

    connection.execute("""
        INSERT INTO signals (
            symbol,
            signal,
            score,
            price,
            stop_loss,
            target1,
            target2,
            target3,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol,
        signal,
        score,
        price,
        stop_loss,
        target1,
        target2,
        target3,
        datetime.utcnow().isoformat()
    ))

    connection.commit()
    connection.close()
