# Copyright (c) 2023, Sione Taumoepeau and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
import pandas as pd
import numpy as np


def execute(filters=None):
    columns, data = [], []

    term = filters.get('academic_term')
    # Get all assessment result documents
    assessment_results = frappe.get_all('Assessment Result', filters={'academic_term': '2023 (Term 1)'})

    for result in assessment_results:
        total_score = 0

        # Get all assessment result details linked to the current assessment result
        assessment_result_details = frappe.get_all('Assessment Result Detail', filters={'parent': result.name})

        # Add up the scores
        for detail in assessment_result_details:
            score = frappe.get_value('Assessment Result Detail', detail.name, 'score')
            total_score += score if score else 0

        total_score = round(total_score, 2)

        stored_total_score = frappe.get_value('Assessment Result', result.name, 'total_score')

		stored_total_score = round(stored_total_score, 2)

        # Compare the calculated total_score with the stored total_score
        if total_score != stored_total_score:
			
            frappe.db.sql("""Update `tabAssessment Result` set docstatus=0 where name=%s""",(result.name))


    return columns, data
