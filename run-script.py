#!/usr/bin/env python3
"""
Runner script for the AI Translator application.
This script ensures all dependencies are properly set up before launching the app.
"""

import os
import sys
import importlib.util
import subprocess
import time


def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "PySide6",
        "cryptography",
        "requests",
        "qdarktheme"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:", ", ".join(missing_packages))
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", *missing_packages
            ])
            print("Successfully installed required packages.")
        except subprocess.CalledProcessError:
            print("Failed to install packages. Please install them manually:")
            print("pip install -r requirements.txt")
            return False
    
    return True


def create_folders():
    """Create necessary folders if they don't exist."""
    folders = [
        "api",
        "config",
        "resources/icons",
        "resources/styles",
        "ui",
        "utils"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Create empty __init__.py files in each package folder
    for folder in ["api", "config", "ui", "utils"]:
        init_file = os.path.join(folder, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Package initialization\n")
    
    return True


def run_application():
    """Run the main application."""
    print("Starting AI Translator...")
    
    # Add the current directory to sys.path
    sys.path.insert(0, os.path.abspath("."))
    
    try:
        from main import main
        main()
    except ImportError as e:
        print(f"Error importing main module: {e}")
        return False
    except Exception as e:
        print(f"Error running application: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("AI Translator Setup")
    print("===================")
    
    # Check and install dependencies
    if not check_dependencies():
        print("Failed to set up dependencies. Exiting.")
        sys.exit(1)
    
    # Create necessary folders
    if not create_folders():
        print("Failed to create necessary folders. Exiting.")
        sys.exit(1)
    
    # Run the application
    if not run_application():
        print("Failed to run the application. Exiting.")
        sys.exit(1)
