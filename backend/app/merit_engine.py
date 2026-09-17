from typing import List, Dict, Any

PVTG_COMMUNITIES = {
    "chenchu", "toda", "birhor", "maria gond", "sauria paharia", "asur",
    "katkari", "kolam", "koraga", "baiga", "sahariya", "kamar", "bondo",
    "dongria kondh", "chuktia bhunjia", "kutia kondh", "lodha"
}

def calculate_merit_score(
    form_data: Dict[str, Any],
    income_ceiling: float = 600000.0,
    marks_weight: float = 0.70,
    income_weight: float = 0.30,
    merit_weights: Dict[str, Any] = None
) -> float:
    """
    Computes assistive merit score (0 - 100) incorporating official MoTA scheme rules:
    - Academic Merit (marks_weight)
    - Economic Need / Interview (if applicable)
    - Preferred Group Affirmative Bonuses:
        * Female scholar bonus (+5 points)
        * Particularly Vulnerable Tribal Group (PVTG) bonus (+5 points)
        * Divyangjan (Disability) bonus (+3 points)
    """
    weights = merit_weights or {}
    effective_marks_w = weights.get("marks_weight", marks_weight)
    effective_income_w = weights.get("income_weight", income_weight)
    interview_w = weights.get("interview_weight", 0.0)

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

    # Economic need score: lower income gets higher points
    if income_ceiling > 0:
        income_ratio = min(max(income / income_ceiling, 0.0), 1.0)
        norm_need = (1.0 - income_ratio) * 90.0 + 10.0
    else:
        norm_need = 50.0

    total_score = (norm_marks * effective_marks_w) + (norm_need * effective_income_w)

    # Optional interview score (NOS scheme)
    if interview_w > 0:
        try:
            int_score = float(form_data.get("interview_score", 70.0))
        except (ValueError, TypeError):
            int_score = 70.0
        total_score += min(max(int_score, 0.0), 100.0) * interview_w

    # Affirmative Preferred Group Bonuses (MoTA guidelines)
    bonus_points = 0.0

    # 1. Female Scholar Bonus (+5)
    gender = str(form_data.get("gender", "")).strip().lower()
    if gender == "female" or form_data.get("is_female") is True:
        bonus_points += float(weights.get("female_bonus", 5.0))

    # 2. PVTG Scholar Bonus (+5)
    tribe = str(form_data.get("community_tribe", "")).strip().lower()
    is_pvtg = form_data.get("is_pvtg") is True or any(pvtg in tribe for pvtg in PVTG_COMMUNITIES)
    if is_pvtg:
        bonus_points += float(weights.get("pvtg_bonus", 5.0))

    # 3. Divyangjan / Disability Bonus (+3)
    if form_data.get("is_divyangjan") is True or form_data.get("disability_status") is True:
        bonus_points += float(weights.get("divyangjan_bonus", 3.0))

    final_score = min(max(total_score + bonus_points, 0.0), 100.0)
    return round(final_score, 2)

def rank_applications(applications: List[Any], marks_weight: float = 0.70, income_weight: float = 0.30) -> List[Dict[str, Any]]:
    """
    Ranks eligible applications and returns an assistive shortlist with score breakdowns.
    """
    scored = []
    for app in applications:
        form_data = app.form_data or {}
        ceiling = app.scheme.income_ceiling if app.scheme else 600000.0
        scheme_w = app.scheme.merit_weights if app.scheme and app.scheme.merit_weights else None
        score = calculate_merit_score(
            form_data,
            income_ceiling=ceiling,
            marks_weight=marks_weight,
            income_weight=income_weight,
            merit_weights=scheme_w
        )

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
