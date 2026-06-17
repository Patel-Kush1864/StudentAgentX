import ollama

def generate_exam_notes(topic):
    """
    Queries Llama3 via Ollama to generate exam-ready study notes on the topic.
    Yields chunks of notes dynamically.
    """
    prompt = f"""
You are an expert academic tutor. Generate highly detailed, comprehensive, exam-ready notes for the topic: "{topic}".

Your output must follow this structure and contain these exact headings:
1. **Introduction**: Detailed introduction, definition, and high-level overview.
2. **Concept**: Explaining core theory, background, and conceptual framework.
3. **Working**: Step-by-step working, operations, architecture, or mechanical steps.
4. **Advantages**: List of pros, benefits, and positive points.
5. **Disadvantages**: List of cons, limitations, or vulnerabilities.
6. **Conclusion**: Closing summary and main takeaway.
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
        yield f"Error generating notes via Ollama: {e}\nPlease check if Ollama is running and has llama3 installed."
