import frappe

def check_score():
    # Get all assessment result documents for the academic year 2023 (Term 1)
    assessment_results = frappe.get_all('Assessment Result', filters={'academic_year': '2023 (Term 1)'})

    for result in assessment_results:
        total_score = 0

        # Get all assessment result details linked to the current assessment result
        assessment_result_details = frappe.get_all('Assessment Result Detail', filters={'parent': result.name})

        # Add up the scores
        for detail in assessment_result_details:
            score = frappe.get_value('Assessment Result Detail', detail.name, 'score')
            total_score += score if score else 0

        # Get the total_score from the assessment result
        stored_total_score = frappe.get_value('Assessment Result', result.name, 'total_score')

        # Compare the calculated total_score with the stored total_score
        if total_score != stored_total_score:
            print(f"Mismatch found for Assessment Result {result.name}: Calculated {total_score}, Stored {stored_total_score}")

check_score():