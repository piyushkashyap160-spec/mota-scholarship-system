from typing import Dict, Any, List, Tuple

def evaluate_eligibility(scheme_rules: Dict[str, Any], form_data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Evaluates applicant's form data against scheme's configurable eligibility rules.
    Returns: (is_eligible, notes, breakdown)
    """
    notes = []
    breakdown = {}
    is_eligible = True

    # 1. Category check (ST mandatory)
    req_category = scheme_rules.get("category_required", "ST")
    user_category = form_data.get("category", "ST")
    cat_pass = user_category.upper() == req_category.upper()
    breakdown["category"] = {
        "label": "Social Category (ST)",
        "required": req_category,
        "provided": user_category,
        "passed": cat_pass,
        "remarks": "Verified Scheduled Tribe" if cat_pass else "Must belong to Scheduled Tribe"
    }
    if not cat_pass:
        is_eligible = False
        notes.append(f"Ineligible: Social category is {user_category}; scheme requires {req_category}")
    else:
        notes.append("Category Requirement Satisfied (ST)")

    # 2. Income Ceiling check
    income_ceiling = scheme_rules.get("income_ceiling", 600000.0)
    try:
        user_income = float(form_data.get("annual_income", 0.0))
    except (ValueError, TypeError):
        user_income = 0.0

    income_pass = user_income <= income_ceiling
    breakdown["income"] = {
        "label": "Annual Family Income Ceiling",
        "ceiling": f"₹ {income_ceiling:,.0f}",
        "provided": f"₹ {user_income:,.0f}",
        "passed": income_pass,
        "remarks": f"Within allowable limit of ₹{income_ceiling:,.0f}" if income_pass else f"Exceeds ceiling by ₹{user_income - income_ceiling:,.0f}"
    }
    if not income_pass:
        is_eligible = False
        notes.append(f"Ineligible: Annual family income ₹{user_income:,.0f} exceeds ceiling ₹{income_ceiling:,.0f}")
    else:
        notes.append(f"Income Requirement Satisfied (₹{user_income:,.0f} <= ₹{income_ceiling:,.0f})")

    # 3. Minimum Qualifying Marks check
    min_marks = scheme_rules.get("min_qualifying_percentage", 55.0)
    try:
        user_marks = float(form_data.get("marks_percentage", 0.0))
    except (ValueError, TypeError):
        user_marks = 0.0

    marks_pass = user_marks >= min_marks
    breakdown["marks"] = {
        "label": "Minimum Academic Marks",
        "required_min": f"{min_marks}%",
        "provided": f"{user_marks}%",
        "passed": marks_pass,
        "remarks": f"Meets qualifying threshold ({min_marks}%)" if marks_pass else f"Below minimum cut-off of {min_marks}%"
    }
    if not marks_pass:
        is_eligible = False
        notes.append(f"Ineligible: Marks {user_marks}% below required {min_marks}%")
    else:
        notes.append(f"Academic Marks Threshold Satisfied ({user_marks}% >= {min_marks}%)")

    # 4. Course / Degree Eligibility
    eligible_courses = scheme_rules.get("eligible_courses", [])
    user_course = form_data.get("degree_level", form_data.get("course", ""))
    course_pass = True
    if eligible_courses and user_course:
        course_pass = any(c.lower() in user_course.lower() for c in eligible_courses)
    breakdown["course"] = {
        "label": "Degree / Course Level",
        "eligible_courses": eligible_courses,
        "provided": user_course,
        "passed": course_pass,
        "remarks": "Enrolled in approved higher education / research program" if course_pass else "Course level not covered under scheme guidelines"
    }
    if not course_pass:
        is_eligible = False
        notes.append(f"Ineligible: Degree '{user_course}' not in approved scheme list")
    else:
        notes.append(f"Program Level Satisfied ({user_course})")

    return is_eligible, notes, breakdown
