# Student AI Agent

Student AI Agent is a complete, production-quality, local AI-powered assistant designed for students to manage tasks, prioritize their workload, generate study plans, create exam notes, and perform attendance tracking. It runs fully offline using **Python**, **Ollama**, and the **Llama3** model.

## Features

1. **Task Management**:
   - Add tasks with specific deadlines.
   - View a summary of all current tasks (Pending/Completed).
   - Complete tasks from a list of pending tasks.
   - Offline memory stored in `tasks.json`.

2. **AI Task Prioritization**:
   - Analyzes pending tasks using the local `llama3` model.
   - Returns a structured priority order based on deadlines, logical reasoning, and a suggested completion sequence.

3. **AI Study Planner**:
   - Generates a customized, structured study schedule based on pending tasks.
   - Maps tasks to daily time slots and offers concrete recommendations.

4. **AI Notes Generator**:
   - Produces exam-ready notes for any topic.
   - Structured sections include: *Introduction*, *Working*, *Advantages*, *Disadvantages*, and *Conclusion*.

5. **Attendance Analysis**:
   - Tracks attendance for each subject stored in `attendance.json`.
   - Flags subjects falling below the 75% threshold.
   - Automatically computes exactly how many consecutive lectures must be attended to restore attendance to at least 75% using the formula:
     $$x = 3T - 4A$$
     *(where $T$ = total lectures and $A$ = attended lectures)*

---

## Project Structure

```text
student-agent/
│
├── app.py                # Main command line interface (CLI) and application loop
├── database.py           # Functions to load and save data from tasks.json and attendance.json
├── task_agent.py         # AI Agent integration with Ollama (Llama3)
├── tasks.json            # Tasks database (local storage)
├── attendance.json       # Attendance database (local storage)
├── requirements.txt      # Python dependencies
└── README.md             # This documentation
```

---

## Setup Instructions

### Prerequisites
1. **Python 3.8+** installed.
2. **Ollama** installed on your system.
   - If not installed, download from [ollama.com](https://ollama.com).

### Installation & Run Steps

1. **Start Ollama & Download Llama3**
   Open your terminal/command prompt and run:
   ```bash
   ollama run llama3
   ```
   *Make sure the Ollama desktop application is active in the background.*

2. **Install Python Dependencies**
   Navigate to the project directory and install the required library:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   Launch the command line interface:
   ```bash
   python app.py
   ```

---

## Menu Options

Upon running, you will be presented with a menu:
1. **Add Task**: Input task names and deadlines.
2. **View Tasks**: Show status of all tasks.
3. **AI Prioritize Tasks**: Get AI-generated priorities and reasoning.
4. **Complete Task**: Select a pending task by index to mark it complete.
5. **Generate Study Plan**: Get a personalized study calendar.
6. **Generate Notes**: Prompt Llama3 to write exam notes.
7. **Attendance Analysis**: Review percentages and get attendance strategies.
8. **Exit**: Terminate the CLI application.
