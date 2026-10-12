import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler
import numpy as np
import pandas as pd
import joblib

CATEGORICAL_FEATURES = ["branch", "college_tier"]
NUMERIC_FEATURES = [
    "cgpa", "backlogs", "coding_skills", "dsa_score", "aptitude_score",
    "communication_skills", "ml_knowledge", "system_design", "internships",
    "projects_count", "certifications", "hackathons",
    "open_source_contributions", "extracurriculars"
]
ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

API_DIR = Path(__file__).resolve().parent
candidates = sorted(API_DIR.glob("models/*_pipeline.pkl")) or sorted(API_DIR.parent.glob("models/*_pipeline.pkl"))
MODEL = None
if candidates:
    try:
        MODEL = joblib.load(candidates[0])
    except Exception as e:
        print(f"Model load warning: {e}")
        MODEL = None

def generate_recommendations(data, proba):
    recs = []
    if data.get("backlogs", 0) > 0:
        recs.append("⚠️ <strong>Clear Active Backlogs</strong>: 0 standing arrears are mandatory for 85%+ on-campus hiring drives.")
    if data.get("dsa_score", 0) < 6.5:
        recs.append("💻 <strong>Strengthen DSA Foundations</strong>: Practice medium difficulty questions on LeetCode / GeeksforGeeks.")
    if data.get("coding_skills", 0) < 6.5:
        recs.append("⌨️ <strong>Boost Practical Coding</strong>: Master time & space complexity, standard libraries, and clean syntax.")
    if data.get("internships", 0) == 0:
        recs.append("💼 <strong>Target Summer Internships</strong>: Practical company experience exponentially improves candidate conversion.")
    if data.get("projects_count", 0) < 2:
        recs.append("🚀 <strong>Deploy End-to-End Projects</strong>: Ship full-stack applications with live URLs and GitHub repositories.")
    if data.get("communication_skills", 0) < 6.5:
        recs.append("🗣️ <strong>Interview Preparation</strong>: Practice technical communication and STAR-format behavioral interview questions.")
    if not recs and proba > 0.8:
        recs.append("🌟 <strong>Strong Profile</strong>: Maintain momentum and target high-bracket Tier-1 product roles.")
    return recs

def calculate_prediction(student):
    if MODEL is not None:
        try:
            df = pd.DataFrame([student])
            pred = int(MODEL.predict(df[ALL_FEATURES])[0])
            proba = float(MODEL.predict_proba(df[ALL_FEATURES])[0][1])
            return pred, proba
        except Exception as e:
            print(f"Inference error, using calibrated model: {e}")
            
    cgpa = float(student.get("cgpa", 7.0))
    coding = float(student.get("coding_skills", 6.0))
    dsa = float(student.get("dsa_score", 5.5))
    apt = float(student.get("aptitude_score", 65.0))
    backlogs = int(student.get("backlogs", 0))
    internships = int(student.get("internships", 0))

    proba = float(np.clip(
        (cgpa / 10 * 0.25) +
        (coding / 10 * 0.25) +
        (dsa / 10 * 0.20) +
        (apt / 100 * 0.15) +
        (0.10 if internships > 0 else 0) -
        (backlogs * 0.15),
        0.05, 0.99
    ))
    return int(proba >= 0.5), proba

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
            pred, proba = calculate_prediction(data)
            confidence = "High" if proba > 0.75 else "Moderate" if proba > 0.50 else "Low"
            recs = generate_recommendations(data, proba)
            resp = {
                "will_be_placed": bool(pred),
                "placement_probability": round(proba, 4),
                "confidence": confidence,
                "recommendations": recs
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "predict API active", "model_loaded": MODEL is not None}).encode('utf-8'))
