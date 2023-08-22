import frappe

def update_total_score():
    # Get all assessment result documents
    assessment_results = frappe.get_all('Assessment Result', filters={'academic_year': '2023 (Term 1)'})

    for result in assessment_results:
        total_score = 0

        # Get all assessment result details linked to the current assessment result
        assessment_result_details = frappe.get_all('Assessment Result Detail', filters={'parent': result.name})

        # Add up the scores
        for detail in assessment_result_details:
            score = frappe.get_value('Assessment Result Detail', detail.name, 'score')
            total_score += score if score else 0

        # Update the total score in the assessment result
        frappe.db.set_value('Assessment Result', result.name, 'total_score', total_score)


update_total_score()