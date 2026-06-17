import ollama

def generate_custom_study_plan(tasks, attendance, exam_dates):
    """
    Sends student tasks, attendance records, and exam dates to Ollama Llama3.
    Yields chunks of the generated hour-wise study plan.
    """
    prompt = f"""
You are a Student Study Advisor. Generate a personalized, highly structured study plan.

Input data:
- Pending Tasks: {tasks}
- Attendance Analysis: {attendance}
- Exam Dates/Details: {exam_dates}

Your plan must be comprehensive and include:
1. **Subject Prioritization**: Which subjects need urgent attention (based on low attendance warnings or tight deadlines/exams).
2. **Hour-wise Study Schedule**: Detailed daily schedule (e.g. 09:00 - 11:00) mapping activities to specific tasks.
3. **Revision Suggestions**: Strategic tips on memory retention, revision, mock tests, and active recall.
"""
    try:
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response:
            yield chunk["message"]["content"]
    except Exception as e:
        yield f"Error generating study plan: {e}\nPlease check if Ollama is running and has llama3 installed."
