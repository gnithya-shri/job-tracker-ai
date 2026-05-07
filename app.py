import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ---------- SKILLS ----------
SKILLS = [
    "python", "java", "sql", "html", "css",
    "javascript", "react", "flask", "django",
    "mongodb", "mysql", "git"
]

def extract_skills(text):
    text = text.lower()
    found = []
    for skill in SKILLS:
        if skill in text:
            found.append(skill)
    return list(set(found))

# ---------- ROUTES ----------
@app.route('/')
def home():
    return "Job Tracker Backend Running"

@app.route('/add-job', methods=['POST'])
def add_job():
    data = request.get_json()
    
    company = data.get('company')
    role = data.get('role')
    status = data.get('status')

    if not company or not role or not status:
        return jsonify({"message": "Invalid data"}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO jobs (company, role, status) VALUES (?, ?, ?)",
        (company, role, status)
    )
    
    conn.commit()
    conn.close()

    return jsonify({"message": "Job added successfully"})

@app.route('/get-jobs', methods=['GET'])
def get_jobs():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    
    conn.close()

    job_list = []
    for job in jobs:
        job_list.append({
            "id": job[0],
            "company": job[1],
            "role": job[2],
            "status": job[3]
        })

    return jsonify(job_list)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()

    resume = data.get('resume', "")
    job_desc = data.get('job_desc', "")

    resume_skills = set(extract_skills(resume))
    job_skills = set(extract_skills(job_desc))

    if len(job_skills) == 0:
        return jsonify({"match": 0, "missing": []})

    match = len(resume_skills & job_skills) / len(job_skills) * 100
    missing = list(job_skills - resume_skills)

    return jsonify({
        "match": round(match, 2),
        "missing": missing
    })

if __name__ == '__main__':
    app.run(debug=True)