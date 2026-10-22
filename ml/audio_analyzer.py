import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import soundfile as sf
import librosa
import config

def analyze_audio_fluency(audio_path):
    """
    Performs acoustic signal analysis on speech audio using Librosa.
    Extracts pitch, pauses, speaking rate, and energy dynamics to calculate
    an objective soft-skills & interview fluency score.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Load audio (downsampled to 16kHz for fast speech processing)
    y, sr = librosa.load(audio_path, sr=16000, mono=True)
    total_duration = float(librosa.get_duration(y=y, sr=sr))

    if total_duration < 1.0:
        return {
            'error': 'Audio clip is too short. Please speak for at least 3 seconds.',
            'soft_skills_score': 50.0,
            'confidence_level': 'Insufficient Audio'
        }

    # 1. Non-silent speech intervals & Pause Detection
    # top_db=24 splits quiet background noise from active speech
    intervals = librosa.effects.split(y, top_db=24)
    active_speech_samples = sum(end - start for start, end in intervals)
    speech_duration = float(active_speech_samples / sr)
    pause_duration = max(0.0, total_duration - speech_duration)
    pause_ratio = (pause_duration / total_duration) * 100.0

    # 2. Speaking Rate (Onset / Syllable Cadence)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=False)
    num_onsets = len(onset_frames)
    # Estimate words per minute (typically ~1.4 to 1.7 onsets/syllables per spoken word)
    estimated_syllables_per_sec = num_onsets / max(speech_duration, 1.0)
    estimated_wpm = round(min(220, max(50, (estimated_syllables_per_sec / 1.5) * 60)), 1)

    # 3. Pitch Contour & Modulation (F0 Analysis)
    f0 = librosa.yin(y, fmin=65, fmax=350, sr=sr)
    valid_f0 = f0[~np.isnan(f0)]
    valid_f0 = valid_f0[(valid_f0 >= 75) & (valid_f0 <= 320)]

    if len(valid_f0) > 0:
        pitch_mean = float(np.mean(valid_f0))
        pitch_std = float(np.std(valid_f0))
    else:
        pitch_mean = 145.0
        pitch_std = 25.0

    # 4. RMS Energy & Vocal Projection
    rms = librosa.feature.rms(y=y)[0]
    mean_rms = float(np.mean(rms))
    rms_std = float(np.std(rms))

    # 5. Multi-criteria Objective Scoring Algorithm
    # a) Pause / Fluency Score (Target pause ratio: 15% - 28%)
    if 15.0 <= pause_ratio <= 30.0:
        pause_score = 35.0
    elif 10.0 <= pause_ratio < 15.0 or 30.0 < pause_ratio <= 42.0:
        pause_score = 27.0
    elif pause_ratio < 10.0:
        pause_score = 20.0 # Rushing without breathing
    else:
        pause_score = max(10.0, 35.0 - (pause_ratio - 30.0) * 0.8) # Excessive hesitation

    # b) Speaking Rate Score (Target: 120 - 160 WPM)
    if 120 <= estimated_wpm <= 160:
        wpm_score = 25.0
    elif 100 <= estimated_wpm < 120 or 160 < estimated_wpm <= 180:
        wpm_score = 20.0
    elif estimated_wpm < 100:
        wpm_score = 14.0 # Too slow / hesitating
    else:
        wpm_score = 15.0 # Too fast / anxious cadence

    # c) Pitch Expressiveness (Standard deviation target: 20Hz - 45Hz)
    if 20.0 <= pitch_std <= 45.0:
        pitch_score = 25.0
    elif 14.0 <= pitch_std < 20.0 or 45.0 < pitch_std <= 60.0:
        pitch_score = 19.0
    elif pitch_std < 14.0:
        pitch_score = 12.0 # Monotone delivery
    else:
        pitch_score = 16.0 # Erratic pitch swings

    # d) Energy / Projection (Target mean RMS > 0.02)
    if mean_rms >= 0.025:
        energy_score = 15.0
    elif mean_rms >= 0.012:
        energy_score = 11.0
    else:
        energy_score = 7.0 # Soft / unclear voice

    total_score = round(pause_score + wpm_score + pitch_score + energy_score, 1)

    # Qualitative Assessment & Confidence Level
    if total_score >= 82.0:
        confidence_level = "High Professional Fluency"
    elif total_score >= 68.0:
        confidence_level = "Good Communicator"
    elif total_score >= 55.0:
        confidence_level = "Moderate - Room for Polish"
    else:
        confidence_level = "Needs Communication Coaching"

    # Actionable Feedback Tips
    feedback_notes = []
    if pause_ratio > 35.0:
        feedback_notes.append("High hesitation detected. Practice structuring answers using the STAR (Situation, Task, Action, Result) method to avoid filler silences.")
    elif pause_ratio < 12.0:
        feedback_notes.append("Speech pacing is slightly rushed. Introduce natural 1-second pauses after key points to let technical recruiters absorb your answer.")
    else:
        feedback_notes.append("Excellent natural pausing and breath control throughout the response.")

    if pitch_std < 16.0:
        feedback_notes.append("Vocal tone is somewhat monotone. Emphasize key technical verbs and impactful project outcomes with vocal inflections.")
    else:
        feedback_notes.append("Engaging tonal dynamics and expressive vocal range.")

    if estimated_wpm < 110:
        feedback_notes.append("Delivery speed is on the slower side. Aim for 130-150 words per minute for crisp communication.")
    elif estimated_wpm > 165:
        feedback_notes.append("Speaking tempo is fast. Slowing down slightly improves clarity and displays poise under pressure.")
    else:
        feedback_notes.append("Pacing is well-regulated within the ideal interview speaking rate range.")

    if mean_rms < 0.015:
        feedback_notes.append("Microphone signal / vocal projection was slightly faint. Speak directly toward the microphone with firm chest resonance.")

    return {
        'total_duration': round(total_duration, 2),
        'speech_duration': round(speech_duration, 2),
        'pause_duration': round(pause_duration, 2),
        'pause_ratio': round(pause_ratio, 1),
        'speaking_rate_wpm': estimated_wpm,
        'pitch_mean_hz': round(pitch_mean, 1),
        'pitch_std_hz': round(pitch_std, 1),
        'vocal_energy': round(mean_rms, 4),
        'soft_skills_score': total_score,
        'confidence_level': confidence_level,
        'sub_scores': {
            'fluency_pauses': pause_score,
            'tempo_cadence': wpm_score,
            'pitch_dynamics': pitch_score,
            'energy_projection': energy_score
        },
        'feedback_notes': feedback_notes
    }

def create_sample_wav(output_path, duration=4.0):
    """Generates a synthetic speech-like harmonic tone for testing"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    sr = 16000
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # Formant-like harmonic signal with natural pauses
    freq = 160 + 20 * np.sin(2 * np.pi * 1.5 * t)
    signal = 0.4 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(4 * np.pi * freq * t)
    # Add brief pauses (silences)
    pause_mask = ((t > 1.2) & (t < 1.6)) | ((t > 2.8) & (t < 3.2))
    signal[pause_mask] = 0.001 * np.random.randn(np.sum(pause_mask))
    sf.write(output_path, signal, sr)
    return output_path

if __name__ == '__main__':
    test_wav = os.path.join(config.UPLOAD_FOLDER, 'sample_test.wav')
    create_sample_wav(test_wav)
    print("Testing audio analysis on:", test_wav)
    res = analyze_audio_fluency(test_wav)
    print("Acoustic Fluency Result:")
    print("Soft Skills Score:", res['soft_skills_score'])
    print("Confidence Level:", res['confidence_level'])
    print("Speaking Rate (WPM):", res['speaking_rate_wpm'])
    print("Pause Ratio (%):", res['pause_ratio'])
    print("Feedback Notes:", res['feedback_notes'])
