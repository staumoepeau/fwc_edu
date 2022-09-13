# Copyright (c) 2022, Sione Taumoepeau and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StudentReportCard(Document):

	def validate(self):
		pass

@frappe.whitelist()
def getstudentsresultinfo(student):
	#*******Get students assessment results as list of dictionary
	results = frappe.get_all("Assessment Result", filters={"student": student, "docstatus": 1})
	#**** for each of the results create an object that contains the subject and the result details
	results_obj = []
	for i in results:
		result_name = i.name
		results_h = frappe.get_doc('Assessment Result',i)
		course = frappe.get_doc("Assessment Plan",results_h.assessment_plan).course
		total_score = results_h.total_score
		maximum_score = results_h.maximum_score
		grade = results_h.grade
		score_breakdown = []
		for j in results_h.details:
			score_breakdown.append({'criteria':j.assessment_criteria,'maximum_score':j.maximum_score,'score':j.score,'raw_marks':j.raw_marks})
		results_obj.append({
			"result_name":result_name,
			"course":course,
			"grade":grade,
			"score":total_score,
			"score_breakdown":score_breakdown,
			"maximum_score":maximum_score
			})
	return results_obj
