#!/usr/bin/env python3
"""
Smart Campus Placement Analyser & Predictor
Main Application Launcher
Group: SY-K-17 | Vishwakarma Institute of Technology, Pune
"""
import sys
import os
import socket

# Ensure working directory is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import config
from database.db import init_db, detect_backend, get_db_info
from database.seed_data import seed

def find_available_port(start_port=5001, max_port=5020):
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return start_port

def main():
    print("=" * 72)
    print("  SMART CAMPUS PLACEMENT ANALYSER & PREDICTOR")
    print("  Vishwakarma Institute of Technology, Pune | Computer Engineering")
    print("  Group: SY-K-17 | Guide: Prof. Sachin Jadhav")
    print("  Team: Siddhesh Bhosale, Meghraj Sirsat, Soham Ombale, Arpit Tale")
    print("=" * 72)

    # 1. Detect & Initialize 3NF Database
    backend = detect_backend()
    info = get_db_info()
    print(f"\n[1/4] Database Backend: {info['backend']}")
    if backend == 'mysql':
        print(f"      Connected to MySQL at {info['host']}, database: '{info['database']}'")
    else:
        print(f"      Running Embedded 3NF Relational DB at: {info['path']}")
        print("      (To use MySQL, set DB_TYPE=mysql and configure credentials in .env)")

    init_db()

    # 2. Seed Initial Records
    print("\n[2/4] Verifying Seed Records (Users, Students, Drives, Dynamic Criteria)...")
    seed()

    # 3. Verify ML Model & SHAP Explainer
    print("\n[3/4] Verifying AI/ML Models & SHAP Explainer...")
    if not os.path.exists(config.MODEL_PATH):
        print("      Model bundle not found. Training RandomForestClassifier and TreeSHAP...")
        from ml.train_model import train_and_export
        train_and_export()
    else:
        print(f"      Loaded pre-trained model bundle from {config.MODEL_PATH}")

    # 4. Launch Web Portal
    port = find_available_port(5001)
    print(f"\n[4/4] Starting Web Portal on http://127.0.0.1:{port}")
    print("=" * 72)
    print(f"  Access the Dashboard at: http://127.0.0.1:{port}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 72 + "\n")

    from app import app
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()
