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
#	if program in ('Form 5K','Form 5L','Form 5M','Form 5S','Form 5T','Form 5V',
#		'Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):
	if program.startswith('Form 5') or program.startswith('Form 6') or program.startswith('Form 7'):
		
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

	return total_score[0][0] if total_score else None


@frappe.whitelist()
def get_midyear_score(student, term):
	#*******Get students assessment results as list of dictionary

	program = get_program(student, term)
	#if program in ('Form 5K','Form 5L','Form 5M','Form 5S','Form 5T','Form 5V',
	#	'Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):
	if program and (program.startswith('Form 5') or program.startswith('Form 6') or program.startswith('Form 7')):

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
    program = get_program(student, term)

    totalClass = frappe.db.sql("""SELECT COUNT(*)
        FROM `tabProgram Enrollment`
        WHERE company = 'Queen Salote College'
        AND program = %s
        AND docstatus = 1
        AND academic_term = %s""", (program, term))

    classTotal = totalClass[0][0]

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
        GROUP BY tabAR.student""", (program, term), as_dict=True)

    overall_position = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name,
        SUM(tabAR.total_score) AS 'Overall_Total'
        FROM `tabAssessment Result` as tabAR
        WHERE tabAR.docstatus = 1
        AND tabAR.not_included = 0
        AND tabAR.program = %s
        AND tabAR.academic_term = %s
        GROUP BY tabAR.student""", (program, term), as_dict=True)

    overalData = pd.DataFrame.from_records(overall_position)
    
    if program and (program.startswith('Form 1') or program.startswith('Form 2') or program.startswith('Form 3') or program.startswith('Form 4')):
        	
        overalData['Percentage'] = (overalData['Overall_Total'] /800) * 100
        
    elif program and (program.startswith('Form 5') or program.startswith('Form 6') or program.startswith('Form 7')):

        overalData['Percentage'] = (overalData['Overall_Total']/600) * 100


    overalData['Mark_Rank'] = overalData['Percentage'].rank(ascending=0).astype(int)

    dataMidyear = pd.DataFrame.from_records(midyear_position)
    dataMidyear['Mark_Rank'] = dataMidyear['MidYear_Total'].rank(ascending=0)

    # If the student's data is not found in the DataFrames, set their ranks to NaN
    overallPosition = overalData.loc[overalData.student == student, 'Mark_Rank'].values
    overallPosition = overallPosition[0] if overallPosition else float('nan')

    midYearPosition = dataMidyear.loc[dataMidyear.student == student, 'Mark_Rank'].values
    midYearPosition = midYearPosition[0] if midYearPosition else float('nan')

    # Round the ranks to integers and convert them to strings for consistent formatting
    midYear = "{:.0f}".format(midYearPosition)
    overallPosition = "{:.0f}".format(overallPosition)

    return midYear, overallPosition, classTotal


def get_program(student, term):
	return frappe.get_value('Program Enrollment', {'student': student, 'academic_term':term}, ['program'])

def totalFunc(ele):
	return ele['MidYear_Total']
