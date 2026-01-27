#!/usr/bin/env python3
"""
Startup script that runs migrations before starting the server.
"""
import os
import sys
import subprocess

def run_migrations():
    """Run Alembic migrations"""
    print("Running database migrations...")
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("✓ Migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Migration failed: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("⚠ Warning: alembic not found, skipping migrations", file=sys.stderr)
        return True  # Continue anyway in case alembic is in a different path

def start_server():
    """Start the FastAPI server"""
    port = os.environ.get("PORT", "8000")
    print(f"Starting FastAPI server on port {port}...")
    
    # Use uvicorn to start the server
    os.execvp("uvicorn", [
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", port
    ])

if __name__ == "__main__":
    if not run_migrations():
        print("Failed to run migrations, exiting", file=sys.stderr)
        sys.exit(1)
    
    start_server()
