
from flask import Flask, render_template, jsonify
from nasa_api import get_latest_weather

app = Flask(__name__)

from flask import Flask, render_template, jsonify
from nasa_api import get_latest_weather
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "database.db"


def init_db():

    connection = sqlite3.connect("/tmp/mars_weather.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sol TEXT,
            observation_date TEXT,
            temperature TEXT,
            pressure TEXT,
            wind_speed TEXT,
            recorded_at TEXT,
            UNIQUE(sol, observation_date)
        )
    """)

    connection.commit()
    connection.close()


def save_weather(data):

    connection = sqlite3.connect("/tmp/mars_weather.db")

    connection.execute("""
        INSERT OR IGNORE INTO weather
        (sol, observation_date, temperature,
         pressure, wind_speed, recorded_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(data.get("sol") or ""),
        str(data.get("observation_date") or ""),
        str(data.get("temperature") or ""),
        str(data.get("pressure") or ""),
        str(data.get("wind_speed") or ""),
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_history():

    connection = sqlite3.connect("/tmp/mars_weather.db")

    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT * FROM weather
        ORDER BY id DESC
        LIMIT 30
    """).fetchall()

    connection.close()

    return [dict(row) for row in reversed(rows)]


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/api/weather")
def weather():

    try:

        data = get_latest_weather()

        if "error" in data:
            return jsonify(data), 404

        save_weather(data)

        return jsonify(data)

    except Exception as error:

        return jsonify({"error": str(error)}), 500


@app.route("/api/history")
def history():

    return jsonify(get_history())


init_db()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


