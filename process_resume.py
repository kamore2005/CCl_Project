import fitz  # PyMuPDF
import spacy
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Predefined skills list
SKILL_SET = {"python", "java", "machine learning", "sql", "flask", "react", "html", "css", "docker", "aws","kubernetes", "nlp", "deep learning", "data analysis", "javascript", "c++", "c#", "ruby", "php", "swift", "typescript", "go", "scala", "rust", "matlab", "r", "sas", "hadoop", "spark", "tableau", "powerbi","excel", "git", "github", "jenkins", "ansible", "terraform", "linux", "unix", "windows", "networking", "cybersecurity", "penetration testing", "ethical hacking", "cloud computing", "devops"}

def extract_text_from_pdf(pdf_path):
    """Extract text from a given PDF file."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.lower()

def extract_skills(text):
    """Extract skills from text using spaCy NLP."""
    doc = nlp(text)
    extracted_skills = {token.text.lower() for token in doc if token.text.lower() in SKILL_SET}
    return extracted_skills

def process_resumes(resume_folder, job_desc_path):
    """Process all resumes and rank them based on skill match & similarity to JD."""
    job_description = open(job_desc_path, "r").read().lower()
    
    resume_scores = []
    for resume_file in os.listdir(resume_folder):
        if resume_file.endswith(".pdf"):
            resume_path = os.path.join(resume_folder, resume_file)
            resume_text = extract_text_from_pdf(resume_path)
            resume_skills = extract_skills(resume_text)

            # Compute similarity score
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
            similarity_score = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

            score = len(resume_skills) + (similarity_score * 10)
            resume_scores.append((resume_file, score, list(resume_skills)))
    
    # Rank resumes based on scores
    resume_scores.sort(key=lambda x: x[1], reverse=True)
    return resume_scores
