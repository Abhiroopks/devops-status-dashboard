from flask import Flask, redirect, request, jsonify, render_template, url_for
import sqlite3
import os
import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Create a SQLite database if it doesn't exist
if not os.path.exists("db.sqlite3"):
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE ping_results
                 (url TEXT PRIMARY KEY, response_time REAL, timestamp TEXT)"""
    )
    conn.commit()
    conn.close()


def ping_url(url: str) -> None:
    """
    Ping a URL or IP Address and save the result to the database.

    Args:
        url (str): The URL or IP Address to ping.
    """
    start_time = time.time()
    try:
        response = requests.head(url, timeout=5)
        response_time = response.elapsed.total_seconds()
    except requests.exceptions.RequestException:
        response_time = None

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO ping_results (url) VALUES (?)", (url,))
    cursor.execute(
        "UPDATE ping_results SET response_time = ?, timestamp = ? WHERE url = ?",
        (response_time, timestamp, url),
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    """
    Redirect from the index path to the view results page.

    Returns:
        redirect: A redirect response to the results page.
    """
    return redirect(url_for("view_results"))


def ping_urls_periodically():
    """
    Periodically ping all URLs in the database and save the results.

    Returns:
        None
    """
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("SELECT url FROM ping_results")
    urls = [row[0] for row in c.fetchall()]
    for url in urls:
        ping_url(url)
    conn.close()


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
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute("SELECT * FROM ping_results")
    results = c.fetchall()
    conn.close()
    return render_template("results.html", results=results)


scheduler = BackgroundScheduler()
scheduler.add_job(ping_urls_periodically, "interval", minutes=5)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True)
    scheduler.shutdown()
