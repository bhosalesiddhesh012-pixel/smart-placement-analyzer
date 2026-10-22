import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import joblib
import config

_model_package = None

def get_model():
    global _model_package
    if _model_package is None:
        if not os.path.exists(config.MODEL_PATH):
            from ml.train_model import train_and_export
            train_and_export()
        _model_package = joblib.load(config.MODEL_PATH)
    return _model_package

def predict_student_readiness(student_dict):
    """
    Accepts student profile dict, runs through Random Forest Classifier & Regressor.
    Returns:
        readiness_index: float (0 - 100)
        predicted_tier: str ('Tier 1 Product', 'Tier 2 Core', 'Mass Recruiter', 'Needs Remediation')
        tier_probabilities: dict
        feature_vector: DataFrame
    """
    pkg = get_model()
    feature_names = pkg['feature_names']
    target_classes = pkg['target_classes']

    # Build input vector with safety defaults
    data = {}
    for feat in feature_names:
        val = student_dict.get(feat, 0)
        data[feat] = [float(val)]

    df_in = pd.DataFrame(data)

    # Predict tier & probabilities
    clf = pkg['classifier']
    reg = pkg['regressor']

    # Check if student profile is empty/uninitialized (all core metrics are 0)
    is_uninitialized = (
        float(student_dict.get('cgpa', 0) or 0) == 0.0 and
        float(student_dict.get('ssc_percentage', 0) or 0) == 0.0 and
        float(student_dict.get('hsc_percentage', 0) or 0) == 0.0 and
        float(student_dict.get('dsa_score', 0) or 0) == 0.0 and
        int(student_dict.get('leetcode_solved', 0) or 0) == 0 and
        int(student_dict.get('projects_count', 0) or 0) == 0 and
        float(student_dict.get('soft_skills_score', 0) or 0) == 0.0
    )
    if is_uninitialized:
        return {
            'readiness_index': 0.0,
            'predicted_tier': student_dict.get('target_tier') or 'Uninitialized',
            'tier_probabilities': {c: 0.0 for c in target_classes},
            'feature_vector': df_in
        }

    tier_idx = clf.predict(df_in)[0]
    tier_name = target_classes[tier_idx]
    probs = clf.predict_proba(df_in)[0]
    prob_dict = {target_classes[i]: round(float(probs[i]) * 100, 1) for i in range(len(target_classes))}

    # Predict readiness score
    raw_score = float(reg.predict(df_in)[0])
    readiness_index = max(10.0, min(99.0, round(raw_score, 1)))

    return {
        'readiness_index': readiness_index,
        'predicted_tier': tier_name,
        'tier_probabilities': prob_dict,
        'feature_vector': df_in
    }

if __name__ == '__main__':
    # Quick sanity check
    sample_student = {
        'cgpa': 9.2,
        'ssc_percentage': 90.0,
        'hsc_percentage': 88.0,
        'active_backlogs': 0,
        'history_backlogs': 0,
        'dsa_score': 85.0,
        'leetcode_solved': 280,
        'hackathons_won': 2,
        'projects_count': 4,
        'certifications_count': 3,
        'soft_skills_score': 82.0
    }
    res = predict_student_readiness(sample_student)
    print("Sanity Test Result:")
    print("Readiness Index:", res['readiness_index'])
    print("Predicted Tier:", res['predicted_tier'])
    print("Probabilities:", res['tier_probabilities'])
