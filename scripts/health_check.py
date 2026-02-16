#!/usr/bin/env python3
"""
Health check script for PharmaRec AI.
Verifies all components are working correctly.
Run after installation to ensure everything is set up properly.
"""
import sys
import subprocess
import importlib.util


def check_python_packages():
    """Check if all required Python packages are installed."""
    print("\n Checking Python packages...")
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "jose",
        "passlib",
        "pandas",
        "scikit-learn",
        "watchdog",
        "requests",
        "pytest"
    ]

    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"   {package}")
        except ImportError:
            print(f"   {package} (missing)")
            missing.append(package)

    return missing


def check_node_packages():
    """Check if Node.js and npm are installed."""
    print("\n Checking Node.js packages...")
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        npm_version = result.stdout.strip()
        print(f"   npm {npm_version}")
        return True
    except FileNotFoundError:
        print(f"   npm not found")
        return False


def check_directories():
    """Check if all required directories exist."""
    print("\n📁 Checking directory structure...")
    required_dirs = [
        "backend",
        "backend/app",
        "backend/app/api",
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/services",
        "frontend",
        "frontend/src",
        "ml-engine",
        "tests",
        "scripts"
    ]

    import os
    missing = []
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"   {dir_path}/")
        else:
            print(f"   {dir_path}/ (missing)")
            missing.append(dir_path)

    return missing


def check_files():
    """Check if all required files exist."""
    print("\n Checking critical files...")
    required_files = [
        "requirements.txt",
        ".env.example",
        "README.md",
        "Makefile",
        "docker-compose.yml",
        "backend/app/main.py",
        "backend/app/database.py",
        "backend/app/config.py",
        "frontend/package.json",
        "frontend/tsconfig.json",
        "ml-engine/inference/predict.py",
        "desktop-agent/agent_v2.py"
    ]

    import os
    missing = []
    for file_path in required_files:
        if os.path.isfile(file_path):
            print(f"   {file_path}")
        else:
            print(f"   {file_path} (missing)")
            missing.append(file_path)

    return missing


def main():
    """Run all health checks."""
    print(" PharmaRec AI - Health Check")
    print("=" * 50)

    # Check Python
    print("\n Python Information")
    print(f"  Version: {sys.version}")
    print(f"  Executable: {sys.executable}")

    # Check packages
    missing_packages = check_python_packages()

    # Check Node.js
    has_nodejs = check_node_packages()

    # Check directories
    missing_dirs = check_directories()

    # Check files
    missing_files = check_files()

    # Summary
    print("\n" + "=" * 50)
    print(" Summary")
    print("=" * 50)

    issues = len(missing_packages) + len(missing_dirs) + len(missing_files)
    if not has_nodejs:
        issues += 1

    if issues == 0:
        print(" All checks passed! Your environment is ready.")
        print("\n Next steps:")
        print("  1. Run: make setup")
        print("  2. Run: make dev")
        print("  3. Open: http://localhost:3000")
        return 0
    else:
        print(f" Found {issues} issue(s):")
        if missing_packages:
            print(f"\n  Missing Python packages ({len(missing_packages)}):")
            for pkg in missing_packages:
                print(f"    - {pkg}")
            print(f"  Fix: pip install -r requirements.txt")

        if missing_dirs:
            print(f"\n  Missing directories ({len(missing_dirs)}):")
            for dir_path in missing_dirs:
                print(f"    - {dir_path}/")

        if missing_files:
            print(f"\n  Missing files ({len(missing_files)}):")
            for file_path in missing_files:
                print(f"    - {file_path}")

        if not has_nodejs:
            print("\n  Node.js not found!")
            print("  Fix: Install Node.js from https://nodejs.org/")

        return 1


if __name__ == "__main__":
    sys.exit(main())
