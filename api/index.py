"""Vercel serverless entrypoint for Astramech Flask app."""

import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "company-efficiency-optimizer")

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app import create_app


app = create_app("production")
