import json
import os

TASKS_FILE = "tasks.json"
ATTENDANCE_FILE = "attendance.json"

def load_tasks():
    """
    Loads tasks from tasks.json.
    If the file does not exist or has invalid JSON, returns an empty list.
    """
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading tasks: {e}. Returning empty list.")
        return []

def save_tasks(tasks):
    """
    Saves the tasks list to tasks.json.
    """
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)
    except IOError as e:
        print(f"Error saving tasks: {e}")

def load_attendance():
    """
    Loads attendance data from attendance.json.
    If the file does not exist or has invalid JSON, returns an empty list.
    """
    if not os.path.exists(ATTENDANCE_FILE):
        return []
    try:
        with open(ATTENDANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading attendance: {e}. Returning empty list.")
        return []

def save_attendance(attendance):
    """
    Saves attendance records to attendance.json.
    """
    try:
        with open(ATTENDANCE_FILE, "w", encoding="utf-8") as f:
            json.dump(attendance, f, indent=4)
    except IOError as e:
        print(f"Error saving attendance: {e}")