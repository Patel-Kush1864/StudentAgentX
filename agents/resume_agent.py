import ollama

def build_resume_content(skills, education, projects):
    """
    Takes student raw skills, education, and projects, and uses Llama3 to construct
    an enhanced professional resume summary and bullet points.
    Yields chunks of text.
    """
    prompt = f"""
You are an expert resume builder and technical recruiter.

Transform the following student details into an outstanding, professional, and industry-ready resume:
- Skills: {skills}
- Education: {education}
- Projects: {projects}

Please structure the response with these exact sections:
1. **Professional Summary**: A punchy, 3-sentence professional summary showing their focus.
2. **Education Details**: Polished formatting of their credentials.
3. **Core Competencies**: A categorised list of skills.
4. **Academic & Personal Projects**: Detailed descriptions using the STAR (Situation, Task, Action, Result) format with active verbs.
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
        yield f"Error building resume content: {e}\nPlease check if Ollama is running and has llama3 installed."
