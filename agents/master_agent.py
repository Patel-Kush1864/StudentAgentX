import ollama
from .task_agent import calculate_days_remaining, get_urgent_tasks
from .attendance_agent import analyze_attendance
from .notes_agent import generate_exam_notes
from .study_planner_agent import generate_custom_study_plan
from .resume_agent import build_resume_content
from .internship_agent import recommend_internships

def classify_user_request(query):
    """
    Uses Llama3 to classify the user's intent into one of seven domains.
    Returns the classification keyword.
    """
    prompt = f"""
You are the Master Agent of a Student Success AI system.
Your job is to classify the user's message into one of the following exact categories.

Categories:
- 'task': Questions about tasks, deadlines, prioritizing homework, or completing assignments.
- 'attendance': Questions about class attendance, percentage calculations, or lecture shortages.
- 'notes': Requests to generate study notes, explain a concept, or teach a topic.
- 'study_plan': Requests for a daily study planner, schedule, or calendar.
- 'resume': Questions or requests to build, write, or review a resume.
- 'internship': Queries about finding an internship, jobs, or career advice.
- 'chat': General conversation, greetings, or other student life advice.

User Message: "{query}"

Respond with ONLY the category keyword inside single quotes, e.g., 'task' or 'chat'. Do not explain or include any other text.
"""
    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0}
        )
        content = response["message"]["content"].strip().lower()
        for cat in ['task', 'attendance', 'notes', 'study_plan', 'resume', 'internship', 'chat']:
            if cat in content:
                return cat
        return 'chat'
    except Exception:
        return 'chat'

def handle_autonomous_query(query, tasks_context, attendance_context):
    """
    Classifies the user query and routes execution to the correct sub-agent,
    passing database context elements to formulate personalized responses.
    """
    category = classify_user_request(query)
    pending_tasks = [t for t in tasks_context if t.get("status") == "Pending"]
    
    if category == 'task':
        prompt = f"""
The user is asking about their tasks.
User Query: "{query}"

Here is their current pending tasks list from the database:
{pending_tasks}

Please answer the user's question. If they ask to prioritize, act as a Prioritization Agent and provide:
1. Priority Order
2. Reasoning
3. Suggested Sequence
"""
        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}], stream=True)
            for chunk in response:
                yield chunk["message"]["content"]
        except Exception as e:
            yield f"Error handling tasks: {e}"
            
    elif category == 'attendance':
        analysis = analyze_attendance(attendance_context)
        prompt = f"""
The user is asking about their class attendance.
User Query: "{query}"

Here is their current attendance analysis from the database:
{analysis['analysis']}

Please summarize their attendance situation. Highlight subjects below 75%, predict shortage risk if they miss lectures, and suggest consecutive recovery strategy.
"""
        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}], stream=True)
            for chunk in response:
                yield chunk["message"]["content"]
        except Exception as e:
            yield f"Error handling attendance: {e}"

    elif category == 'notes':
        # Strip some common notes generation request keywords to get a cleaner topic
        cleaned = query.lower()
        for phrase in ["generate notes for", "notes on", "write notes about", "explain"]:
            if phrase in cleaned:
                cleaned = cleaned.replace(phrase, "")
        topic = cleaned.strip().capitalize()
        yield from generate_exam_notes(topic)
        
    elif category == 'study_plan':
        yield from generate_custom_study_plan(pending_tasks, attendance_context, "Upcoming Exams next week")
        
    elif category == 'resume':
        prompt = f"""
The user wants guidance on their resume or wants to build one.
User Query: "{query}"

Provide career guidance on how to structure a resume, or explain how to use the Student success resume builder tool in this portal to compile a professional PDF.
"""
        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}], stream=True)
            for chunk in response:
                yield chunk["message"]["content"]
        except Exception as e:
            yield f"Error handling resume: {e}"

    elif category == 'internship':
        prompt = f"""
The user is asking for career or internship recommendations.
User Query: "{query}"

Provide tailored guidance or suggest internship paths matching Web Development, AI/ML, Blockchain, or Full Stack based on typical academic student profiles.
"""
        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}], stream=True)
            for chunk in response:
                yield chunk["message"]["content"]
        except Exception as e:
            yield f"Error handling career advice: {e}"

    else:
        prompt = f"""
You are the Autonomous Student Success AI Chat Assistant.
User Query: "{query}"

Provide a friendly, helpful response supporting their student life. Mention that you have access to their tasks and attendance, and can generate study plans, notes, or resume files if requested.
"""
        try:
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}], stream=True)
            for chunk in response:
                yield chunk["message"]["content"]
        except Exception as e:
            yield f"Error handling conversation: {e}"
