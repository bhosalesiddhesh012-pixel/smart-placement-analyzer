import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
import json
from database.db import query_db, init_db, get_db_info
from database.seed_data import seed
from ml.predictor import predict_student_readiness
from ml.explainer import explain_student_prediction
from ml.audio_analyzer import analyze_audio_fluency, create_sample_wav
from engine.eligibility_engine import evaluate_student_drive_eligibility
from engine.diagnostic_engine import generate_personalized_remediation
from app import app
import config

class TestSmartPlacementAnalyzer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n--- Initializing Automated System Test Suite ---")
        init_db()
        seed()

    def test_01_database_integrity(self):
        print("Testing 3NF Relational Database tables & seeded records...")
        db_info = get_db_info()
        self.assertIn('backend', db_info)

        students = query_db("SELECT count(*) as c FROM students", one=True)['c']
        self.assertGreaterEqual(students, 6, "Expected at least 6 students in database")

        companies = query_db("SELECT count(*) as c FROM companies", one=True)['c']
        self.assertGreaterEqual(companies, 5, "Expected at least 5 companies in database")

        drives = query_db("SELECT count(*) as c FROM placement_drives", one=True)['c']
        self.assertGreaterEqual(drives, 5, "Expected at least 5 placement drives")

        # Verify group members exist
        siddhesh = query_db("SELECT * FROM students WHERE roll_no = '2071126'", one=True)
        self.assertIsNotNone(siddhesh)
        self.assertEqual(siddhesh['full_name'], 'Siddhesh Bhosale')

        arpit = query_db("SELECT * FROM students WHERE roll_no = '2071161'", one=True)
        self.assertIsNotNone(arpit)
        self.assertEqual(arpit['full_name'], 'Arpit Tale')
        print("✓ Database 3NF schema & seed verification passed.")

    def test_02_ml_prediction(self):
        print("Testing RandomForest & Regressor Placement Prediction...")
        test_student = {
            'cgpa': 9.25,
            'ssc_percentage': 91.4,
            'hsc_percentage': 89.6,
            'active_backlogs': 0,
            'history_backlogs': 0,
            'dsa_score': 88.5,
            'leetcode_solved': 320,
            'hackathons_won': 2,
            'projects_count': 4,
            'certifications_count': 3,
            'soft_skills_score': 85.0
        }
        res = predict_student_readiness(test_student)
        self.assertIn('readiness_index', res)
        self.assertIn('predicted_tier', res)
        self.assertGreaterEqual(res['readiness_index'], 75.0)
        self.assertIn(res['predicted_tier'], ['Tier 1 Product', 'Tier 2 Core'])
        print(f"✓ ML Prediction passed: Index={res['readiness_index']}, Tier={res['predicted_tier']}")

    def test_03_explainable_ai_shap(self):
        print("Testing TreeSHAP Local Feature Attribution Calculation...")
        test_student = {
            'cgpa': 7.65,
            'ssc_percentage': 82.0,
            'hsc_percentage': 78.5,
            'active_backlogs': 1,
            'history_backlogs': 1,
            'dsa_score': 58.0,
            'leetcode_solved': 85,
            'hackathons_won': 0,
            'projects_count': 2,
            'certifications_count': 1,
            'soft_skills_score': 68.0
        }
        exp = explain_student_prediction(test_student)
        self.assertIn('base_value', exp)
        self.assertIn('contributions', exp)
        self.assertIn('chart_data', exp)
        self.assertEqual(len(exp['contributions']), 11, "Expected 11 feature contributions")

        # Active backlog should be a negative impact
        backlog_contrib = next(c for c in exp['contributions'] if c['feature'] == 'active_backlogs')
        self.assertLess(backlog_contrib['shap_value'], 0, "Active backlogs must have negative SHAP attribution")
        print(f"✓ SHAP XAI passed: Base={exp['base_value']}, Active Backlog SHAP={backlog_contrib['shap_value']}")

    def test_04_librosa_acoustic_analysis(self):
        print("Testing Librosa Acoustic Signal Processing...")
        test_wav = os.path.join(config.UPLOAD_FOLDER, 'unit_test_tone.wav')
        create_sample_wav(test_wav, duration=3.5)
        self.assertTrue(os.path.exists(test_wav))

        res = analyze_audio_fluency(test_wav)
        self.assertIn('soft_skills_score', res)
        self.assertIn('pitch_mean_hz', res)
        self.assertIn('speaking_rate_wpm', res)
        self.assertIn('pause_ratio', res)
        self.assertGreaterEqual(res['soft_skills_score'], 0)
        self.assertLessEqual(res['soft_skills_score'], 100)
        print(f"✓ Librosa Audio Analysis passed: Soft Skills Score={res['soft_skills_score']}, WPM={res['speaking_rate_wpm']}")

    def test_05_dynamic_recruiter_eligibility(self):
        print("Testing Dynamic Eligibility Screening against live DB criteria...")
        # Siddhesh Bhosale (Student 1) vs Google India (Drive 1)
        res_siddhesh = evaluate_student_drive_eligibility(1, 1)
        self.assertEqual(res_siddhesh['status'], 'ELIGIBLE')
        self.assertEqual(len(res_siddhesh['deficits']), 0)

        # Arpit Tale (Student 4) vs Google India (Drive 1)
        res_arpit = evaluate_student_drive_eligibility(4, 1)
        self.assertEqual(res_arpit['status'], 'INELIGIBLE')
        self.assertGreater(len(res_arpit['deficits']), 0)
        print(f"✓ Dynamic Eligibility passed: Siddhesh={res_siddhesh['status']}, Arpit={res_arpit['status']} ({len(res_arpit['deficits'])} deficits)")

    def test_06_flask_routes(self):
        print("Testing Flask Web Endpoints & RBAC...")
        client = app.test_client()

        # Login page
        res = client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Smart Campus Placement Analyser', res.data)

        # Demo login as student
        res_demo = client.get('/demo-login/2', follow_redirects=True)
        self.assertEqual(res_demo.status_code, 200)
        self.assertIn(b'Siddhesh Bhosale', res_demo.data)

        # Student Explainability view
        res_xai = client.get('/explainability')
        self.assertEqual(res_xai.status_code, 200)
        self.assertIn(b'Explainable AI', res_xai.data)

        # Student Speech Lab
        res_lab = client.get('/interview-lab')
        self.assertEqual(res_lab.status_code, 200)
        self.assertIn(b'Interview Speech Fluency Lab', res_lab.data)

        # Switch to TPO Admin
        res_admin_login = client.get('/demo-login/1', follow_redirects=True)
        self.assertEqual(res_admin_login.status_code, 200)
        self.assertIn(b'Placement Cell Administration', res_admin_login.data)
        print("✓ All Flask Web routes and RBAC transitions passed.")

if __name__ == '__main__':
    unittest.main()
