"""Configuration for the web service."""

import os

basedir: str = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Class to hold config values for the web service."""

    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
