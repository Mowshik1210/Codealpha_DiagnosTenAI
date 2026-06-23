"""
DiagnosTenAI — Multi Disease Prediction System
File   : app.py  (Windows-compatible final version)
Author : Dharshan (Mowshik) | github.com/Mowshik1210
Batch  : DecodeLabs AI Industrial Training 2026

PDF library: xhtml2pdf  — pure Python, zero system dependencies.
Works on Windows / macOS / Linux with just:
    pip install xhtml2pdf
No GTK, no Pango, no sudo needed.
"""

# ── Standard library ─────────────────────────────────────────
import os
import uuid
import io
from datetime import datetime

# ── Flask ────────────────────────────────────────────────────
from flask import (
    Flask, render_template, request,
    make_response, redirect, url_for
)

# ── Machine learning ─────────────────────────────────────────
import joblib

# ── PDF generation — xhtml2pdf (pure Python, Windows safe) ───
# Install: pip install xhtml2pdf
try:
    from xhtml2pdf import pisa
    PDF_OK = True
except ImportError:
    PDF_OK = False
    print(
        "\n[DiagnosTenAI] WARNING: xhtml2pdf not installed.\n"
        "  Run:  pip install xhtml2pdf\n"
        "  PDF download will fall back to browser print view.\n"
    )

# ─────────────────────────────────────────────────────────────
app = Flask(__name__)


# ═══════════════════════════════════════════════════════════════
# DISEASE REGISTRY
# ═══════════════════════════════════════════════════════════════

DISEASES = {
    "heart": {
        "name": "Heart Disease",
        "model": "models/heart.pkl"
    },
    "diabetes": {
        "name": "Diabetes",
        "model": "models/diabetes.pkl"
    },
    "breast_cancer": {
        "name": "Breast Cancer",
        "model": "models/breast_cancer.pkl"
    },
    "parkinsons": {
        "name": "Parkinson's Disease",
        "model": "models/parkinsons.pkl"
    },
    "kidney": {
        "name": "Kidney Disease",
        "model": "models/kidney.pkl"
    },
    "liver": {
        "name": "Liver Disease",
        "model": "models/liver.pkl"
    },
    "lung": {
        "name": "Lung Cancer",
        "model": "models/lung.pkl"
    },
    "stroke": {
        "name": "Stroke Prediction",
        "model": "models/stroke.pkl"
    },
    "thyroid": {
        "name": "Thyroid Disease",
        "model": "models/thyroid.pkl"
    },
    "alzheimers": {
        "name": "Alzheimer's Disease",
        "model": "models/alzheimers.pkl"
    }
}


# ═══════════════════════════════════════════════════════════════
# RECOMMENDATIONS ENGINE
# ═══════════════════════════════════════════════════════════════

RECOMMENDATIONS = {
    "Heart Disease": {
        "positive": [
            "Consult a cardiologist for a comprehensive cardiac evaluation immediately.",
            "Consider an ECG, echocardiogram, and coronary angiography as advised.",
            "Adopt a heart-healthy diet — low sodium, low saturated fat, high fibre.",
            "Begin a supervised cardiac rehabilitation exercise programme.",
            "Monitor blood pressure and cholesterol levels regularly.",
            "Avoid smoking, alcohol, and high-stress environments.",
            "Take prescribed medications (statins, beta-blockers) consistently.",
        ],
        "negative": [
            "Maintain a balanced diet rich in fruits, vegetables, and whole grains.",
            "Exercise at least 150 minutes of moderate activity per week.",
            "Schedule an annual cardiovascular check-up.",
            "Monitor blood pressure and cholesterol every 6 months.",
            "Avoid smoking and limit alcohol consumption.",
            "Manage stress through meditation, yoga, or relaxation techniques.",
        ],
    },
    "Diabetes": {
        "positive": [
            "Consult an endocrinologist for a comprehensive diabetes evaluation.",
            "Monitor fasting blood glucose and HbA1c levels regularly.",
            "Adopt a low-glycaemic, high-fibre diet; reduce refined carbohydrates.",
            "Begin a structured physical activity programme to improve insulin sensitivity.",
            "Take prescribed diabetes medications or insulin as directed.",
            "Monitor feet daily for sores or infections (neuropathy risk).",
            "Schedule annual eye and kidney function examinations.",
        ],
        "negative": [
            "Maintain a healthy weight — BMI between 18.5 and 24.9.",
            "Limit sugar and refined carbohydrates in your diet.",
            "Exercise regularly to maintain insulin sensitivity.",
            "Get a fasting blood glucose test annually.",
            "Discuss diabetes screening with your doctor if you have a family history.",
            "Avoid processed foods and sweetened beverages.",
        ],
    },
    "Breast Cancer": {
        "positive": [
            "Seek immediate consultation with an oncologist for staging and biopsy.",
            "Discuss treatment options: surgery, radiation, chemotherapy, hormone therapy.",
            "Get a second opinion from a cancer centre if possible.",
            "Join a breast cancer support group for emotional and practical guidance.",
            "Genetic counselling (BRCA1/BRCA2 testing) is recommended.",
            "Maintain a nutritious diet and keep active during treatment.",
            "Follow up with mammography and imaging as recommended.",
        ],
        "negative": [
            "Perform a monthly breast self-examination to detect any changes.",
            "Schedule mammography as per your age and risk profile guidelines.",
            "Maintain a healthy weight and limit alcohol consumption.",
            "Breastfeed if possible — it reduces breast cancer risk.",
            "Discuss hormone replacement therapy risks with your doctor.",
            "Report any lumps, nipple discharge, or skin changes promptly.",
        ],
    },
    "Parkinson's Disease": {
        "positive": [
            "Consult a neurologist specialising in movement disorders immediately.",
            "Begin medications (levodopa/carbidopa) as prescribed — early treatment is key.",
            "Engage in physical therapy to maintain balance and mobility.",
            "Consider speech therapy if swallowing or speech difficulties arise.",
            "Join a Parkinson's support group for coping strategies.",
            "Make home safety modifications to prevent falls.",
            "Explore deep brain stimulation (DBS) eligibility with your neurologist.",
        ],
        "negative": [
            "Maintain regular aerobic exercise — it supports brain health.",
            "Follow a Mediterranean diet rich in antioxidants.",
            "Avoid exposure to pesticides and environmental toxins.",
            "Monitor for early signs: tremor, rigidity, slow movement.",
            "Schedule a neurological evaluation if any symptoms develop.",
            "Stay mentally active with puzzles, reading, and social engagement.",
        ],
    },
    "Kidney Disease": {
        "positive": [
            "Consult a nephrologist for GFR staging and treatment planning.",
            "Restrict sodium, potassium, and phosphorus in your diet.",
            "Monitor fluid intake and urine output daily.",
            "Control blood pressure rigorously (target below 130/80 mmHg).",
            "Manage diabetes carefully if present — it accelerates kidney damage.",
            "Avoid NSAIDs and nephrotoxic medications.",
            "Discuss dialysis or transplant planning with your care team.",
        ],
        "negative": [
            "Stay well hydrated — drink 8 to 10 glasses of water daily.",
            "Avoid excessive use of pain relievers (NSAIDs).",
            "Control blood pressure and blood sugar levels.",
            "Maintain a balanced, low-sodium diet.",
            "Get annual kidney function tests (creatinine, eGFR).",
            "Avoid smoking — it worsens kidney blood flow.",
        ],
    },
    "Liver Disease": {
        "positive": [
            "Consult a hepatologist for liver function tests and imaging.",
            "Abstain completely from alcohol — it accelerates liver damage.",
            "Follow a liver-friendly diet: low fat, high fibre, no processed foods.",
            "Monitor bilirubin, ALT, AST, and albumin levels regularly.",
            "Get vaccinated against Hepatitis A and B if not already immune.",
            "Avoid herbal supplements not approved by your doctor.",
            "Discuss antiviral therapy if hepatitis is the underlying cause.",
        ],
        "negative": [
            "Limit alcohol consumption to recommended safe levels.",
            "Maintain a healthy weight to prevent fatty liver disease.",
            "Get vaccinated against Hepatitis A and B.",
            "Avoid sharing needles or personal hygiene items.",
            "Schedule annual liver function blood tests.",
            "Eat a balanced diet and exercise regularly.",
        ],
    },
    "Lung Cancer": {
        "positive": [
            "Seek immediate evaluation by a thoracic oncologist.",
            "Low-dose CT scan and bronchoscopy will confirm staging.",
            "Discuss treatment: surgery, chemotherapy, radiation, immunotherapy.",
            "Stop smoking immediately — it significantly improves treatment outcomes.",
            "Consider pulmonary rehabilitation to maintain breathing capacity.",
            "Nutritional support is critical during cancer treatment.",
            "Explore clinical trials at cancer research centres.",
        ],
        "negative": [
            "If you smoke, quit immediately — it is the single most important step.",
            "Avoid secondhand smoke and radon gas exposure at home.",
            "Test your home for radon with a DIY kit.",
            "If you have a long smoking history, ask about annual low-dose CT screening.",
            "Wear protective masks when exposed to asbestos or chemicals.",
            "Report persistent cough, blood in sputum, or weight loss promptly.",
        ],
    },
    "Stroke Prediction": {
        "positive": [
            "Call emergency services immediately if stroke symptoms appear (FAST).",
            "Strict blood pressure control is essential — target below 130/80 mmHg.",
            "Start antiplatelet or anticoagulant therapy as prescribed.",
            "Begin a stroke rehabilitation programme (physiotherapy, speech therapy).",
            "Control atrial fibrillation with medication or procedures.",
            "Manage diabetes, cholesterol, and weight rigorously.",
            "Avoid smoking and limit alcohol consumption.",
        ],
        "negative": [
            "Control blood pressure — hypertension is the top stroke risk factor.",
            "Manage cholesterol levels through diet and medication if needed.",
            "Exercise regularly and maintain a healthy BMI.",
            "Follow the FAST acronym to recognise stroke symptoms early.",
            "If you have atrial fibrillation, ensure it is being treated.",
            "Limit alcohol and quit smoking.",
        ],
    },
    "Thyroid Disease": {
        "positive": [
            "Consult an endocrinologist for TSH, T3, T4 blood tests and ultrasound.",
            "Take thyroid hormone replacement (levothyroxine) consistently if hypothyroid.",
            "If hyperthyroid, discuss antithyroid medications, radioactive iodine, or surgery.",
            "Monitor thyroid levels every 6 to 12 months.",
            "Eat a balanced diet with adequate iodine; avoid excess iodine supplements.",
            "Watch for symptoms: fatigue, weight changes, mood swings.",
            "Regular neck self-examination to detect any swelling or nodules.",
        ],
        "negative": [
            "Ensure adequate iodine intake through diet (iodised salt, seafood).",
            "Have TSH levels tested if you experience fatigue, weight change, or mood changes.",
            "Avoid excess iodine supplements unless prescribed.",
            "If you have a family history of thyroid disease, schedule regular screenings.",
            "Maintain a healthy lifestyle with balanced nutrition and regular exercise.",
        ],
    },
    "Alzheimer's Disease": {
        "positive": [
            "Consult a neurologist or geriatrician for cognitive assessment and MRI.",
            "Early treatment with cholinesterase inhibitors may slow progression.",
            "Engage in cognitive training exercises and mentally stimulating activities.",
            "Plan for future care needs: advance directives, legal documents.",
            "Connect with the Alzheimer's Association for caregiver support resources.",
            "Maintain physical activity — it supports brain health and mood.",
            "Create a safe home environment to reduce accident risk.",
        ],
        "negative": [
            "Stay mentally active: read, learn new skills, solve puzzles.",
            "Exercise regularly — aerobic activity promotes neuroplasticity.",
            "Maintain a Mediterranean or MIND diet for brain health.",
            "Sleep 7 to 9 hours per night — poor sleep increases amyloid buildup.",
            "Control cardiovascular risk factors (blood pressure, diabetes, cholesterol).",
            "Stay socially engaged — social activity protects cognitive function.",
            "Report any memory concerns or cognitive changes to your doctor early.",
        ],
    },
}

_DEFAULT_RECS = {
    "positive": [
        "Consult a qualified medical professional for a thorough evaluation.",
        "Follow prescribed treatment protocols and medication schedules.",
        "Monitor relevant biomarkers regularly as advised by your doctor.",
        "Adopt a healthy lifestyle: balanced diet and regular physical exercise.",
        "Attend all scheduled follow-up appointments without delay.",
    ],
    "negative": [
        "Maintain regular health check-ups with your doctor.",
        "Follow a balanced diet and engage in regular physical activity.",
        "Monitor for any new or changing symptoms.",
        "Report any health concerns to your healthcare provider promptly.",
    ],
}


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_risk_level(is_positive: bool, confidence: float) -> str:
    """Return risk level string matching result.html Jinja2 logic."""
    if is_positive:
        if confidence >= 85:
            return "High"
        elif confidence >= 65:
            return "Moderate"
        else:
            return "Low-Moderate"
    else:
        if confidence >= 85:
            return "Very Low"
        elif confidence >= 65:
            return "Low"
        else:
            return "Low-Moderate"


def get_recommendations(disease_name: str, is_positive: bool) -> list:
    """Pick the correct rec list for the disease and prediction."""
    bucket = RECOMMENDATIONS.get(disease_name, _DEFAULT_RECS)
    key    = "positive" if is_positive else "negative"
    return bucket.get(key, _DEFAULT_RECS[key])


def generate_report_id() -> str:
    """Return e.g. DTA-20240615-8F3A"""
    date_part = datetime.now().strftime("%Y%m%d")
    uid_part  = uuid.uuid4().hex[:4].upper()
    return f"DTA-{date_part}-{uid_part}"


def get_timestamp() -> str:
    """Return e.g. 15 Jun 2024, 14:32 IST"""
    return datetime.now().strftime("%d %b %Y, %H:%M IST")


def html_to_pdf(html_string: str) -> bytes | None:
    """
    Convert an HTML string to PDF bytes using xhtml2pdf.
    Returns None if conversion fails or library is unavailable.

    xhtml2pdf notes:
      - Pure Python — no system packages needed on Windows.
      - Supports most CSS2.1 and basic CSS3.
      - External Google Fonts are fetched at render time
        (internet connection required during PDF generation).
      - For offline use, switch report.html fonts to web-safe
        fonts (Arial, Georgia) and remove the Google Fonts link.
    """
    if not PDF_OK:
        return None

    try:
        pdf_buffer = io.BytesIO()
        result = pisa.CreatePDF(
            io.StringIO(html_string),   # HTML source
            dest=pdf_buffer,            # output buffer
            encoding="utf-8",
        )
        if result.err:
            app.logger.error(
                "xhtml2pdf conversion errors: %s", result.err
            )
            return None
        return pdf_buffer.getvalue()

    except Exception as exc:
        app.logger.error("PDF generation exception: %s", exc)
        return None


# ═══════════════════════════════════════════════════════════════
# ORIGINAL ROUTES  (preserved exactly — zero changes)
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def home():
    return "DiagnosTenAI Running Successfully"

@app.route("/disease/<disease_key>")
def disease_page(disease_key):

    if disease_key not in DISEASES:
        return "Disease not found", 404

    model_data = joblib.load(
        DISEASES[disease_key]["model"]
    )

    columns = model_data["columns"]

    return render_template(
        "disease.html",
        disease=DISEASES[disease_key],
        disease_key=disease_key,
        columns=columns
    )


@app.route("/predict/<disease_key>", methods=["POST"])
def predict(disease_key):

    if disease_key not in DISEASES:
        return "Disease not found", 404

    model_data = joblib.load(
        DISEASES[disease_key]["model"]
    )

    model = model_data["model"]

    values = []

    for column in model_data["columns"]:

        value = request.form.get(column)

        try:
            value = float(value)
        except Exception:
            value = 0

        values.append(value)

    prediction = model.predict([values])[0]

    # Fix Heart Dataset Labels
    if disease_key == "heart":
        prediction = 1 - prediction

    if disease_key == "kidney":
        prediction = 1 - prediction

    if disease_key == "liver":
        prediction = 1 - prediction

    confidence = round(
        max(model.predict_proba([values])[0]) * 100,
        2
    )

    return render_template(
        "result.html",
        disease=DISEASES[disease_key]["name"],
        prediction=prediction,
        confidence=confidence
    )


# ═══════════════════════════════════════════════════════════════
# /report — browser HTML preview
# ═══════════════════════════════════════════════════════════════

@app.route("/report", methods=["GET", "POST"])
def report_preview():
    """
    Browser-readable preview of report.html.
    GET  → demo/test layout with placeholder values.
    POST → full populated report from result.html form data.
    """
    if request.method == "POST":
        disease      = request.form.get("disease",       "Unknown Disease")
        prediction   = int(request.form.get("prediction",   0))
        confidence   = float(request.form.get("confidence",  0.0))
        risk_level   = request.form.get("risk_level",    "Unknown")
        result_label = request.form.get("result_label",  "Unknown")
    else:
        disease      = "Heart Disease"
        prediction   = 1
        confidence   = 87.50
        risk_level   = "High"
        result_label = "Positive"

    is_positive     = prediction != 0
    recommendations = get_recommendations(disease, is_positive)

    return render_template(
        "report.html",
        disease=disease,
        prediction=prediction,
        confidence=confidence,
        risk_level=risk_level,
        result_label=result_label,
        recommendations=recommendations,
        report_id=generate_report_id(),
        timestamp=get_timestamp(),
    )


# ═══════════════════════════════════════════════════════════════
# /download_report — PDF binary response  (File 7)
# ═══════════════════════════════════════════════════════════════

@app.route("/download_report", methods=["POST"])
def download_report():
    """
    1. Reads form fields from result.html Download PDF button.
    2. Renders report.html → HTML string via Jinja2.
    3. Converts HTML → PDF bytes via xhtml2pdf (pure Python).
    4. Streams PDF as a file download.

    Fallback: if xhtml2pdf is unavailable or fails, returns the
    HTML report page so the user can browser-print to PDF.
    """

    # ── Read POST fields sent by result.html ─────────────────
    disease      = request.form.get("disease",       "Unknown Disease")
    prediction   = int(request.form.get("prediction",   0))
    confidence   = float(request.form.get("confidence",  0.0))
    risk_level   = request.form.get("risk_level",    "Unknown")
    result_label = request.form.get("result_label",  "Unknown")

    is_positive     = prediction != 0
    recommendations = get_recommendations(disease, is_positive)
    report_id       = generate_report_id()
    timestamp       = get_timestamp()

    # ── Render report.html to HTML string ────────────────────
    html_string = render_template(
        "report.html",
        disease=disease,
        prediction=prediction,
        confidence=confidence,
        risk_level=risk_level,
        result_label=result_label,
        recommendations=recommendations,
        report_id=report_id,
        timestamp=timestamp,
    )

    # ── Convert to PDF ────────────────────────────────────────
    pdf_bytes = html_to_pdf(html_string)

    if pdf_bytes:
        # Success — stream PDF file to browser
        safe_name = (
            disease.lower()
                   .replace(" ", "_")
                   .replace("'", "")
                   .replace(".", "")
        )
        filename = f"{safe_name}_report_{report_id}.pdf"

        response = make_response(pdf_bytes)
        response.headers["Content-Type"]        = "application/pdf"
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        return response

    # ── Fallback — serve HTML for browser print-to-PDF ───────
    app.logger.warning(
        "PDF generation failed or xhtml2pdf not installed. "
        "Serving HTML preview for browser print."
    )
    html_response = make_response(html_string, 200)
    html_response.headers["Content-Type"]    = "text/html; charset=utf-8"
    html_response.headers["X-PDF-Fallback"] = "true"
    return html_response


# ═══════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)