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
    
    # Try to find alembic in common locations
    alembic_paths = [
        "alembic",  # In PATH
        "/opt/venv/bin/alembic",  # Railway virtual environment
        "python", "-m", "alembic",  # As Python module
    ]
    
    # Try as direct command first
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        print("✓ Migrations completed successfully")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try as Python module
        try:
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            print("✓ Migrations completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Migration failed: {e.stderr}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"⚠ Warning: Could not run migrations: {e}", file=sys.stderr)
            print("⚠ Continuing without migrations (database may need manual setup)", file=sys.stderr)
            return True  # Continue anyway to allow manual migration

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
