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


class VercelPathFixMiddleware:
    """
    Normalizes PATH_INFO when Vercel rewrites requests to /api/index.py.
    Ensures that Flask routes matched to '/', '/view/...', '/api/search',
    and '/static/...' resolve correctly regardless of proxy prefixes.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")

        # Use matched path from Vercel header if available and valid
        matched = environ.get("HTTP_X_MATCHED_PATH")
        if matched and not matched.startswith("/api/index"):
            environ["PATH_INFO"] = matched
            path = matched

        for prefix in ("/api/index.py", "/api/index", "/api"):
            if path == prefix or path == f"{prefix}/":
                environ["PATH_INFO"] = "/"
                break
            elif path.startswith(f"{prefix}/"):
                subpath = path[len(prefix):]
                environ["PATH_INFO"] = subpath
                break

        return self.wsgi_app(environ, start_response)


# Apply WSGI middleware
app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)

