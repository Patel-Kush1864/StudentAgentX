def analyze_attendance(records):
    """
    Analyzes a list of subject attendance dictionaries and returns structured calculations,
    flagging risk levels and calculating consecutive lectures required to hit 75%.
    """
    analysis_results = []
    low_attendance_subjects = []
    
    for r in records:
        subj = r.get("subject_name", "Unknown")
        att = r.get("attended", 0)
        tot = r.get("total", 0)
        
        pct = (att / tot * 100) if tot > 0 else 0.0
        status = "Sufficient" if pct >= 75.0 else "Low"
        
        recovery_lectures = 0
        if pct < 75.0:
            recovery_lectures = max(0, (3 * tot) - (4 * att))
            low_attendance_subjects.append({
                "subject": subj,
                "percentage": round(pct, 2),
                "needed": recovery_lectures
            })
            
        # Shortage prediction: check attendance percentage if student misses the next 3 lectures
        projected_pct = (att / (tot + 3) * 100) if (tot + 3) > 0 else 0.0
        shortage_risk = projected_pct < 75.0
        
        analysis_results.append({
            "subject": subj,
            "attended": att,
            "total": tot,
            "percentage": round(pct, 2),
            "status": status,
            "needed": recovery_lectures,
            "projected_percentage": round(projected_pct, 2),
            "shortage_risk": shortage_risk
        })
        
    return {
        "analysis": analysis_results,
        "low_subjects": low_attendance_subjects
    }
