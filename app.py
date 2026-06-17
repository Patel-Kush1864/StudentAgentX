import math
from database import load_tasks, save_tasks, load_attendance
from task_agent import prioritize, generate_study_plan, generate_notes

def display_menu():
    """
    Displays the student assistant command line menu options.
    """
    print("\n" + "=" * 45)
    print("         STUDENT AI ASSISTANT AGENT          ")
    print("=" * 45)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. AI Prioritize Tasks")
    print("4. Complete Task")
    print("5. Generate Study Plan")
    print("6. Generate Notes")
    print("7. Attendance Analysis")
    print("8. Exit")
    print("=" * 45)

def add_task_flow():
    """
    Guides the user through adding a new task, with validation.
    """
    print("\n--- Add New Task ---")
    task_name = input("Enter task name: ").strip()
    if not task_name:
        print("[ERROR] Task name cannot be empty.")
        return

    deadline = input("Enter deadline (e.g. 'Tomorrow', '3 Days', '2026-06-20'): ").strip()
    if not deadline:
        print("[ERROR] Deadline cannot be empty.")
        return

    tasks = load_tasks()
    new_task = {
        "task": task_name,
        "deadline": deadline,
        "status": "Pending"
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"[SUCCESS] Task '{task_name}' successfully added as 'Pending'.")

def view_tasks_flow():
    """
    Loads and displays all tasks with status and deadline formatting.
    """
    print("\n--- Current Tasks ---")
    tasks = load_tasks()
    if not tasks:
        print("No tasks found. Add some tasks first!")
        return

    print(f"{'#':<4} {'Task Name':<30} {'Deadline':<15} {'Status':<10}")
    print("-" * 65)
    for idx, task in enumerate(tasks, 1):
        status_symbol = "[Pending]" if task.get("status") == "Pending" else "[Completed]"
        print(f"{idx:<4} {task.get('task'):<30} {task.get('deadline'):<15} {status_symbol:<10}")

def ai_prioritize_flow():
    """
    Loads tasks and uses Llama3 to prioritize them, streaming the output.
    """
    print("\n--- AI Task Prioritizer (Ollama) ---")
    tasks = load_tasks()
    pending_tasks = [t for t in tasks if t.get("status") == "Pending"]
    if not pending_tasks:
        print("No pending tasks to prioritize!")
        return

    print("[AI] Analyzing your tasks and deadlines. Please wait...")
    print("\n[AI Recommendations]:")
    print("-" * 50)
    try:
        for chunk in prioritize(tasks):
            print(chunk, end='', flush=True)
        print()
    except Exception as e:
        print(f"\n[ERROR] Error communicating with Ollama: {e}")
        print("Please verify that Ollama is running and Llama3 is installed (`ollama run llama3`).")

def complete_task_flow():
    """
    Guides the user to select and mark a pending task as completed.
    """
    print("\n--- Complete Task ---")
    tasks = load_tasks()
    
    # Filter only pending tasks to choose from
    pending_tasks_with_index = [(original_idx, task) for original_idx, task in enumerate(tasks) if task.get("status") == "Pending"]
    
    if not pending_tasks_with_index:
        print("No pending tasks found to complete!")
        return

    print("Pending Tasks:")
    for display_idx, (original_idx, task) in enumerate(pending_tasks_with_index, 1):
        print(f"{display_idx}. {task.get('task')} (Deadline: {task.get('deadline')})")

    try:
        choice_str = input("\nEnter the number of the task to complete: ").strip()
        choice = int(choice_str)
        if 1 <= choice <= len(pending_tasks_with_index):
            original_idx, selected_task = pending_tasks_with_index[choice - 1]
            tasks[original_idx]["status"] = "Completed"
            save_tasks(tasks)
            print(f"[SUCCESS] Task '{selected_task.get('task')}' marked as Completed!")
        else:
            print("[ERROR] Selection out of range.")
    except ValueError:
        print("[ERROR] Please enter a valid number.")

def generate_study_plan_flow():
    """
    Generates an AI structured study schedule, streaming the output.
    """
    print("\n--- AI Study Planner (Ollama) ---")
    tasks = load_tasks()
    pending_tasks = [t for t in tasks if t.get("status") == "Pending"]
    if not pending_tasks:
        print("No pending tasks to plan for!")
        return

    print("[AI] Drafting your study schedule. Please wait...")
    print("\n[AI Study Plan]:")
    print("-" * 50)
    try:
        for chunk in generate_study_plan(tasks):
            print(chunk, end='', flush=True)
        print()
    except Exception as e:
        print(f"\n[ERROR] Error communicating with Ollama: {e}")
        print("Please verify that Ollama is running and Llama3 is installed (`ollama run llama3`).")

def generate_notes_flow():
    """
    Prompts the user for a topic and generates exam notes, streaming the output.
    """
    print("\n--- AI Exam Notes Generator (Ollama) ---")
    topic = input("Enter the topic you want exam notes for: ").strip()
    if not topic:
        print("[ERROR] Topic cannot be empty.")
        return

    print(f"[AI] Generating exam-ready notes for '{topic}'. Please wait...")
    print("\n[AI Notes]:")
    print("-" * 50)
    try:
        for chunk in generate_notes(topic):
            print(chunk, end='', flush=True)
        print()
    except Exception as e:
        print(f"\n[ERROR] Error communicating with Ollama: {e}")
        print("Please verify that Ollama is running and Llama3 is installed (`ollama run llama3`).")

def attendance_analysis_flow():
    """
    Reads attendance, prints analysis, flags low subjects, 
    and calculates consecutive lectures needed to hit 75%.
    """
    print("\n--- Attendance Analysis ---")
    attendance = load_attendance()
    if not attendance:
        print("No attendance records found in attendance.json.")
        return

    print(f"{'Subject':<20} {'Attended':<10} {'Total':<10} {'Percentage':<12} {'Status':<15}")
    print("-" * 72)
    
    low_attendance_flag = False

    for record in attendance:
        subject = record.get("subject", "Unknown")
        attended = record.get("attended", 0)
        total = record.get("total", 0)
        
        if total == 0:
            percentage = 0.0
        else:
            percentage = (attended / total) * 100

        # Determine status
        if percentage >= 75.0:
            status = "Sufficient"
        else:
            status = "LOW (<75%)"
            low_attendance_flag = True

        print(f"{subject:<20} {attended:<10} {total:<10} {percentage:.2f}%{' ':<5} {status:<15}")

        if percentage < 75.0:
            # Formula: x = 3T - 4A to hit 75%
            needed = (3 * total) - (4 * attended)
            if needed > 0:
                print(f"   * Recommendation: Attend the next {needed} lectures consecutively to reach 75%.")
            else:
                # Fallback if rounding edge cases occur
                print(f"   * Recommendation: Attend next lectures consecutively to improve.")

    if not low_attendance_flag:
        print("\nExcellent! Your attendance in all subjects is at or above 75%. Keep it up!")

def main():
    """
    Main program loop for the Student AI Assistant Agent CLI.
    """
    while True:
        display_menu()
        choice = input("Enter choice (1-8): ").strip()
        
        if choice == "1":
            add_task_flow()
        elif choice == "2":
            view_tasks_flow()
        elif choice == "3":
            ai_prioritize_flow()
        elif choice == "4":
            complete_task_flow()
        elif choice == "5":
            generate_study_plan_flow()
        elif choice == "6":
            generate_notes_flow()
        elif choice == "7":
            attendance_analysis_flow()
        elif choice == "8":
            print("\nExiting Student AI Assistant Agent. Good luck with your studies!")
            break
        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 8.")

if __name__ == "__main__":
    main()