import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, r2_score
import joblib
import shap
import config

FEATURE_NAMES = [
    'cgpa',
    'ssc_percentage',
    'hsc_percentage',
    'active_backlogs',
    'history_backlogs',
    'dsa_score',
    'leetcode_solved',
    'hackathons_won',
    'projects_count',
    'certifications_count',
    'soft_skills_score'
]

TARGET_CLASSES = ['Needs Remediation', 'Mass Recruiter', 'Tier 2 Core', 'Tier 1 Product']

def generate_synthetic_dataset(n_samples=1500, random_state=42):
    rng = np.random.default_rng(random_state)

    # 1. Academics
    cgpa = np.clip(rng.normal(7.8, 1.1, n_samples), 5.2, 9.95)
    ssc = np.clip(rng.normal(82.0, 8.5, n_samples), 55.0, 98.5)
    hsc = np.clip(rng.normal(79.0, 9.0, n_samples), 52.0, 98.0)

    # 2. Backlogs (poisson distributed)
    active_backlogs = rng.choice([0, 1, 2, 3], size=n_samples, p=[0.72, 0.18, 0.07, 0.03])
    history_backlogs = active_backlogs + rng.choice([0, 1, 2], size=n_samples, p=[0.75, 0.18, 0.07])

    # 3. Coding & Technical
    # Correlated with CGPA to some degree, but with high variance
    dsa_base = (cgpa - 5.0) * 16.0 + rng.normal(0, 12, n_samples)
    dsa_score = np.clip(dsa_base, 10.0, 99.0)

    leetcode_solved = np.clip((dsa_score * 3.8 + rng.normal(0, 40, n_samples)).astype(int), 5, 550)
    hackathons_won = rng.choice([0, 1, 2, 3, 4], size=n_samples, p=[0.55, 0.25, 0.12, 0.06, 0.02])
    projects_count = np.clip(rng.poisson(2.5, n_samples), 1, 7)
    certifications_count = np.clip(rng.poisson(1.8, n_samples), 0, 5)

    # 4. Soft Skills & Interview Fluency
    soft_skills = np.clip(rng.normal(74.0, 11.0, n_samples), 40.0, 98.0)

    # Calculate Composite Placement Readiness Index (0-100)
    # Weights reflecting standard campus placements:
    # Academics 25%, Coding/DSA 35%, Projects/Hackathons 20%, Soft Skills 20% - Penalties for backlogs
    academic_score = (cgpa / 10.0) * 100.0 * 0.15 + (ssc * 0.05) + (hsc * 0.05)
    coding_score = (dsa_score * 0.22) + (np.clip(leetcode_solved / 350.0, 0, 1) * 100.0 * 0.13)
    project_score = (np.clip(projects_count / 4.0, 0, 1) * 60.0 + np.clip(hackathons_won / 2.0, 0, 1) * 25.0 + np.clip(certifications_count / 3.0, 0, 1) * 15.0) * 0.20
    communication_score = soft_skills * 0.20

    backlog_penalty = (active_backlogs * 14.0) + (history_backlogs * 3.0)

    readiness_index = np.clip(academic_score + coding_score + project_score + communication_score - backlog_penalty, 15.0, 99.5)

    # Tier Categorization
    tier_labels = []
    tier_indices = []
    for i in range(n_samples):
        r = readiness_index[i]
        c = cgpa[i]
        d = dsa_score[i]
        ab = active_backlogs[i]

        if r >= 82.0 and c >= 8.0 and d >= 75.0 and ab == 0:
            tier_indices.append(3) # Tier 1 Product
            tier_labels.append('Tier 1 Product')
        elif r >= 68.0 and c >= 7.0 and d >= 60.0 and ab <= 1:
            tier_indices.append(2) # Tier 2 Core
            tier_labels.append('Tier 2 Core')
        elif r >= 52.0 and c >= 6.0 and ab <= 2:
            tier_indices.append(1) # Mass Recruiter
            tier_labels.append('Mass Recruiter')
        else:
            tier_indices.append(0) # Needs Remediation
            tier_labels.append('Needs Remediation')

    df = pd.DataFrame({
        'cgpa': np.round(cgpa, 2),
        'ssc_percentage': np.round(ssc, 2),
        'hsc_percentage': np.round(hsc, 2),
        'active_backlogs': active_backlogs,
        'history_backlogs': history_backlogs,
        'dsa_score': np.round(dsa_score, 1),
        'leetcode_solved': leetcode_solved,
        'hackathons_won': hackathons_won,
        'projects_count': projects_count,
        'certifications_count': certifications_count,
        'soft_skills_score': np.round(soft_skills, 1),
        'placement_readiness_index': np.round(readiness_index, 1),
        'target_tier_idx': tier_indices,
        'target_tier': tier_labels
    })

    return df

def train_and_export():
    print("Generating comprehensive campus training dataset (1,800 records)...")
    df = generate_synthetic_dataset(n_samples=1800, random_state=42)

    X = df[FEATURE_NAMES]
    y_tier = df['target_tier_idx']
    y_score = df['placement_readiness_index']

    X_train, X_test, y_tier_train, y_tier_test, y_score_train, y_score_test = train_test_split(
        X, y_tier, y_score, test_size=0.2, random_state=42, stratify=y_tier
    )

    print("Training RandomForestClassifier for Tier Categorization...")
    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=10,
        min_samples_split=4,
        random_state=42,
        class_weight='balanced'
    )
    clf.fit(X_train, y_tier_train)

    y_pred_tier = clf.predict(X_test)
    acc = accuracy_score(y_tier_test, y_pred_tier)
    print(f"RandomForest Tier Classifier Test Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_tier_test, y_pred_tier, target_names=TARGET_CLASSES))

    print("Training GradientBoostingRegressor for fine-grained Readiness Index...")
    reg = GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.08,
        random_state=42
    )
    reg.fit(X_train, y_score_train)
    score_pred = reg.predict(X_test)
    r2 = r2_score(y_score_test, score_pred)
    print(f"Readiness Index Regressor R^2 Score: {r2:.3f}")

    print("Initializing SHAP TreeExplainer for Explainable AI...")
    # Using the regressor or classifier for SHAP explanation
    # The regressor explains continuous readiness score contributions directly in points (+/-)
    explainer = shap.TreeExplainer(reg, feature_perturbation='tree_path_dependent')

    package = {
        'classifier': clf,
        'regressor': reg,
        'explainer': explainer,
        'feature_names': FEATURE_NAMES,
        'target_classes': TARGET_CLASSES,
        'feature_means': X_train.mean().to_dict(),
        'feature_stds': X_train.std().to_dict(),
        'base_value': float(reg.predict(X_train).mean())
    }

    os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)
    joblib.dump(package, config.MODEL_PATH)
    print(f"Trained AI/ML & SHAP bundle successfully saved to {config.MODEL_PATH}!")

if __name__ == '__main__':
    train_and_export()
