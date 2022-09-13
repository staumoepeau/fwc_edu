# -*- coding: utf-8 -*-
# Copyright (c) 2022, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from audioop import reverse
import math
import frappe
from frappe import _, msgprint

@frappe.whitelist()
def get_total_score(student):
	#*******Get students assessment results as list of dictionary
	total_score = frappe.db.sql("""SELECT SUM(tabAR.total_score)/(count(tabAR.total_score)*100)*100 AS 'totalScore'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.student = %s
					AND tabAR .docstatus = 1
					AND tabAR.not_included = 0
					GROUP BY tabAR.student
					ORDER BY SUM(tabAR.total_score) DESC""", student)

	return total_score

@frappe.whitelist()
def get_midyear_score(student):
	#*******Get students assessment results as list of dictionary

	program = get_program(student)
	score = frappe.db.sql("""SELECT SUM(tabARD.score)/(count(tabARD.score)*100)*100 AS 'Score' 
				FROM `tabAssessment Result` as tabAR
				LEFT JOIN `tabAssessment Result Detail` AS tabARD
				ON tabAR.name = tabARD.parent
				WHERE tabAR .docstatus = 1
				AND tabAR.student = %s
				AND tabAR.program = %s
				AND tabAR.not_included = 0
				AND tabARD.assessment_criteria = 'Mid Year Exam'""", (student, program))

	return score

@frappe.whitelist()
def get_midyear_position(student):
	#*******Get students assessment results as list of dictionary
#	def totalFunc(ele):
#		return ele['MidYear_Total']

	program = get_program(student)
	midyear_position = frappe.db.sql("""SELECT tabAR.academic_year, 
					tabAR.academic_term, tabAR.student, tabAR.student_name,
					tabARD.assessment_criteria, SUM(tabARD.score) AS 'MidYear_Total'
					FROM `tabAssessment Result` as tabAR
					LEFT JOIN `tabAssessment Result Detail` AS tabARD
					ON tabAR.name = tabARD.parent
					WHERE tabAR .docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					AND tabARD.assessment_criteria = 'Mid Year Exam'
					GROUP BY tabAR.student""", (program), as_dict=1)
	
	midyear_position.sort(key=totalFunc, reverse=True)

	frappe.msgprint(_("Class {0}").format(midyear_position))
	
	return midyear_position

def get_program(student):
	return frappe.get_value('Program Enrollment', {'student': student}, ['program'])

def totalFunc(ele):
	return ele['MidYear_Total']