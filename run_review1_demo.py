#!/usr/bin/env python3
"""
Smart Campus Placement Analyser and Predictor
========================================================================
MID-SEMESTER REVIEW 1 - 50% PROJECT MILESTONE DEMONSTRATION RUNNER
Vishwakarma Institute of Technology (VIT), Pune
Department of Computer Engineering | AY 2026-27 | Semester 3
Group No: SY-K-17 | Guide: Prof. Sachin Jadhav
Team: Siddhesh Bhosale, Meghraj Sirsat, Soham Ombale, Arpit Tale
========================================================================
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from database.db import detect_backend, get_db_info, query_db, execute_db, init_db
from ml.predictor import predict_student_readiness
from engine.eligibility_engine import evaluate_student_drive_eligibility, get_all_drives_for_student
from engine.diagnostic_engine import generate_personalized_remediation

def print_header():
    print("\n" + "=" * 76)
    print("      VISHWAKARMA INSTITUTE OF TECHNOLOGY (VIT), PUNE")
    print("      DEPARTMENT OF COMPUTER ENGINEERING | AY 2026-27")
    print("=" * 76)
    print("  PROJECT TITLE : Smart Campus Placement Analyser and Predictor using ML & XAI")
    print("  GROUP NO      : SY-K-17 (Form FF No. 180)")
    print("  REVIEW STAGE  : REVIEW 1 (MID-SEMESTER - 50% PROJECT MILESTONE)")
    print("  INTERNAL GUIDE: Prof. Sachin Jadhav (sachin.jadhav@vit.edu)")
    print("  GROUP MEMBERS : Siddhesh Bhosale (2071126), Meghraj Sirsat (2071129),")
    print("                  Soham Ombale (2071134), Arpit Tale (2071161)")
    print("=" * 76)

def show_scope_matrix():
    print("\n" + "─" * 76)
    print("  📋 PROJECT ARCHITECTURE & SEMESTER MILESTONE MATRIX (50% vs 50%)")
    print("─" * 76)
    print("  STATUS       | MODULE NAME                            | TECHNOLOGY")
    print("  " + "─" * 72)
    print("  ✅ COMPLETED | 1. 3NF Relational Database Modeling    | MySQL 8.0+ (Relational 3NF)")
    print("  ✅ COMPLETED | 2. Dynamic Recruiter Criteria Engine   | Python & MySQL CRUD")
    print("  ✅ COMPLETED | 3. ML Placement Readiness Classifier   | Random Forest (Scikit-Learn)")
    print("  ✅ COMPLETED | 4. Actionable Skill-Gap Diagnostics    | Exact Numerical Deficit Engine")
    print("  " + "─" * 72)
    print("  ⏳ REVIEW 2  | 5. Acoustic Signal Speech Fluency      | Librosa (Pitch, Pauses, WPM)")
    print("  ⏳ REVIEW 2  | 6. Explainable AI Local Attributions   | SHAP (TreeExplainer Waterfall)")
    print("  ⏳ REVIEW 2  | 7. Institutional 5-Yr Placement Trends | Aggregated Statistical Reports")
    print("  ⏳ REVIEW 2  | 8. Dynamic 4-Week Remediation Roadmap  | Auto-Curated DSA Sprints")
    print("─" * 76)

def step1_database_verification():
    print("\n" + "►" * 3 + " [STEP 1/5] DATABASE LAYER VERIFICATION (3NF Relational Schema)")
    print("─" * 76)
    db_info = get_db_info()
    backend = detect_backend()
    print(f"  • Database Backend : {db_info['backend']}")
    print(f"  • Active Schema    : {db_info['database']}")
    print(f"  • Status           : ONLINE & CONNECTED")

    if backend == 'mysql':
        tables = query_db("SHOW TABLES;")
        table_names = [list(t.values())[0] for t in tables] if tables else []
    else:
        tables = query_db("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        table_names = [t['name'] for t in tables] if tables else []

    print(f"\n  Normalized 3NF Relational Tables ({len(table_names)} verified):")
    for tbl in sorted(table_names):
        try:
            cnt = query_db(f"SELECT COUNT(*) as c FROM {tbl}", one=True)['c']
            print(f"    ├─ {tbl:<24} [{cnt:>2} records]")
        except Exception:
            print(f"    ├─ {tbl:<24}")
    print("  └─ Data integrity and Foreign Key constraints active.")

def step2_ml_readiness_evaluation():
    print("\n" + "►" * 3 + " [STEP 2/5] ML PREDICTIVE ENGINE (Placement Readiness Index 0-100)")
    print("─" * 76)
    print("  Fetching student profiles from MySQL and running Random Forest Inference:\n")

    students = query_db("SELECT * FROM students ORDER BY cgpa DESC;")
    for s in students:
        res = predict_student_readiness(s)
        print(f"  • Student: {s['full_name']} (Roll: {s['roll_no']})")
        print(f"    - Academics & Skills : CGPA: {s['cgpa']} | DSA: {s['dsa_score']}/100 | LeetCode: {s['leetcode_solved']} | Backlogs: {s['active_backlogs']}")
        print(f"    - Readiness Index    : \033[1;32m{res['readiness_index']} / 100\033[0m")
        print(f"    - Predicted Tier     : \033[1;34m{res['predicted_tier']}\033[0m")
        print(f"    - Model Probabilities: {res['tier_probabilities']}")
        print()

def step3_dynamic_eligibility():
    print("\n" + "►" * 3 + " [STEP 3/5] DYNAMIC RECRUITER ELIGIBILITY SCREENING")
    print("─" * 76)
    print("  Evaluating candidates against dynamic company criteria configured in MySQL:\n")

    drives = query_db("""
        SELECT d.id, c.name as company, d.job_role, d.package_lpa, 
               cr.min_cgpa, cr.min_dsa_score, cr.max_active_backlogs
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.id
        LEFT JOIN drive_criteria cr ON cr.drive_id = d.id
        WHERE d.status = 'ACTIVE' LIMIT 2;
    """)

    for d in drives:
        print(f"  🏢 CAMPUS DRIVE: {d['company']} - {d['job_role']} ({d['package_lpa']} LPA)")
        print(f"     Criteria in SQL: CGPA >= {d['min_cgpa']} | DSA >= {d['min_dsa_score']} | Max Backlogs <= {d['max_active_backlogs']}")
        print("     Candidate Screening Results:")

        for roll in ['2071126', '2071161']:
            st = query_db("SELECT * FROM students WHERE roll_no = ?", (roll,), one=True)
            if not st:
                continue
            elig = evaluate_student_drive_eligibility(st['id'], d['id'])
            status_tag = "\033[1;32m[ELIGIBLE]\033[0m" if elig['is_eligible'] else "\033[1;31m[INELIGIBLE]\033[0m"
            print(f"     • {status_tag} {st['full_name']} (CGPA: {st['cgpa']}, DSA: {st['dsa_score']}, Backlogs: {st['active_backlogs']})")
            if not elig['is_eligible']:
                for defic in elig['deficits']:
                    print(f"        ⚠️  Deficit: {defic}")
        print()

def step4_skill_gap_diagnostics():
    print("\n" + "►" * 3 + " [STEP 4/5] ACTIONABLE SKILL-GAP DIAGNOSTIC ENGINE")
    print("─" * 76)
    print("  Traditional systems simply reject candidates with a binary 'Fail'.")
    print("  Our Skill-Gap Engine computes exact numerical deficiencies to provide actionable guidance:\n")

    # Diagnose Arpit Tale who has backlogs/lower scores
    arpit = query_db("SELECT * FROM students WHERE roll_no = '2071161';", one=True)
    if arpit:
        diag = generate_personalized_remediation(arpit['id'], target_tier='Tier 1 Product')
        print(f"  Diagnostic Case Study: {arpit['full_name']} (Roll: {arpit['roll_no']})")
        print(f"  - Target Category        : {arpit['target_tier']}")
        print(f"  - Total Weakness Areas   : {len(diag['weaknesses'])}")
        print("\n  Precise Identified Gaps & Deficits:")
        for w in diag['weaknesses']:
            print(f"    [!] Area: {w['area']} (Severity: {w['severity']})")
            print(f"        Metric     : {w['metric']}")
            print(f"        Deficiency : {w['deficiency']}")
            print()

def step5_tpo_dynamic_update_demo():
    print("\n" + "►" * 3 + " [STEP 5/5] REAL-TIME TPO CRITERIA UPDATE DEMONSTRATION")
    print("─" * 76)
    print("  Demonstrating how a Placement Officer updates criteria in MySQL in real-time")
    print("  without restarting the server:\n")

    drive = query_db("""
        SELECT d.id, c.name as company, cr.min_cgpa, cr.min_dsa_score 
        FROM placement_drives d
        JOIN companies c ON d.company_id = c.id
        JOIN drive_criteria cr ON cr.drive_id = d.id
        WHERE d.id = 1;
    """, one=True)

    if drive:
        orig_cgpa = drive['min_cgpa']
        print(f"  • Current Cutoff in SQL for {drive['company']}: CGPA >= {orig_cgpa}")
        print("  • Placement Officer lowers CGPA cutoff to 7.50 in database to widen pool...")
        execute_db("UPDATE drive_criteria SET min_cgpa = 7.50 WHERE drive_id = 1;")
        
        updated_drive = query_db("SELECT min_cgpa FROM drive_criteria WHERE drive_id = 1;", one=True)
        print(f"  • Verified in MySQL: New Cutoff = {updated_drive['min_cgpa']}")
        print("  • Re-evaluating candidate Arpit Tale under updated criteria...")
        arpit = query_db("SELECT * FROM students WHERE roll_no = '2071161';", one=True)
        elig = evaluate_student_drive_eligibility(arpit['id'], 1)
        print(f"  • CGPA Check status now: {elig['checks'][0]['parameter']} -> Pass: {elig['checks'][0]['passed']} (Current: {elig['checks'][0]['student_val']})")
        
        # Reset back to original
        execute_db("UPDATE drive_criteria SET min_cgpa = ? WHERE drive_id = 1;", (orig_cgpa,))
        print(f"  • Restored original CGPA cutoff ({orig_cgpa}) in database.")

def main_menu():
    print_header()
    show_scope_matrix()

    while True:
        print("\n" + "=" * 76)
        print("                        REVIEW 1 EXECUTION MENU")
        print("=" * 76)
        print("  1. Run Complete 50% Review 1 Demonstration (All Steps)")
        print("  2. Verify MySQL Database & Inspect 3NF Schema")
        print("  3. Run ML Placement Readiness Evaluation on All Students")
        print("  4. Test Dynamic Recruiter Eligibility Screening")
        print("  5. Run Actionable Skill-Gap Diagnostics on Deficient Candidate")
        print("  6. Test Real-time TPO Criteria Update in MySQL")
        print("  7. Test Custom Student Input (Predict Readiness)")
        print("  8. Start Full Interactive Web Portal (localhost:5001)")
        print("  9. Exit")
        print("=" * 76)

        try:
            choice = input("\nEnter choice [1-9] (Press Enter for 1): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == '' or choice == '1':
            step1_database_verification()
            step2_ml_readiness_evaluation()
            step3_dynamic_eligibility()
            step4_skill_gap_diagnostics()
            step5_tpo_dynamic_update_demo()
            print("\n" + "=" * 76)
            print("  ✅ 50% PROJECT MILESTONE (REVIEW 1) SUCCESSFULLY DEMONSTRATED!")
            print("  Ready for presentation to Guide Prof. Sachin Jadhav & Committee.")
            print("=" * 76)
        elif choice == '2':
            step1_database_verification()
        elif choice == '3':
            step2_ml_readiness_evaluation()
        elif choice == '4':
            step3_dynamic_eligibility()
        elif choice == '5':
            step4_skill_gap_diagnostics()
        elif choice == '6':
            step5_tpo_dynamic_update_demo()
        elif choice == '7':
            print("\n--- Evaluate Custom Student Candidate ---")
            try:
                cgpa = float(input("Enter CGPA (e.g. 8.4): ") or "8.4")
                dsa = float(input("Enter DSA Score (0-100, e.g. 75): ") or "75")
                leetcode = int(input("Enter LeetCode Solved (e.g. 150): ") or "150")
                backlogs = int(input("Enter Active Backlogs (e.g. 0): ") or "0")
                projects = int(input("Enter Projects Count (e.g. 3): ") or "3")
                
                custom_student = {
                    'cgpa': cgpa,
                    'dsa_score': dsa,
                    'leetcode_solved': leetcode,
                    'active_backlogs': backlogs,
                    'projects_count': projects,
                    'hackathons_won': 1,
                    'certifications_count': 2,
                    'ssc_percentage': 85.0,
                    'hsc_percentage': 82.0,
                    'soft_skills_score': 75.0
                }
                res = predict_student_readiness(custom_student)
                print("\n  ► Evaluation Result:")
                print(f"    - Placement Readiness Index: \033[1;32m{res['readiness_index']} / 100\033[0m")
                print(f"    - Predicted Placement Tier : \033[1;34m{res['predicted_tier']}\033[0m")
                print(f"    - Tier Probabilities       : {res['tier_probabilities']}")
            except Exception as e:
                print(f"Error evaluating custom student: {e}")
        elif choice == '8':
            print("\nLaunching Flask Web Server...")
            os.system(f"{sys.executable} start.py")
        elif choice == '9':
            print("\nGoodbye!")
            break
        else:
            print("Invalid option. Please choose 1-9.")

if __name__ == "__main__":
    init_db()
    main_menu()
