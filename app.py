import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash

# Custom Modules
from database.db_helper import get_db_connection, init_db
from models.ml_model import train_predictor_model, predict_score
from agents.task_agent import calculate_days_remaining, auto_calculate_priority, get_urgent_tasks
from agents.attendance_agent import analyze_attendance
from agents.notes_agent import generate_exam_notes
from agents.study_planner_agent import generate_custom_study_plan
from agents.resume_agent import build_resume_content
from agents.internship_agent import recommend_internships
from agents.master_agent import handle_autonomous_query
from services.pdf_generator import generate_notes_pdf, generate_resume_pdf

app = Flask(__name__)
app.secret_key = "autonomous_student_success_secret_key"

# Initialize SQLite database and ML prediction model on application start
init_db()
train_predictor_model()

# Login Decorator to protect secure views
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Context processor to expose variables to template views
@app.context_processor
def inject_active_page():
    return dict(active_page=None)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_created_at'] = user['created_at']
            flash("Successfully signed in!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email address or password.", "error")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not name or not email or not password:
            flash("All registration fields are required.", "error")
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error registering: Email might already be in use.", "error")
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Successfully signed out.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    attendance = conn.execute("SELECT * FROM attendance WHERE user_id = ?", (user_id,)).fetchall()
    
    predicted_marks = session.get('predicted_marks', None)
    conn.close()
    
    total_tasks = len(tasks)
    pending_tasks = sum(1 for t in tasks if t['status'] == 'Pending')
    
    total_classes = sum(a['total'] for a in attendance)
    total_attended = sum(a['attended'] for a in attendance)
    avg_attendance = (total_attended / total_classes * 100) if total_classes > 0 else 0.0
    
    # Run Attendance Risk Agent calculations
    analysis_data = analyze_attendance([dict(a) for a in attendance])
    low_subs = analysis_data['low_subjects']
    
    # Process Tasks dead-lines countdown & urgent list
    tasks_with_remaining = []
    urgent_tasks = []
    for t in tasks:
        td = dict(t)
        days = calculate_days_remaining(t['deadline'])
        td['days_remaining'] = days
        tasks_with_remaining.append(td)
        if t['status'] == 'Pending' and days <= 2:
            urgent_tasks.append(td)
            
    return render_template(
        'dashboard.html',
        active_page='dashboard',
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        avg_attendance=avg_attendance,
        predicted_marks=predicted_marks,
        urgent_tasks_count=len(urgent_tasks),
        urgent_tasks=urgent_tasks,
        low_attendance_subjects=low_subs
    )

@app.route('/tasks')
@login_required
def tasks():
    user_id = session['user_id']
    conn = get_db_connection()
    tasks_rows = conn.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY status DESC, id DESC", (user_id,)).fetchall()
    conn.close()
    
    tasks = []
    for r in tasks_rows:
        td = dict(r)
        td['days_remaining'] = calculate_days_remaining(r['deadline'])
        tasks.append(td)
        
    return render_template('tasks.html', active_page='tasks', tasks=tasks)

@app.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    user_id = session['user_id']
    task_name = request.form.get('task_name', '').strip()
    deadline = request.form.get('deadline', '').strip()
    
    if not task_name or not deadline:
        flash("Task name and deadline are required.", "error")
        return redirect(url_for('tasks'))
        
    # Smart task management: Auto-calculate remaining days and priority level
    days = calculate_days_remaining(deadline)
    priority = auto_calculate_priority(days)
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (user_id, task_name, deadline, status, priority) VALUES (?, ?, ?, 'Pending', ?)",
        (user_id, task_name, deadline, priority)
    )
    conn.commit()
    conn.close()
    
    flash("Task successfully added!", "success")
    return redirect(url_for('tasks'))

@app.route('/tasks/complete/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    conn.commit()
    conn.close()
    flash("Task marked as completed!", "success")
    return redirect(url_for('tasks'))

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()
    flash("Task deleted successfully.", "success")
    return redirect(url_for('tasks'))

@app.route('/attendance')
@login_required
def attendance():
    user_id = session['user_id']
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM attendance WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    
    analysis_data = analyze_attendance([dict(r) for r in records])
    return render_template('attendance.html', active_page='attendance', attendance=analysis_data['analysis'])

@app.route('/attendance/add', methods=['POST'])
@login_required
def add_attendance():
    user_id = session['user_id']
    subject_name = request.form.get('subject_name', '').strip()
    attended = int(request.form.get('attended', 0))
    total = int(request.form.get('total', 0))
    
    if not subject_name or total < 0 or attended < 0 or attended > total:
        flash("Please enter valid subject and lecture counts.", "error")
        return redirect(url_for('attendance'))
        
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO attendance (user_id, subject_name, attended, total) VALUES (?, ?, ?, ?)",
        (user_id, subject_name, attended, total)
    )
    conn.commit()
    conn.close()
    
    flash("Subject added to tracker!", "success")
    return redirect(url_for('attendance'))

@app.route('/attendance/log/<int:attendance_id>/<string:type>', methods=['POST'])
@login_required
def log_lecture(attendance_id, type):
    user_id = session['user_id']
    conn = get_db_connection()
    record = conn.execute("SELECT * FROM attendance WHERE id = ? AND user_id = ?", (attendance_id, user_id)).fetchone()
    
    if not record:
        conn.close()
        flash("Record not found.", "error")
        return redirect(url_for('attendance'))
        
    attended = record['attended']
    total = record['total']
    
    if type == 'attend':
        attended += 1
        total += 1
    elif type == 'absent':
        total += 1
        
    conn.execute(
        "UPDATE attendance SET attended = ?, total = ? WHERE id = ? AND user_id = ?",
        (attended, total, attendance_id, user_id)
    )
    conn.commit()
    conn.close()
    flash(f"Logged lecture as {'Present' if type == 'attend' else 'Absent'}.", "success")
    return redirect(url_for('attendance'))

@app.route('/attendance/delete/<int:attendance_id>', methods=['POST'])
@login_required
def delete_attendance(attendance_id):
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute("DELETE FROM attendance WHERE id = ? AND user_id = ?", (attendance_id, user_id))
    conn.commit()
    conn.close()
    flash("Subject tracker deleted.", "success")
    return redirect(url_for('attendance'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', active_page='chat')

@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    user_id = session['user_id']
    data = request.get_json()
    query = data.get('message', '').strip()
    
    if not query:
        return jsonify({"status": "error", "message": "Query cannot be empty"})
        
    # Gather context from SQLite
    conn = get_db_connection()
    tasks_rows = conn.execute("SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    attendance_rows = conn.execute("SELECT * FROM attendance WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    
    tasks_context = [dict(t) for t in tasks_rows]
    attendance_context = [dict(a) for a in attendance_rows]
    
    # Process through Master Agent
    try:
        reply_generator = handle_autonomous_query(query, tasks_context, attendance_context)
        reply = "".join(reply_generator)
        return jsonify({"status": "success", "reply": reply})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/notes')
@login_required
def notes():
    user_id = session['user_id']
    conn = get_db_connection()
    notes_history = conn.execute("SELECT id, topic FROM notes WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    
    view_id = request.args.get('view_id')
    active_notes = None
    if view_id:
        active_notes = conn.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", (view_id, user_id)).fetchone()
    elif notes_history:
        active_notes = conn.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", (notes_history[0]['id'], user_id)).fetchone()
        
    conn.close()
    return render_template('notes.html', active_page='notes', notes_history=notes_history, active_notes=active_notes)

@app.route('/notes/generate', methods=['POST'])
@login_required
def generate_notes_route():
    user_id = session['user_id']
    topic = request.form.get('topic', '').strip()
    
    if not topic:
        flash("Please input a valid topic.", "error")
        return redirect(url_for('notes'))
        
    # Call Notes generation agent
    notes_generator = generate_exam_notes(topic)
    notes_content = "".join(notes_generator)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (user_id, topic, generated_notes) VALUES (?, ?, ?)",
        (user_id, topic, notes_content)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    flash(f"Exam notes for '{topic}' generated successfully!", "success")
    return redirect(url_for('notes') + f"?view_id={new_id}")

@app.route('/notes/export/<int:notes_id>')
@login_required
def export_notes_pdf(notes_id):
    user_id = session['user_id']
    conn = get_db_connection()
    note = conn.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", (notes_id, user_id)).fetchone()
    conn.close()
    
    if not note:
        flash("Notes record not found.", "error")
        return redirect(url_for('notes'))
        
    pdf_buffer = generate_notes_pdf(note['topic'], note['generated_notes'])
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{note['topic'].replace(' ', '_')}_notes.pdf",
        mimetype='application/pdf'
    )

@app.route('/study-planner')
@login_required
def study_planner():
    user_id = session['user_id']
    conn = get_db_connection()
    active_plan = conn.execute("SELECT * FROM study_plans WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    return render_template('study_planner.html', active_page='study_planner', active_plan=active_plan)

@app.route('/study-planner/generate', methods=['POST'])
@login_required
def generate_study_plan_route():
    user_id = session['user_id']
    exam_dates = request.form.get('exam_dates', '').strip()
    
    if not exam_dates:
        flash("Please input exam details.", "error")
        return redirect(url_for('study_planner'))
        
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE user_id = ? AND status = 'Pending'", (user_id,)).fetchall()
    attendance = conn.execute("SELECT * FROM attendance WHERE user_id = ?", (user_id,)).fetchall()
    
    tasks_context = [dict(t) for t in tasks]
    attendance_context = [dict(a) for a in attendance]
    
    # Query study planner agent
    plan_generator = generate_custom_study_plan(tasks_context, attendance_context, exam_dates)
    plan_text = "".join(plan_generator)
    
    conn.execute(
        "INSERT INTO study_plans (user_id, plan_text) VALUES (?, ?)",
        (user_id, plan_text)
    )
    conn.commit()
    conn.close()
    
    flash("AI Study Schedule generated successfully!", "success")
    return redirect(url_for('study_planner'))

@app.route('/resume-builder')
@login_required
def resume_builder():
    user_id = session['user_id']
    conn = get_db_connection()
    resume_data = conn.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    
    active_resume = session.get('active_resume_content', None)
    return render_template('resume_builder.html', active_page='resume_builder', resume_data=resume_data, active_resume=active_resume)

@app.route('/resume-builder/build', methods=['POST'])
@login_required
def build_resume_route():
    user_id = session['user_id']
    skills = request.form.get('skills', '').strip()
    education = request.form.get('education', '').strip()
    projects = request.form.get('projects', '').strip()
    
    if not skills or not education or not projects:
        flash("All fields are required to build a resume.", "error")
        return redirect(url_for('resume_builder'))
        
    # Save parameters
    conn = get_db_connection()
    conn.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
    conn.execute(
        "INSERT INTO resumes (user_id, skills, education, projects) VALUES (?, ?, ?, ?)",
        (user_id, skills, education, projects)
    )
    conn.commit()
    conn.close()
    
    # Call AI agent to polish
    resume_generator = build_resume_content(skills, education, projects)
    resume_content = "".join(resume_generator)
    
    session['active_resume_content'] = resume_content
    flash("Resume compiled and optimized by AI!", "success")
    return redirect(url_for('resume_builder'))

@app.route('/resume-builder/export')
@login_required
def export_resume_pdf():
    user_id = session['user_id']
    conn = get_db_connection()
    resume_data = conn.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    
    ai_resume = session.get('active_resume_content', '')
    
    if not resume_data:
        flash("No resume details found.", "error")
        return redirect(url_for('resume_builder'))
        
    pdf_buffer = generate_resume_pdf(
        resume_data['skills'],
        resume_data['education'],
        resume_data['projects'],
        ai_resume
    )
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="Student_Resume.pdf",
        mimetype='application/pdf'
    )

@app.route('/marks-predictor', methods=['GET', 'POST'])
@login_required
def marks_predictor():
    prediction = session.get('last_marks_prediction', None)
    input_data = session.get('last_marks_inputs', None)
    return render_template('marks_predictor.html', active_page='marks_predictor', prediction=prediction, input_data=input_data)

@app.route('/marks-predictor/predict', methods=['POST'])
@login_required
def marks_predictor_route():
    try:
        attendance = float(request.form.get('attendance', 0.0))
        study_hours = float(request.form.get('study_hours', 0.0))
        internal_marks = float(request.form.get('internal_marks', 0.0))
        
        prediction = predict_score(attendance, study_hours, internal_marks)
        
        session['last_marks_prediction'] = prediction
        session['last_marks_inputs'] = {
            "attendance": attendance,
            "study_hours": study_hours,
            "internal_marks": internal_marks
        }
        session['predicted_marks'] = prediction
        
        flash("Exam score predicted successfully via Scikit-learn Linear Regression!", "success")
    except Exception as e:
        flash(f"Error predicting score: {e}", "error")
        
    return redirect(url_for('marks_predictor'))

@app.route('/profile')
@login_required
def profile():
    skills = session.get('profile_skills', '')
    projects = session.get('profile_projects', '')
    interests = session.get('profile_interests', '')
    recommendations = session.get('internship_recs', '')
    
    return render_template(
        'profile.html',
        active_page='profile',
        skills=skills,
        projects=projects,
        interests=interests,
        recommendations=recommendations
    )

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    session['profile_skills'] = request.form.get('skills', '').strip()
    session['profile_projects'] = request.form.get('projects', '').strip()
    session['profile_interests'] = request.form.get('interests', '').strip()
    flash("Skills and Career profile saved successfully!", "success")
    return redirect(url_for('profile'))

@app.route('/profile/match-internships', methods=['POST'])
@login_required
def match_internships():
    skills = session.get('profile_skills', '')
    projects = session.get('profile_projects', '')
    interests = session.get('profile_interests', '')
    
    if not skills or not projects:
        flash("Please set your skills and projects in your profile first.", "error")
        return redirect(url_for('profile'))
        
    rec_generator = recommend_internships(skills, projects, interests)
    recommendations = "".join(rec_generator)
    
    session['internship_recs'] = recommendations
    flash("Matched career options with AI Internship Recruiter!", "success")
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)