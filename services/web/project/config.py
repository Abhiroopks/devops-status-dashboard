"""Configuration for the web service."""

import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Class to hold config values for the web service."""

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
