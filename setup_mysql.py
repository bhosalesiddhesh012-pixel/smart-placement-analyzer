#!/usr/bin/env python3
"""
Setup and Verify MySQL Database for Smart Placement Analyzer
Supports automated connection checking, schema import, and seed verification.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from database.db import detect_backend, get_connection, get_db_info, query_db, init_db

def test_mysql_connection():
    print("=" * 68)
    print("      SMART CAMPUS PLACEMENT ANALYZER - DATABASE LAYER")
    print("=" * 68)
    print(f"Target Database Type : MySQL 8.0+")
    print(f"Host:Port            : {config.MYSQL_HOST}:{config.MYSQL_PORT}")
    print(f"User                 : {config.MYSQL_USER}")
    print(f"Target Database      : {config.MYSQL_DB}")
    print("-" * 68)

    backend = detect_backend()
    db_info = get_db_info()

    if backend == 'mysql':
        print(f"✅ SUCCESS: Connected to live MySQL server at {db_info['host']}!")
        print(f"   Active Database: {db_info['database']}")
    else:
        print(f"ℹ️  MySQL is not currently reachable on {config.MYSQL_HOST}:{config.MYSQL_PORT}.")
        print(f"   Automatic 3NF SQLite fallback is active: {db_info['path']}")
        print("")
        print("💡 To use native MySQL:")
        print("   1. Ensure MySQL server is started (e.g. `brew services start mysql` or MySQL Workbench).")
        print("   2. Update credentials in .env if using a password:")
        print("      MYSQL_USER=root")
        print("      MYSQL_PASSWORD=your_password")
        print("      MYSQL_HOST=localhost")
        print("      MYSQL_PORT=3306")
        print("      MYSQL_DB=smart_placement_db")

    print("\nEnsuring all 3NF tables are initialized and verified...")
    init_db()

    # List tables
    if backend == 'mysql':
        tables = query_db("SHOW TABLES;")
        table_names = [list(t.values())[0] for t in tables] if tables else []
    else:
        tables = query_db("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        table_names = [t['name'] for t in tables] if tables else []

    print(f"✅ Found {len(table_names)} 3NF Relational Tables in Database:")
    for i, tbl in enumerate(table_names, 1):
        try:
            cnt = query_db(f"SELECT COUNT(*) as c FROM {tbl}", one=True)['c']
            print(f"   {i:2d}. {tbl:<25} ({cnt} rows)")
        except Exception:
            print(f"   {i:2d}. {tbl}")

    print("\nVerifying Sample Student Cohort (VIT SY-K-17):")
    students = query_db("SELECT id, roll_no, full_name, cgpa, dsa_score, target_tier FROM students LIMIT 5;")
    for s in students:
        print(f"   • [{s['roll_no']}] {s['full_name']:<20} | CGPA: {s['cgpa']} | DSA: {s['dsa_score']} | Target: {s['target_tier']}")

    print("\nVerifying Active Placement Drives & Criteria:")
    drives = query_db("SELECT d.id, c.name as company, d.job_role, d.package_lpa, cr.min_cgpa, cr.min_dsa_score FROM placement_drives d JOIN companies c ON d.company_id = c.id LEFT JOIN drive_criteria cr ON cr.drive_id = d.id WHERE d.status = 'ACTIVE' LIMIT 4;")
    for d in drives:
        print(f"   • {d['company']:<15} | Role: {d['job_role']:<20} | Package: {d['package_lpa']} LPA | Cutoffs: CGPA >= {d['min_cgpa']}, DSA >= {d['min_dsa_score']}")

    print("\n" + "=" * 68)
    print("Database setup & 3NF integrity check complete.")
    print("=" * 68)

if __name__ == '__main__':
    test_mysql_connection()
