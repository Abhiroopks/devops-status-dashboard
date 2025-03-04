from flask import Flask, redirect, request, jsonify, render_template, url_for
import psycopg2
import os
import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler


def get_config() -> dict:
    """
    Retrieve configuration for connecting to the PostgreSQL database.

    The configuration is sourced from environment variables, with the following defaults:
    - POSTGRES_HOST: localhost
    - POSTGRES_DB: flask_db
    - POSTGRES_USER: flask
    - POSTGRES_PASSWORD: (no default)

    Returns:
        dict: A dictionary containing the database configuration.
    """
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "dbname": os.getenv("POSTGRES_DB", "flask_db"),
        "user": os.getenv("POSTGRES_USER", "flask"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    }


def connect_to_postgres() -> psycopg2.extensions.connection:
    """Establishes a connection to a PostgreSQL database.

    Returns:
        connection: A psycopg2 connection object to the PostgreSQL database.
    """
    config = get_config()
    return psycopg2.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        dbname=config["dbname"],
    )


app = Flask(__name__)


conn = connect_to_postgres()
c = conn.cursor()
c.execute(
    query="""CREATE TABLE IF NOT EXISTS ping_results (
        url VARCHAR(255) PRIMARY KEY,
        response_time REAL,
        timestamp TIMESTAMP
        );"""
)
conn.commit()
conn.close()


def ping_url(url: str) -> None:
    """Ping a URL or IP Address and save the result to the database.

    Args:
        url (str): The URL or IP Address to ping.
    """
    try:
        response = requests.head(url, timeout=5)
        response_time = response.elapsed.total_seconds()
    except requests.exceptions.RequestException:
        response_time = None

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    database_connection = connect_to_postgres()
    cursor = database_connection.cursor()
    cursor.execute(
        "INSERT INTO ping_results (url) VALUES (%s) ON CONFLICT (url) DO NOTHING",
        (url,),
    )
    cursor.execute(
        "UPDATE ping_results SET response_time = %s, timestamp = %s WHERE url = %s",
        (response_time, timestamp, url),
    )
    database_connection.commit()
    database_connection.close()


@app.route("/")
def index():
    """
    Redirect from the index path to the view results page.

    Returns:
        redirect: A redirect response to the results page.
    """
    return redirect(url_for("view_results"))


def ping_all_urls():
    """Periodically ping all URLs in the database and save the results."""
    db_connection = connect_to_postgres()
    cursor = db_connection.cursor()
    cursor.execute("SELECT url FROM ping_results")
    urls = [row[0] for row in cursor.fetchall()]
    for url in urls:
        ping_url(url)
    db_connection.close()


@app.route("/submit", methods=["POST"])
def submit_url():
    """
    API endpoint to submit a URL or IP Address for a status check.

    Args:
        url (str): The URL or IP Address to submit.

    Returns:
        jsonify: A JSON response indicating whether the submission was successful.
    """
    url = request.json["url"]
    ping_url(url)
    return jsonify({"message": "URL submitted successfully"}), 201


@app.route("/results")
def view_results():
    """
    Route to view all ping results.

    Returns:
        render_template: A rendered template displaying all ping results.
    """
    conn = connect_to_postgres()
    c = conn.cursor()
    c.execute("SELECT * FROM ping_results")
    results = c.fetchall()
    conn.close()
    return render_template("results.html", results=results)


scheduler = BackgroundScheduler()
scheduler.add_job(ping_all_urls, "interval", minutes=5)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
    scheduler.shutdown()
