# -*- coding: utf-8 -*-
# Copyright (c) 2022, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from audioop import reverse
import math
import frappe
from frappe import _, msgprint
import pandas as pd
import numpy as np
import functools


@frappe.whitelist()
def get_total_score(student):
	#*******Get students assessment results as list of dictionary
	total_score = frappe.db.sql("""SELECT ROUND(SUM(tabAR.total_score)/(count(tabAR.total_score)*100)*100, 1) AS 'totalScore'
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
	score = frappe.db.sql("""SELECT ROUND(SUM(tabARD.raw_marks)/(count(tabARD.raw_marks)*100)*100, 1) AS 'Score' 
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

	totalClass = frappe.db.sql("""SELECT COUNT(*)
					FROM `tabProgram Enrollment`
					WHERE program = %s""", (program))

	
	ClassTotal = functools.reduce(lambda sub, ele: sub * 10 + ele, totalClass)

	midyear_position = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name,
					SUM(tabARD.raw_marks) AS 'MidYear_Total'
					FROM `tabAssessment Result` as tabAR
					LEFT JOIN `tabAssessment Result Detail` AS tabARD
					ON tabAR.name = tabARD.parent
					WHERE tabAR .docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					AND tabARD.assessment_criteria = 'Mid Year Exam'
					GROUP BY tabAR.student""", (program), as_dict=1)
	
	overall_position = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name,
					SUM(tabAR.total_score) AS 'Overall_Total'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR .docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					GROUP BY tabAR.student""", (program), as_dict=1)
	
	overalData = pd.DataFrame.from_records(overall_position)
	overalData['Mark_Rank'] = overalData['Overall_Total'].rank(ascending = 0)

	dataframe = pd.DataFrame.from_records(midyear_position)
	dataframe['Mark_Rank'] = dataframe['MidYear_Total'].rank(ascending = 0)
	#dataframe = dataframe.set_index('Mark_Rank')
	#dataframe = dataframe.sort_index()

	studentID = student

	OverallPosition = dataframe.loc[dataframe.student == studentID,'Mark_Rank'].values[0]
	MidYearPosition = dataframe.loc[dataframe.student == studentID,'Mark_Rank'].values[0]

#	frappe.msgprint(_("Class {0}").format(ClassTotal))
#	frappe.msgprint(_("Class {0}").format(MidYearPosition))
	
	return MidYearPosition, OverallPosition, ClassTotal

def get_program(student):
	return frappe.get_value('Program Enrollment', {'student': student}, ['program'])

def totalFunc(ele):
	return ele['MidYear_Total']