import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import shap
from ml.predictor import get_model, predict_student_readiness

HUMAN_FEATURE_LABELS = {
    'cgpa': 'Engineering CGPA',
    'ssc_percentage': '10th (SSC) Score',
    'hsc_percentage': '12th (HSC) Score',
    'active_backlogs': 'Active Backlogs',
    'history_backlogs': 'History of Backlogs',
    'dsa_score': 'Data Structures & Algorithms',
    'leetcode_solved': 'LeetCode Problems Solved',
    'hackathons_won': 'Hackathons & Competitions',
    'projects_count': 'Technical Projects',
    'certifications_count': 'Industry Certifications',
    'soft_skills_score': 'Interview Soft-Skills'
}

FEATURE_ICONS = {
    'cgpa': 'fa-graduation-cap',
    'ssc_percentage': 'fa-award',
    'hsc_percentage': 'fa-school',
    'active_backlogs': 'fa-triangle-exclamation',
    'history_backlogs': 'fa-clock-rotate-left',
    'dsa_score': 'fa-code',
    'leetcode_solved': 'fa-terminal',
    'hackathons_won': 'fa-trophy',
    'projects_count': 'fa-laptop-file',
    'certifications_count': 'fa-certificate',
    'soft_skills_score': 'fa-microphone-lines'
}

def explain_student_prediction(student_dict):
    """
    Computes exact SHAP local feature attribution values for a student.
    Returns:
        base_value: float benchmark score
        predicted_score: float student readiness score
        contributions: list of dicts sorted by absolute impact
        positive_factors: top strengths
        negative_factors: top areas needing improvement
        chart_data: labels, values, colors ready for Chart.js waterfall/bar visualization
    """
    pkg = get_model()
    explainer = pkg['explainer']
    feature_names = pkg['feature_names']
    base_val = round(float(pkg.get('base_value', 68.0)), 1)

    # Prepare DataFrame
    pred_res = predict_student_readiness(student_dict)
    df_in = pred_res['feature_vector']
    predicted_score = pred_res['readiness_index']

    # Compute TreeSHAP values
    shap_vals = explainer.shap_values(df_in)

    # Handle shape differences if 2D or 1D
    if isinstance(shap_vals, list):
        # Multi-output case
        sv = shap_vals[0]
    else:
        sv = shap_vals

    if len(sv.shape) > 1:
        sv = sv[0]

    contributions = []
    for i, feat in enumerate(feature_names):
        raw_val = float(df_in[feat].iloc[0])
        impact_val = round(float(sv[i]), 2)
        label = HUMAN_FEATURE_LABELS.get(feat, feat)
        icon = FEATURE_ICONS.get(feat, 'fa-circle-info')

        # Formulate human explanation
        if impact_val > 0:
            direction = 'Positive'
            narrative = f"+{impact_val:.1f} pts: Strong performance in {label} ({raw_val})"
        elif impact_val < 0:
            direction = 'Negative'
            narrative = f"{impact_val:.1f} pts: Deficit or penalty in {label} ({raw_val})"
        else:
            direction = 'Neutral'
            narrative = f"Neutral impact from {label} ({raw_val})"

        contributions.append({
            'feature': feat,
            'label': label,
            'student_value': raw_val,
            'shap_value': impact_val,
            'direction': direction,
            'icon': icon,
            'narrative': narrative,
            'abs_impact': abs(impact_val)
        })

    # Sort by absolute impact magnitude
    contributions.sort(key=lambda x: x['abs_impact'], reverse=True)

    positive_drivers = [c for c in contributions if c['shap_value'] > 0]
    negative_drags = [c for c in contributions if c['shap_value'] < 0]

    # Format data for Chart.js
    chart_labels = [c['label'] for c in contributions]
    chart_values = [c['shap_value'] for c in contributions]
    chart_colors = ['#10B981' if v >= 0 else '#EF4444' for v in chart_values]

    return {
        'base_value': base_val,
        'predicted_score': predicted_score,
        'predicted_tier': pred_res['predicted_tier'],
        'tier_probabilities': pred_res['tier_probabilities'],
        'contributions': contributions,
        'positive_drivers': positive_drivers,
        'negative_drags': negative_drags,
        'chart_data': {
            'labels': chart_labels,
            'impact_values': chart_values,
            'colors': chart_colors
        }
    }

if __name__ == '__main__':
    sample = {
        'cgpa': 7.6,
        'ssc_percentage': 82.0,
        'hsc_percentage': 78.0,
        'active_backlogs': 1,
        'history_backlogs': 1,
        'dsa_score': 58.0,
        'leetcode_solved': 85,
        'hackathons_won': 0,
        'projects_count': 2,
        'certifications_count': 1,
        'soft_skills_score': 68.0
    }
    exp = explain_student_prediction(sample)
    print("Base Value:", exp['base_value'])
    print("Predicted Score:", exp['predicted_score'])
    print("Top Negative Drag:", exp['negative_drags'][0] if exp['negative_drags'] else "None")
    print("Top Positive Driver:", exp['positive_drivers'][0] if exp['positive_drivers'] else "None")
