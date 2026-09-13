import uvicorn
import os
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    print("[Developer Intelligence] Starting Backend on http://localhost:8000 (0.0.0.0:8000) ...")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=False)


