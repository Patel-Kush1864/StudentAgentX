import ollama

def recommend_internships(skills, projects, interests):
    """
    Suggests internship pathways, application guidelines, and development roadmaps
    based on student profile details.
    Yields chunks of the recommendation response.
    """
    prompt = f"""
You are a Career Placement Officer. Recommend matching internship roles and strategies.

Student Background:
- Skills: {skills}
- Projects: {projects}
- Interests/Preferences: {interests}

Analyze these details and recommend relevant positions within Web Development, AI/ML, Blockchain, or Full Stack.
Your response must include:
1. **Recommended Internship Roles**: At least 3 specific internship positions matching their profile.
2. **Profile Fit Analysis**: Logical reasoning for why these roles fit their current skills.
3. **Upskilling Checklist**: Key technologies, APIs, or tools they need to study to qualify.
4. **Resume Action Plan**: Recommended next steps to attract technical recruiters (e.g., specific project types to build).
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
        yield f"Error recommendations: {e}\nPlease check if Ollama is running and has llama3 installed."
