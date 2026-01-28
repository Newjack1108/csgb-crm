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
    
    # Check if DATABASE_URL is set (for debugging)
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Mask password in output
        masked_url = database_url.split("@")[-1] if "@" in database_url else "***"
        print(f"Database URL: ***@{masked_url}")
        
        # Check if it's still pointing to localhost (Railway issue)
        if "localhost" in database_url or "127.0.0.1" in database_url:
            print("⚠ ERROR: DATABASE_URL points to localhost!", file=sys.stderr)
            print("⚠ This means Railway hasn't linked the PostgreSQL service.", file=sys.stderr)
            print("⚠ Please check Railway dashboard:", file=sys.stderr)
            print("   1. Go to your web service → Variables", file=sys.stderr)
            print("   2. Ensure DATABASE_URL references the PostgreSQL service", file=sys.stderr)
            print("   3. Or add PostgreSQL service reference in service settings", file=sys.stderr)
            return False  # Fail fast if database URL is wrong
    else:
        print("⚠ ERROR: DATABASE_URL not found in environment", file=sys.stderr)
        print("⚠ Please add DATABASE_URL variable in Railway dashboard", file=sys.stderr)
        return False
    
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
    # Try python3 first, fall back to python
    import shutil
    python_cmd = shutil.which("python3") or shutil.which("python") or "python"
    uvicorn_cmd = shutil.which("uvicorn") or f"{python_cmd} -m uvicorn"
    
    if uvicorn_cmd.startswith(python_cmd):
        # Use python -m uvicorn
        os.execvp(python_cmd, [
            python_cmd, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", port
        ])
    else:
        # Use uvicorn directly
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
