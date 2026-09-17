"""
Vercel Serverless Entry Point
Wraps the Flask search application for Vercel's Python runtime.
"""
import sys
import os

# Resolve project root (one level up from api/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add project root to Python path so search_app can be imported
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set environment variable so app.py knows it's running on Vercel
os.environ["VERCEL"] = "1"

# Import the Flask app
from search_app.app import app

# Vercel looks for an `app` variable (WSGI-compatible) in this module.
# The import above already exposes it.
