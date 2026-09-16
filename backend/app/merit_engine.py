from typing import List, Dict, Any

def calculate_merit_score(form_data: Dict[str, Any], income_ceiling: float = 600000.0, marks_weight: float = 0.70, income_weight: float = 0.30) -> float:
    """
    Computes assistive merit score (0 - 100):
    - Academic Merit (marks_weight): Rewards higher scholastic achievement.
    - Economic Need (income_weight): Prioritizes scholars with greater financial need.
    """
    try:
        marks = float(form_data.get("marks_percentage", 60.0))
    except (ValueError, TypeError):
        marks = 60.0

    try:
        income = float(form_data.get("annual_income", 300000.0))
    except (ValueError, TypeError):
        income = 300000.0

    # Academic score capped between 0 and 100
    norm_marks = min(max(marks, 0.0), 100.0)

    # Economic need score: lower income gets higher points (affirmative need principle)
    # If income is 0, need score is 100; if income equals ceiling, need score is 10
    if income_ceiling > 0:
        income_ratio = min(max(income / income_ceiling, 0.0), 1.0)
        norm_need = (1.0 - income_ratio) * 90.0 + 10.0
    else:
        norm_need = 50.0

    total_score = (norm_marks * marks_weight) + (norm_need * income_weight)
    return round(total_score, 2)

def rank_applications(applications: List[Any], marks_weight: float = 0.70, income_weight: float = 0.30) -> List[Dict[str, Any]]:
    """
    Ranks eligible applications and returns an assistive shortlist with score breakdowns.
    """
    scored = []
    for app in applications:
        form_data = app.form_data or {}
        ceiling = app.scheme.income_ceiling if app.scheme else 600000.0
        score = calculate_merit_score(form_data, income_ceiling=ceiling, marks_weight=marks_weight, income_weight=income_weight)

        scored.append({
            "application_id": app.id,
            "application_number": app.application_number,
            "applicant_name": app.applicant.full_name if app.applicant else "N/A",
            "email": app.applicant.email if app.applicant else "N/A",
            "state": app.applicant.state if app.applicant else (form_data.get("state") or "N/A"),
            "community_tribe": app.applicant.community_tribe if app.applicant else (form_data.get("community_tribe") or "ST"),
            "scheme_name": app.scheme.name if app.scheme else "N/A",
            "scheme_code": app.scheme.code if app.scheme else "N/A",
            "status": app.status,
            "marks_percentage": form_data.get("marks_percentage", "N/A"),
            "annual_income": form_data.get("annual_income", "N/A"),
            "institution": form_data.get("institution", "N/A"),
            "course": form_data.get("course", "N/A"),
            "merit_score": score,
            "eligibility_passed": app.eligibility_passed
        })

    # Sort descending by merit score
    scored.sort(key=lambda x: x["merit_score"], reverse=True)

    # Assign 1-indexed ranks
    for idx, item in enumerate(scored, 1):
        item["rank"] = idx

    return scored
