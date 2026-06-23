"""Vercel serverless entrypoint for the core Flask app."""

import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
PROJECT_DIR = os.path.join(REPO_ROOT, "company-efficiency-optimizer")

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from app import create_app


app = create_app("production")
