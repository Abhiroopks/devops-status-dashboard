"""
Web service to ping URLs and save the results to a database.

"""

import time

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from project.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class PingResult(db.Model):
    """
    Model representing a ping result.

    Attributes:
        __tablename__ (str): The name of the database table.
        url (db.Column): The URL or IP Address that was pinged.
        response_time (db.Column): The response time for the ping.
        timestamp (db.Column): The timestamp of when the ping was made.
    """

    __tablename__ = "ping_results"

    url = db.Column(db.String(255), primary_key=True)
    response_time = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)

    def __init__(self, url, response_time, timestamp):
        """
        Initialize a PingResult object.

        Args:
            url (str): The URL or IP Address that was pinged.
            response_time (float): The response time for the ping.
            timestamp (datetime): The timestamp of when the ping was made.
        """
        self.url = url
        self.response_time = response_time
        self.timestamp = timestamp


def ping_url(url: str) -> None:
    """
    Ping a URL or IP Address and save the result to the database.

    Args:
        url (str): The URL or IP Address to ping.
    """
    try:
        start_time = time.time()
        requests.head(url, timeout=5)
        response_time = time.time() - start_time
    except requests.exceptions.RequestException:
        response_time = None

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    db.session.merge(PingResult(url, response_time, timestamp))
    db.session.commit()


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
    urls = [result.url for result in PingResult.query.all()]
    for url in urls:
        ping_url(url)


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
    results = PingResult.query.all()
    return render_template("results.html", results=results)


scheduler = BackgroundScheduler()
scheduler.add_job(ping_all_urls, "interval", minutes=5)
scheduler.start()
