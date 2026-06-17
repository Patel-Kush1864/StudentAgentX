import ollama

MODEL_NAME = "llama3"

def prioritize(tasks):
    """
    Sends pending tasks to Llama3 via Ollama to prioritize them.
    Yields chunks of the priority order, reasoning, and suggested sequence.
    """
    pending_tasks = [t for t in tasks if t.get("status") == "Pending"]
    
    prompt = f"""
You are a student assistant agent. 

Analyze the following list of pending student tasks:
{pending_tasks}

Please prioritize these tasks based on their deadlines and urgency.
Provide a clear response structured as:
1. **Priority Order**: A numbered list of tasks from highest to lowest priority.
2. **Reasoning**: Explanation of why you prioritized them in this order.
3. **Suggested Completion Sequence**: A concrete sequence and advice on when to work on each task.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True
    )
    for chunk in response:
        yield chunk["message"]["content"]

def generate_study_plan(tasks):
    """
    Generates a structured study schedule and daily study recommendations
    from the list of pending tasks. Yields chunks of the generated schedule.
    """
    pending_tasks = [t for t in tasks if t.get("status") == "Pending"]

    prompt = f"""
You are a student assistant agent.

Here are the student's pending tasks:
{pending_tasks}

Generate a complete, structured study schedule.
Your response must include:
1. **Suggested Study Time Slots**: Daily time slots (e.g., Morning: 9 AM - 11 AM) mapped to specific tasks.
2. **Urgency-based Priority**: Emphasize how the plan addresses the most urgent deadlines first.
3. **Daily Study Recommendations**: Key tips on focus, breaks, and daily milestones to stay on track.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True
    )
    for chunk in response:
        yield chunk["message"]["content"]

def generate_notes(topic):
    """
    Generates exam-ready notes for a given topic using Llama3.
    Structure: Introduction, Working, Advantages, Disadvantages, Conclusion.
    Yields chunks of the generated notes.
    """
    prompt = f"""
You are a student assistant agent.

Generate detailed, exam-ready notes on the following topic: "{topic}"

The notes must follow this exact structural format:
1. **Introduction**: A clear definition and overview of the topic.
2. **Working**: Detailed explanation of how it works or operates.
3. **Advantages**: List of key benefits or pros.
4. **Disadvantages**: List of key drawbacks, limitations, or cons.
5. **Conclusion**: Summary and final takeaway.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True
    )
    for chunk in response:
        yield chunk["message"]["content"]