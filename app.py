from flask import Flask, redirect, request, jsonify, render_template, url_for
import sqlite3
import os
import schedule
import time
import requests

app = Flask(__name__)

# Create a SQLite database if it doesn't exist
if not os.path.exists("db.sqlite3"):
    conn = sqlite3.connect("db.sqlite3")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE ping_results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, response_time REAL, timestamp TEXT)"""
    )
    conn.commit()
    conn.close()


def ping_url(url):
    """
    Ping a URL or IP Address and save the result to the database.

    Args:
        url (str): The URL or IP Address to ping.

    Returns:
        None
    """
    try:
        response = requests.head(url, timeout=5)
        response_time = response.elapsed.total_seconds()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute(
            "INSERT INTO ping_results (url, response_time, timestamp) VALUES (?, ?, ?)",
            (url, response_time, timestamp),
        )
        conn.commit()
        conn.close()
    except requests.exceptions.RequestException as e:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("db.sqlite3")
        c = conn.cursor()
        c.execute(
            "INSERT INTO ping_results (url, response_time, timestamp) VALUES (?, ?, ?)",
            (url, None, timestamp),
        )
        conn.commit()
        conn.close()
        print(f"Error pinging {url}: {e}")


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


@app.route("/")
def index():
    """
    Redirect to the results page.

    Returns:
        redirect: A redirect to the results page.
    """
    return redirect(url_for("view_results"))


# Schedule the ping_urls_periodically function to run every 5 minutes
schedule.every(5).minutes.do(ping_urls_periodically)

if __name__ == "__main__":
    app.run(debug=True)
    while True:
        schedule.run_pending()
        time.sleep(1)
