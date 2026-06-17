from datetime import datetime, date

def calculate_days_remaining(deadline_str):
    """
    Parses a deadline string and calculates the number of days remaining
    relative to the current date: 2026-06-17.
    """
    cleaned = deadline_str.strip().lower()
    
    if "tomorrow" in cleaned:
        return 1
    if "today" in cleaned:
        return 0
    if "completed" in cleaned or "done" in cleaned:
        return 0
        
    # Match phrases like "3 days" or "5 days left"
    if "day" in cleaned:
        try:
            for word in cleaned.split():
                if word.isdigit():
                    return int(word)
        except Exception:
            pass

    # Try standard date string formats
    current_date = date(2026, 6, 17)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            target_date = datetime.strptime(deadline_str.strip(), fmt).date()
            return (target_date - current_date).days
        except Exception:
            continue
            
    return 7  # Default fallback

def auto_calculate_priority(days_remaining):
    """
    Derives task priority level (High, Medium, Low) based on days remaining.
    """
    if days_remaining <= 2:
        return "High"
    elif days_remaining <= 5:
        return "Medium"
    else:
        return "Low"

def get_urgent_tasks(tasks):
    """
    Filters and returns a list of urgent pending tasks (deadline <= 2 days).
    """
    urgent = []
    for t in tasks:
        if t.get("status") == "Pending":
            days = calculate_days_remaining(t.get("deadline", ""))
            if days <= 2:
                urgent.append({
                    "task_name": t.get("task_name"),
                    "deadline": t.get("deadline"),
                    "days_remaining": days,
                    "priority": t.get("priority")
                })
    return urgent
