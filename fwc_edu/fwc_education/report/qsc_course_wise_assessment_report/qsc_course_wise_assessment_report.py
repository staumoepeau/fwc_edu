# Copyright (c) 2022, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from itertools import groupby
import sys
import datetime
import pandas as pd
import xlsxwriter
import openpyxl 
import numpy as np

from openpyxl import load_workbook
from frappe import _, msgprint, utils
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, datetime, comma_and
from collections import defaultdict
from werkzeug.wrappers import Response
import frappe, erpnext
from collections import defaultdict


def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []

	#groupSQL = filters.student_group_name
	
	#schoolTerm = "tabAR.academic_term = '{academic_term}'".format(academic_term=filters.academic_term) if filters.academic_term else "1 = 1"
	studentGroupSQL = "tabAR.student_group = '{student_group}'".format(student_group=filters.student_group) if filters.student_group else "1 = 1"
	schoolTerm = filters.get("academic_term")
#	getProgram = frappe.db.get_value('Student Group', {'name': groupSQL}, ['program'])
#	getCourse = frappe.db.get_value('Student Group', {'name': groupSQL}, ['course'])

	
	if schoolTerm == "2022 (Term 1)":
		studentList = """SELECT tabAR.student_group, tabAR.course, tabAR.student, tabAR.student_name,
				tabARD.assessment_criteria, tabARD.maximum_score, 
				tabARD.score, tabARD.raw_marks, tabARD.total_raw_marks, tabARD.grade
				FROM `tabAssessment Result` AS tabAR
				LEFT JOIN `tabAssessment Result Detail` AS tabARD
				ON tabAR.name = tabARD.parent
				WHERE tabAR.docstatus = 1
				AND tabAR.assessment_group = "QSC2002-T1"
				AND ({studentGroupSQL})
				ORDER BY tabARD.assessment_criteria DESC""".format(studentGroupSQL = studentGroupSQL)

		totalSQL = """SELECT tabAR.name, tabAR.student_group, tabAR.course, tabAR.student, tabAR.academic_term,
				tabAR.student_name, tabAR.grade, tabAR.total_score
				FROM `tabAssessment Result` AS tabAR
				WHERE tabAR.docstatus = 1
				AND tabAR.assessment_group = "QSC2002-T1"
				AND ({studentGroupSQL})
				""".format(studentGroupSQL = studentGroupSQL)

	if schoolTerm == "2022 (Term 4)":
		studentList = """SELECT tabAR.student_group, tabAR.course, tabAR.student, tabAR.student_name,
				tabARD.assessment_criteria, tabARD.maximum_score, 
				tabARD.score, tabARD.raw_marks, tabARD.total_raw_marks, tabARD.grade
				FROM `tabAssessment Result` AS tabAR
				LEFT JOIN `tabAssessment Result Detail` AS tabARD
				ON tabAR.name = tabARD.parent
				WHERE tabAR.docstatus = 1
				AND tabAR.assessment_group = "QSC2002-T4"
				AND ({studentGroupSQL})
				ORDER BY tabARD.assessment_criteria DESC""".format(studentGroupSQL = studentGroupSQL)
	

		totalSQL = """SELECT tabAR.name, tabAR.student_group, tabAR.course, tabAR.student, tabAR.academic_term,
				tabAR.student_name, tabAR.grade, tabAR.total_score
				FROM `tabAssessment Result` AS tabAR
				WHERE tabAR.docstatus = 1
				AND tabAR.assessment_group = "QSC2002-T4"
				AND ({studentGroupSQL})
				""".format(studentGroupSQL = studentGroupSQL)

#	frappe.msgprint(_("Term {0}").format(schoolTerm))

	data = frappe.db.sql(studentList, as_dict=1)
	totalData = frappe.db.sql(totalSQL, as_dict=1)

	dataframe = pd.DataFrame.from_records(data)
	df_total = pd.DataFrame.from_records(totalData)
	df_grade = pd.DataFrame.from_records(totalData)

#	frappe.msgprint(_("Dataframe {0}").format(df_total))

	df_total = df_total.pivot_table(index='student_name', values='total_score')
	df_grade = df_grade.pivot_table(index='student_name', values='grade',aggfunc = lambda x: ','.join(str(v) for v in x))
#	frappe.msgprint(_("Dataframe {0}").format(dataframe))
	assessments = dataframe.assessment_criteria.unique().tolist()

	dataframe = dataframe.pivot_table(index="student_name", columns="assessment_criteria", values=('score'))
	
	dataframe['Overall'] = df_total
	dataframe['Grade'] = df_grade
	dataframe['Comments'] = " "
	
	dataframe.fillna(0, inplace = True)

	if schoolTerm == "2022 (Term 1)":
		dataframe['raw_marks'] = dataframe.loc[:, 'Mid Year Exam'] / 70 * 100
	
	if schoolTerm == "2022 (Term 4)":
		dataframe['raw_marks'] = dataframe.loc[:, 'Final Exam'] / 70 * 100

	dataframe["raw_marks"] = dataframe["raw_marks"].apply(lambda x: round(x, 2))

	assessments = [{"fieldname": assessment_criteria, "label": _(assessment_criteria), "fieldtype": "Data", "width": 200, } for assessment_criteria in assessments]
	columns = [ { "fieldname": "student_name", "label": _("Student"), "fieldtype": "Data", "width": 200 }]
	columns += [ { "fieldname": "raw_marks", "label": _("Raw Marks"), "fieldtype": "Data", "width": 150 }]
	columns += assessments
	columns+=[ { "fieldname": "Overall", "label": _("Overall"), "fieldtype": "Data", "width": 100 }]
	columns+=[ { "fieldname": "Grade", "label": _("Grade"), "fieldtype": "Data", "width": 100 }]
#	columns+=[ { "fieldname": "Comments", "label": _("Teacher's Comment"), "fieldtype": "Data", "width": 500}]


#	frappe.msgprint(_("Column {0}").format(columns))
#	columns += [ { "fieldname": "assessment_criteria", "label": _("Assessment"), "fieldtype": "Data", "width": 200 }]
	data = dataframe.reset_index().to_dict('records')
#	data = dataframe.reset_index(drop=True)

	return columns, data
