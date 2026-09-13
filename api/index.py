import os
import sys

# Keep this file as a compatibility import. Vercel FastAPI uses root index.py.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.main import app

__all__ = ["app"]
