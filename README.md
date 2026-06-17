# Autonomous Student Success AI Agent

The **Autonomous Student Success AI Agent** is a production-quality, local web application designed to help students track performance, manage deadlines, generate exam study notes and resumes, receive AI-matched career recommendations, and run machine learning models to predict final exam scores.

It operates fully offline using **Flask**, **SQLite**, **Bootstrap 5**, **Scikit-learn**, **ReportLab**, and **Ollama (Llama3)**.

---

## Key Features

1. **Autonomous Master Agent & Chat**:
   - Zero-shot classification routes queries to specialized sub-agents.
   - Provides contextual recommendations by reading task and attendance records in real-time.

2. **Smart Task Management**:
   - Autocalculates days remaining and priority level (High/Medium/Low).
   - Generates dashboard deadline alerts for tasks due within 48 hours.

3. **Attendance Risk Management**:
   - Computes percentages and highlights subjects below the 75% limit.
   - Proactively predicts future shortages (if you skip the next 3 classes).
   - Calculates consecutive lectures needed to recover.

4. **AI Exam Notes Generator**:
   - Generates notes structured into: *Introduction*, *Concept*, *Working*, *Advantages*, *Disadvantages*, and *Conclusion*.
   - Exporter compiles study notes into a professionally structured PDF document.

5. **AI Study Planner**:
   - Creates a personalized, hour-wise calendar schedule based on tasks and exam dates.

6. **AI Resume Builder & PDF Exporter**:
   - Refines raw input details into impact-driven bullet points using the STAR method.
   - Exports the polished single-page resume to PDF.

7. **AI Internship Recommendations**:
   - Tailors placement suggestions (Web Dev, AI/ML, Blockchain, Full Stack) based on skills, projects, and career interests.

8. **ML Exam Score Predictor**:
   - Uses a Scikit-learn Linear Regression model trained on local synthetic data.
   - Evaluates attendance, daily study hours, and internal marks to predict final exam grades.

---

## File Structure

```text
student_ai_agent/
│
├── app.py                      # Flask routing & application controllers
├── student.db                  # Local SQLite database
├── requirements.txt            # Python dependencies
├── README.md                   # Setup guidelines
│
├── database/
│   └── db_helper.py            # SQLite schema initialization and seeding
│
├── models/
│   └── ml_model.py             # Scikit-learn Linear Regression Marks Predictor
│
├── agents/
│   ├── master_agent.py         # Intent classifier and router agent
│   ├── task_agent.py           # Countdown and prioritization agent
│   ├── attendance_agent.py     # Attendance analysis agent
│   ├── notes_agent.py          # Exam notes generation agent
│   ├── study_planner_agent.py    # Study schedule planner agent
│   ├── resume_agent.py         # Resume builder polisher agent
│   └── internship_agent.py     # Recruiter match career agent
│
├── services/
│   └── pdf_generator.py        # ReportLab PDF compile pipeline
│
├── templates/                  # Jinja2 HTML layout views
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── tasks.html
│   ├── attendance.html
│   ├── notes.html
│   ├── study_planner.html
│   ├── resume_builder.html
│   ├── marks_predictor.html
│   ├── profile.html
│   └── chat.html
│
└── static/                     # Assets
    ├── css/
    │   └── style.css           # Premium Glassmorphism Dark Theme
    └── js/
        └── main.js             # Chat AJAX integrations
```

---

## Setup & Running Guide

### 1. Prerequisites
- **Python 3.9+** installed.
- **Ollama** installed locally. (Make sure you have pulled `llama3`: `ollama run llama3`).

### 2. Install Dependencies
Install all required libraries using pip:
```bash
pip install -r requirements.txt
```

### 3. Initialize & Run
Start the web application:
```bash
python app.py
```
This will automatically:
1. Initialize the SQLite database `student.db`.
2. Seed mock student data for instant testing.
3. Train the Scikit-learn marks predictor model in memory.
4. Launch the local server on `http://127.0.0.1:5000`.

---

## Credentials for Testing
You can sign up for a new account, or use the pre-seeded student account:
- **Email**: `user@example.com`
- **Password**: `password123`
