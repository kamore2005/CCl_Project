import os
import re
import PyPDF2
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt

# Firebase Setup
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")  # Your Firebase key
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Can be changed for production

# ------------------ SKILL SETS ------------------

TECHNICAL_SKILLS_SET = {
    "python", "java", "sql", "react", "nlp", "flask", "aws", "docker", "kubernetes",
    "machine learning", "deep learning", "data analysis", "html", "css", "javascript",
    "c++", "c#", "ruby", "php", "swift", "typescript", "go", "scala", "rust", "matlab",
    "r", "sas", "hadoop", "spark", "tableau", "powerbi", "excel", "git", "github",
    "jenkins", "ansible", "terraform", "linux", "unix", "windows", "networking",
    "cybersecurity", "penetration testing", "ethical hacking", "cloud computing",
    "devops", "agile", "scrum", "project management", "business analysis"
}

SOFT_SKILLS_SET = {
    "communication", "leadership", "teamwork", "problem-solving", "adaptability",
    "time management", "critical thinking", "creativity", "interpersonal skills",
    "emotional intelligence", "conflict resolution", "negotiation", "presentation skills",
    "active listening", "collaboration", "decision making", "work ethic", "positive attitude",
    "flexibility", "self-motivation", "stress management", "organizational skills",
    "customer service", "empathy", "cultural awareness", "networking", "relationship building",
    "influence", "persuasion", "mentoring", "coaching", "public speaking", "writing skills",
    "research skills", "analytical skills", "attention to detail", "initiative", "self-awareness",
    "self-regulation", "social skills", "resilience"
}

# ------------------ PDF & SKILL LOGIC ------------------

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text.lower()

def extract_skills(text):
    words = set(text.split())
    technical_skills = words.intersection(TECHNICAL_SKILLS_SET)
    soft_skills = words.intersection(SOFT_SKILLS_SET)
    return list(technical_skills), list(soft_skills)

def extract_name(text):
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if len(line) > 1 and len(line.split()) >= 2:
            if re.match(r"^[A-Za-z\s]+$", line):
                return line
    return "Unknown"

# ------------------ AUTH ROUTES ------------------

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    doc_ref = db.collection("users").document(username)
    doc = doc_ref.get()

    if doc.exists:
        user_data = doc.to_dict()
        if bcrypt.check_password_hash(user_data['password'], password):
            session['username'] = username
            return redirect(url_for("dashboard"))

    return "Invalid Credentials! Try Again."

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template("upload.html", username=session['username'])
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))

# ------------------ RESUME SCORING ------------------

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return "No file part", 400

    files = request.files.getlist('files')
    resumes_data = []

    for file in files:
        if file.filename == '' or not file.filename.endswith('.pdf'):
            continue

        text = extract_text_from_pdf(file)
        name = extract_name(text)
        technical_skills, soft_skills = extract_skills(text)
        score = len(technical_skills) + len(soft_skills)

        resumes_data.append({
            "name": name,
            "filename": file.filename,
            "score": score,
            "technical_skills": ", ".join(technical_skills) or "No technical skills found",
            "soft_skills": ", ".join(soft_skills) or "No soft skills found"
        })

    resumes_data.sort(key=lambda x: x["score"], reverse=True)
    return render_template("result.html", resumes=resumes_data)

# ------------------ MAIN ------------------

if __name__ == '__main__':
    app.run(debug=True)
