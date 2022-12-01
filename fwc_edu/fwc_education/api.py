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
from re import search
from collections import Counter
from frappe.utils import (
	cint,
	flt,
	rounded
)


@frappe.whitelist()
def get_total_score(student, term):

	program = get_program(student, term)
#	frappe.msgprint(_("Dataframe {0}").format(program))
	if program in ('Form 5K','Form 5L','Form 5M','Form 5S','Form 5T','Form 5V',
		'Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):
		
		
	#*******Get students assessment results as list of dictionary
		total_score = frappe.db.sql("""SELECT ROUND(SUM(tabAR.total_score)/(600)*100, 2) AS 'totalScore'
			FROM `tabAssessment Result` as tabAR
			WHERE tabAR.student = %s
			AND tabAR.docstatus = 1
			AND tabAR.not_included = 0
			AND tabAR.academic_term = %s
			GROUP BY tabAR.student
			ORDER BY SUM(tabAR.total_score) DESC""", (student, term))
	else:
		
		total_score = frappe.db.sql("""SELECT ROUND(SUM(tabAR.total_score)/(800)*100, 2) AS 'totalScore'
			FROM `tabAssessment Result` as tabAR
			WHERE tabAR.student = %s
			AND tabAR.docstatus = 1
			AND tabAR.not_included = 0
			AND tabAR.academic_term = %s
			GROUP BY tabAR.student
			ORDER BY SUM(tabAR.total_score) DESC""", (student, term))
	
	return total_score

@frappe.whitelist()
def get_midyear_score(student, term):
	#*******Get students assessment results as list of dictionary

	program = get_program(student, term)
	if program in ('Form 5K','Form 5L','Form 5M','Form 5S','Form 5T','Form 5V',
		'Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):

		score = frappe.db.sql("""SELECT ROUND(SUM(tabARD.raw_marks)/(600)*100, 2) AS 'Score' 
				FROM `tabAssessment Result` as tabAR
				LEFT JOIN `tabAssessment Result Detail` AS tabARD
				ON tabAR.name = tabARD.parent
				WHERE tabAR.docstatus = 1
				AND tabAR.student = %s
				AND tabAR.program = %s
				AND tabAR.academic_term = %s
				AND tabAR.not_included = 0
				AND tabARD.assessment_criteria = 'Mid Year Exam'""", (student, program, term))
	else:
		score = frappe.db.sql("""SELECT ROUND(SUM(tabARD.raw_marks)/(800)*100, 2) AS 'Score' 
				FROM `tabAssessment Result` as tabAR
				LEFT JOIN `tabAssessment Result Detail` AS tabARD
				ON tabAR.name = tabARD.parent
				WHERE tabAR.docstatus = 1
				AND tabAR.student = %s
				AND tabAR.program = %s
				AND tabAR.academic_term = %s
				AND tabAR.not_included = 0
				AND tabARD.assessment_criteria = 'Mid Year Exam'""", (student, program, term))

#	frappe.msgprint(_("Score {0}").format(score))
	return score

@frappe.whitelist()
def get_midyear_position(student, term):
	#*******Get students assessment results as list of dictionary
#	def totalFunc(ele):
#		return ele['MidYear_Total']

	program = get_program(student, term)

	if (term == "2022 (Term 1)"):

		totalClass = frappe.db.sql("""SELECT COUNT(*)
					FROM `tabProgram Enrollment`
					WHERE company = 'Queen Salote College'
					AND program = %s""", (program))

	
		ClassTotal = functools.reduce(lambda sub, ele: sub * 10 + ele, totalClass)

		midyear_position = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name,
					SUM(tabARD.raw_marks) AS 'MidYear_Total'
					FROM `tabAssessment Result` as tabAR
					LEFT JOIN `tabAssessment Result Detail` AS tabARD
					ON tabAR.name = tabARD.parent
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					AND tabAR.academic_term = %s
					AND tabARD.assessment_criteria = 'Mid Year Exam'
					GROUP BY tabAR.student""", (program, term), as_dict=1)
	
		overall_position = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name,
					SUM(tabAR.total_score) AS 'Overall_Total'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					AND tabAR.academic_term = %s
					GROUP BY tabAR.student""", (program, term), as_dict=1)
	
		overalData = pd.DataFrame.from_records(overall_position)
		overalData['Mark_Rank'] = overalData['Overall_Total'].rank(ascending = 0)

		dataMidyear = pd.DataFrame.from_records(midyear_position)
		dataMidyear['Mark_Rank'] = dataMidyear['MidYear_Total'].rank(ascending = 0)
		#dataframe = dataframe.set_index('Mark_Rank')
		#dataframe = dataframe.sort_index()

		#studentID = student

		OverallPosition = overalData.loc[overalData.student == student,'Mark_Rank'].values[0]

		MidYearPosition = dataMidyear.loc[dataMidyear.student == student,'Mark_Rank'].values[0]
		
		MidYear = "{:.0f}".format(MidYearPosition)

		return MidYear, OverallPosition, ClassTotal

@frappe.whitelist()
def get_final_second_half(student, term):
	#*******Get students assessment results as list of dictionary

	program = get_program(student, term)
	if program in ('Form 5K','Form 5L','Form 5M','Form 5S','Form 5T','Form 5V',
		'Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):

		finalhalf_score = frappe.db.sql("""SELECT ROUND(SUM(tabAR.total_score)/(600)*100, 3) AS 'Score' 
				FROM `tabAssessment Result` as tabAR
				WHERE tabAR.docstatus = 1
				AND tabAR.student = %s
				AND tabAR.program = %s
				AND tabAR.academic_term = %s
				AND tabAR.not_included = 0
				""", (student, program, term))

		midyear_score = frappe.db.sql("""SELECT ROUND(SUM(tabAR.total_score)/(600)*100, 3) AS 'Score' 
				FROM `tabAssessment Result` as tabAR
				WHERE tabAR.docstatus = 1
				AND tabAR.student = %s
				AND tabAR.program = %s
				AND tabAR.academic_term = '2022 (Term 1)'
				AND tabAR.not_included = 0
				""", (student, program))
	else:
		finalhalf_score = frappe.db.sql("""SELECT ROUND(SUM(tabAR.total_score)/(800)*100, 3) AS 'Score' 
				FROM `tabAssessment Result` as tabAR
				WHERE tabAR.docstatus = 1
				AND tabAR.not_included = 0
				AND tabAR.student = %s
				AND tabAR.program = %s
				AND tabAR.academic_term = %s
				""", (student, program, term))

		midyear_score = frappe.db.sql("""SELECT ROUND(SUM(tabAR.total_score)/(800)*100, 3) AS 'Score' 
				FROM `tabAssessment Result` as tabAR
				WHERE tabAR.docstatus = 1
				AND tabAR.not_included = 0
				AND tabAR.student = %s
				AND tabAR.program = %s
				AND tabAR.academic_term = '2022 (Term 1)'
				AND tabAR.not_included = 0
				""", (student, program))
	
	midyear_score = str(midyear_score).replace(',', '')
	midyear_score = str(midyear_score).replace('((', '')
	midyear_score = str(midyear_score).replace('))', '')

	midyear_40 = float(midyear_score)*40/100

	finalhalf_score = str(finalhalf_score).replace(',', '')
	finalhalf_score = str(finalhalf_score).replace('((', '')
	finalhalf_score = str(finalhalf_score).replace('))', '')

	finalhalf_score = round(float(finalhalf_score), 2)
	finalhalf_60 = round(float(finalhalf_score)*60/100, 2)

	grand_total = round(float(midyear_40 + finalhalf_60), 2)

	frappe.msgprint(_("MID1 {0}").format(midyear_score))
	frappe.msgprint(_("MID {0}").format(midyear_40))
	frappe.msgprint(_("FIN {0}").format(finalhalf_60))

	
	return finalhalf_score, grand_total


@frappe.whitelist()
def get_finalsecond_half_position(student, term):
	#*******Get students assessment results as list of dictionary
#	def totalFunc(ele):
#		return ele['MidYear_Total']

	program = get_program(student, term)

	totalClass = frappe.db.sql("""SELECT COUNT(*)
						FROM `tabProgram Enrollment`
						WHERE company = 'Queen Salote College'
						AND docstatus = 1
						AND program = %s
						AND academic_term = %s""", (program, term))

	Final_ClassTotal = functools.reduce(lambda sub, ele: sub * 10 + ele, totalClass)

	level = program[:-1]
	leveltotal = frappe.db.sql("""SELECT COUNT(*)
						FROM `tabProgram Enrollment`
						WHERE company = 'Queen Salote College'
						AND docstatus = 1
						AND program LIKE %s
						AND academic_term = %s""",("%%%s%%" % level, term))

		
	Level_Total = functools.reduce(lambda sub, ele: sub * 10 + ele, leveltotal)

	if program in ('Form 5K','Form 5L','Form 5M','Form 5S','Form 5T','Form 5V',
		'Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):


		final_second_half_position =frappe.db.sql("""SELECT tabAR.student, tabAR.student_name,
					ROUND(SUM(tabAR.total_score)/(600)*100, 2) AS 'Final_Second_Half_Total'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					AND tabAR.academic_term = %s
					GROUP BY tabAR.student
					""", (program, term), as_dict=1)
	else:

		final_second_half_position =frappe.db.sql("""SELECT tabAR.student, tabAR.student_name,
					ROUND(SUM(tabAR.total_score)/(800)*100, 2) AS 'Final_Second_Half_Total'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					AND tabAR.academic_term = %s
					GROUP BY tabAR.student
				""", (program, term), as_dict=1)
		

	dataFinal = pd.DataFrame.from_records(final_second_half_position)

	dataFinal['Rank'] = dataFinal['Final_Second_Half_Total'].rank(ascending = 0)

#	dataFinal = dataFinal.sort_values(by=['Rank'])

#	frappe.msgprint(_("Level {0}").format(dataFinal))

	FinalHalfPosition = dataFinal.loc[dataFinal.student == student,'Rank'].values[0]
	
#	frappe.msgprint(_("Position {0}").format(FinalHalfPosition))

	FinalHalfPosition = "{:.0f}".format(FinalHalfPosition)

	return FinalHalfPosition, Final_ClassTotal, Level_Total


@frappe.whitelist()
def get_final_overall_position(student, term):
	#*******Get students assessment results as list of dictionary
#	def totalFunc(ele):
#		return ele['MidYear_Total']
	
	program = get_program(student, term)

	level = program[:-1]


#	frappe.msgprint(_("Level Total {0}").format(Level_Total))
	if (level in ('Form 1', 'Form 2', 'Form 3', 'Form 4')):

		if student in ('S22000368','S22000478'):

			midyear_40 = frappe.db.sql("""SELECT tabAR.student,
					ROUND(((SUM(tabAR.total_score)/700*100)*40/100), 2) AS 'MidYear_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.academic_term = "2022 (Term 1)"
					GROUP BY tabAR.student""", ("%%%s%%" % level), as_dict=1)
	
			final_60 = frappe.db.sql("""SELECT tabAR.student,
					ROUND(((SUM(tabAR.total_score)/700*100)*60/100), 2) AS 'Total_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.academic_term = %s
					GROUP BY tabAR.student""", ("%%%s%%" % level, term), as_dict=1)
		else:

			midyear_40 = frappe.db.sql("""SELECT tabAR.student,
						ROUND(((SUM(tabAR.total_score)/800*100)*40/100), 2) AS 'MidYear_Score'
						FROM `tabAssessment Result` as tabAR
						WHERE tabAR.docstatus = 1
						AND tabAR.not_included = 0
						AND tabAR.program LIKE %s
						AND tabAR.academic_term = "2022 (Term 1)"
						GROUP BY tabAR.student""", ("%%%s%%" % level), as_dict=1)
		
			final_60 = frappe.db.sql("""SELECT tabAR.student,
						ROUND(((SUM(tabAR.total_score)/800*100)*60/100), 2) AS 'Total_Score'
						FROM `tabAssessment Result` as tabAR
						WHERE tabAR.docstatus = 1
						AND tabAR.not_included = 0
						AND tabAR.program LIKE %s
						AND tabAR.academic_term = %s
						GROUP BY tabAR.student""", ("%%%s%%" % level, term), as_dict=1)
	else:

		midyear_40 = frappe.db.sql("""SELECT tabAR.student,
					ROUND(((SUM(tabAR.total_score)/600*100)*40/100),2) AS 'MidYear_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.academic_term = "2022 (Term 1)"
					GROUP BY tabAR.student""", ("%%%s%%" % level), as_dict=1)
	
		final_60 = frappe.db.sql("""SELECT tabAR.student, 
					ROUND(((SUM(tabAR.total_score)/600*100)*60/100),2) AS 'Total_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.academic_term = %s
					GROUP BY tabAR.student""", ("%%%s%%" % level, term), as_dict=1)



	#frappe.msgprint(_("Final {0}").format(midyear_40))

	#finalResult = Counter(final_60) + Counter(midyear_40)

	midYeay_40 = pd.DataFrame.from_records(midyear_40)
	finalHalf_60 = pd.DataFrame.from_records(final_60)
	
	gTotal = pd.merge(finalHalf_60, midYeay_40, on='student')

	#gTotal.set_index('student',inplace=True)
	#gtest = gTotal['MidYear_Score']

	gTotal['OverallScore'] = gTotal['Total_Score'] + gTotal['MidYear_Score']

	gTotal['Mark_Rank'] = gTotal['OverallScore'].rank(ascending = 0)

	FinalPosition = gTotal.loc[gTotal.student == student,'Mark_Rank'].values[0]
	
	FinalPosition = "{:.0f}".format(FinalPosition)

	#frappe.msgprint(_("Final {0}").format(gtest))

	return FinalPosition

@frappe.whitelist()
def get_honour_board(student, term):

	program = get_program(student, term)

	if program in ('Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):
	
		honourB = frappe.db.sql("""SELECT ROUND(SUM(tabARD.raw_marks)/(600)*100, 2) AS 'Score' 
					FROM `tabAssessment Result` as tabAR
					LEFT JOIN `tabAssessment Result Detail` AS tabARD
					ON tabAR.name = tabARD.parent
					WHERE tabAR.docstatus = 1
					AND tabAR.student = %s
					AND tabAR.program = %s
					AND tabAR.academic_term = %s
					AND tabAR.honor_board_exempt = 0
					AND tabARD.assessment_criteria = 'Final Exam'""", (student, program, term))
	else:
		honourB = []
	return honourB

def get_program(student, term):
	return frappe.get_value('Program Enrollment', {'student': student, 'academic_term':term}, ['program'])

def totalFunc(ele):
	return ele['MidYear_Total']