# app.py
from flask import Flask, render_template, request
import os
import PyPDF2
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'resumes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def calculate_ats_score(resume_text, job_description):
    # Lowercase and tokenize
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    job_words = set(re.findall(r'\b\w+\b', job_description.lower()))

    # Keyword overlap
    matched_keywords = resume_words & job_words
    score = (len(matched_keywords) / len(job_words)) * 100 if job_words else 0
    return round(score, 2), matched_keywords

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    job_desc = request.form['job_desc']
    resume = request.files['resume']

    if resume:
        filepath = os.path.join(UPLOAD_FOLDER, resume.filename)
        resume.save(filepath)

        if filepath.endswith('.pdf'):
            resume_text = extract_text_from_pdf(filepath)
        else:
            resume_text = resume.read().decode('utf-8', errors='ignore')

        score, matched = calculate_ats_score(resume_text, job_desc)
        return f"""
        <h2>Thanks, {name}!</h2>
        <p>Your ATS score is: <strong>{score}%</strong></p>
        <p>Matched Keywords: {', '.join(matched)}</p>
        """
    return "Error: Resume not found."

if __name__ == '__main__':
    app.run(debug=True)
