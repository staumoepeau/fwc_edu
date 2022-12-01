# Copyright (c) 2022, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from itertools import groupby
import json
import time
import math
import ast
import os.path
import sys
import datetime
import pandas as pd
import numpy as np
import functools

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

	get_term = filters.get("academic_term")
	program = filters.get("program")
	studentsql = "tabAR.student = '{student}'".format(student=filters.student) if filters.student else "1 = 1"

	if get_term == "2022 (Term 1)":
		scoreSQL = """
			SELECT tabAR.name, tabAR.course, tabAR.student, tabAR.student_name,
			tabARD.assessment_criteria, tabARD.maximum_score, 
			tabARD.score, tabARD.raw_marks, tabARD.total_raw_marks, tabARD.grade
			FROM `tabAssessment Result` AS tabAR
			LEFT JOIN `tabAssessment Result Detail` AS tabARD
			ON tabAR.name = tabARD.parent
			WHERE tabAR.docstatus = 1
			AND tabARD.assessment_criteria IN ('Common Test','Mid Year Exam')
			AND ({studentsql})
			ORDER BY tabARD.assessment_criteria DESC""".format(studentsql = studentsql)
		
		totalSQL = """
			SELECT tabAR.name, tabAR.course, tabAR.student, tabAR.student_name,
			tabAR.grade, tabAR.total_score
			FROM `tabAssessment Result` AS tabAR
			WHERE tabAR.docstatus = 1
			AND tabAR.academic_term = '2022 (Term 1)'
			AND ({studentsql})""".format(studentsql = studentsql)

		totalData = frappe.db.sql(totalSQL, as_dict=1)
		data = frappe.db.sql(scoreSQL, as_dict=1)
	#	frappe.msgprint(_("Data {0}").format(data))

		
		dataframe = pd.DataFrame.from_records(data)
		df_total = pd.DataFrame.from_records(totalData)
		df_grade = pd.DataFrame.from_records(totalData)

		
	#	frappe.msgprint(_("Dataframe {0}").format(dataframe))
		assessments = dataframe.assessment_criteria.unique().tolist()
		
		Subjects = {'English' : 1, 'Mathematics' : 2, 'Science' : 3, 'Biblical': 4, 'Lea Fakatonga' : 5, 'Tonga moe Angafakafonua' : 6, 'Tourism and Hospitality' : 7, 'Creative Technology' : 8, 'Music' : 9,
					'Accounting' : 10, 'Mathematic with Calculus' : 11, 'Statistic' : 12, 'Physic' : 13, 'Chemistry' : 14, 'Biology' : 15, 'Computing' : 16, 'Economic' : 17, 'Geography' :18,
					'History' : 19, 'Home Economic' : 20, 'Agricultural' : 21, 'French' : 22, 'Tourism and Hospitality' : 23,
					'Design Technology' : 24}
		
		dataframe['Subject_Index'] = dataframe['course'].map(Subjects)
		
		#dataframe = dataframe.set_index('Subject_Index')
		#dataframe = dataframe.sort_index()

		#frappe.msgprint(_("Column {0}").format(dataframe))

		df_total['Subject_Index'] = df_total['course'].map(Subjects)
		df_grade['Subject_Index'] = df_grade['course'].map(Subjects)

		df_total = df_total.pivot_table(index=("Subject_Index", "course"), values='total_score')
		df_grade = df_grade.pivot_table(index=("Subject_Index", "course"), values='grade',aggfunc = lambda x: ','.join(str(v) for v in x))

	#	frappe.msgprint(_("Column {0}").format(dataframe))

		dataframe = dataframe.pivot_table(index=("Subject_Index", "course"), columns="assessment_criteria", values=('score'))
		
		dataframe['Overall'] = df_total
		dataframe['Grade'] = df_grade
		dataframe['Comments'] = " "
		
	#	frappe.msgprint(_("Column {0}").format(dataframe))

		dataframe.fillna(0, inplace = True)
		dataframe['raw_marks'] = dataframe.loc[:, 'Mid Year Exam'] / 70 * 100
		
		dataframe["raw_marks"] = dataframe["raw_marks"].apply(lambda x: round(x, 3))

		assessments = [{"fieldname": assessment_criteria, "label": _(assessment_criteria), "fieldtype": "Data", "width": 200, } for assessment_criteria in assessments]
		columns = [ { "fieldname": "course", "label": _("Subjects"), "fieldtype": "Data", "width": 200 }]
		columns += [ { "fieldname": "raw_marks", "label": _("Raw Marks"), "fieldtype": "Data", "width": 150 }]
		columns += assessments
		columns+=[ { "fieldname": "Overall", "label": _("Overall"), "fieldtype": "Data", "width": 100 }]
		columns+=[ { "fieldname": "Grade", "label": _("Grade"), "fieldtype": "Data", "width": 100 }]
		columns+=[ { "fieldname": "Comments", "label": _("Teacher's Comment"), "fieldtype": "Data", "width": 500}]

		data = dataframe.reset_index().to_dict('records')


	if get_term == "2022 (Term 4)":

		scoreSQL = """
			SELECT tabAR.name, tabAR.course, tabAR.student, tabAR.student_name,
			tabARD.assessment_criteria, tabARD.maximum_score, 
			tabARD.score, tabARD.raw_marks, tabARD.total_raw_marks, tabARD.grade
			FROM `tabAssessment Result` AS tabAR
			LEFT JOIN `tabAssessment Result Detail` AS tabARD
			ON tabAR.name = tabARD.parent
			WHERE tabAR.docstatus = 1
			AND tabARD.assessment_criteria IN ('Common Test Final','Final Exam')
			AND ({studentsql})
			ORDER BY tabARD.assessment_criteria DESC""".format(studentsql = studentsql)
		
		totalSQL = """
			SELECT tabAR.name, tabAR.course, tabAR.student, tabAR.student_name,
			tabAR.grade, tabAR.total_score
			FROM `tabAssessment Result` AS tabAR
			WHERE tabAR.docstatus = 1
			AND tabAR.academic_term = '2022 (Term 4)'
			AND ({studentsql})""".format(studentsql = studentsql)
		
		MidYear_totalSQL = """
			SELECT tabAR.name, tabAR.course, tabAR.student, tabAR.student_name,
			tabAR.grade, tabAR.total_score
			FROM `tabAssessment Result` AS tabAR
			WHERE tabAR.docstatus = 1
			AND tabAR.academic_term = '2022 (Term 1)'
			AND ({studentsql})""".format(studentsql = studentsql)

		totalData = frappe.db.sql(totalSQL, as_dict=1)
		Midyear_totalData = frappe.db.sql(MidYear_totalSQL, as_dict=1)
		data = frappe.db.sql(scoreSQL, as_dict=1)
	#	frappe.msgprint(_("Data {0}").format(data))

		dataframe = pd.DataFrame.from_records(data)
		df_total = pd.DataFrame.from_records(totalData)
		df_midyear_total = pd.DataFrame.from_records(Midyear_totalData)
		df_grade = pd.DataFrame.from_records(totalData)
		
	#	frappe.msgprint(_("Dataframe {0}").format(dataframe))
		assessments = dataframe.assessment_criteria.unique().tolist()
		
		Subjects = {'English' : 1, 'Mathematics' : 2, 'Science' : 3, 'Biblical': 4, 'Lea Fakatonga' : 5, 'Tonga moe Angafakafonua' : 6, 'Tourism and Hospitality' : 7, 'Creative Technology' : 8, 'Music' : 9,
					'Accounting' : 10, 'Mathematic with Calculus' : 11, 'Statistic' : 12, 'Physic' : 13, 'Chemistry' : 14, 'Biology' : 15, 'Computing' : 16, 'Economic' : 17, 'Geography' :18,
					'History' : 19, 'Home Economic' : 20, 'Agricultural' : 21, 'French' : 22, 'Tourism and Hospitality' : 23}
		
		dataframe['Subject_Index'] = dataframe['course'].map(Subjects)
		
		#dataframe = dataframe.set_index('Subject_Index')
		#dataframe = dataframe.sort_index()

		#frappe.msgprint(_("Column {0}").format(dataframe))

		df_total['Subject_Index'] = df_total['course'].map(Subjects)
		df_midyear_total['Subject_Index'] = df_midyear_total['course'].map(Subjects)
		df_grade['Subject_Index'] = df_grade['course'].map(Subjects)

		df_total = df_total.pivot_table(index=("Subject_Index", "course"), values='total_score')
		df_midyear_total = df_midyear_total.pivot_table(index=("Subject_Index", "course"), values='total_score')
		df_grade = df_grade.pivot_table(index=("Subject_Index", "course"), values='grade',aggfunc = lambda x: ','.join(str(v) for v in x))

	#	frappe.msgprint(_("Column {0}").format(dataframe))

		dataframe = dataframe.pivot_table(index=("Subject_Index", "course"), columns="assessment_criteria", values=('score'))
		
		dataframe['MidYear_40'] = round((df_midyear_total * 40/100), 2)
		dataframe['Final_60'] = round((df_total * 60/100), 2)
		dataframe['Total_Overall'] = round(dataframe['MidYear_40'] + dataframe['Final_60'], 2)
		dataframe['Overall'] = round(df_total, 2)
	#	dataframe['Grade'] = df_grade
		dataframe['Comments'] = " "

	#	totalOverall = dataframe['Overall']

	#	frappe.msgprint(_("Column {0}").format(dataframe[dataframe['Overall']]))
		
		dataframe.fillna(0, inplace = True)

		dataframe['raw_marks'] = round(dataframe.loc[:, 'Final Exam'] / 70 * 100, 2)
		
		dataframe["raw_marks"] = dataframe["raw_marks"].apply(lambda x: round(x, 3))

		score_bins = [0, 50, 56, 70, 75, 80, 90, 100]
		letter_grades =['NA', 'C', 'C+','B','B+','A','A+']

		letter_cats = pd.cut(dataframe['Total_Overall'], score_bins, labels=letter_grades)

		dataframe['Grade'] = letter_cats

		dataframe['Grade'] = dataframe['Grade'].cat.add_categories('NULL')
		dataframe['Grade'].fillna('NULL', inplace = True)

		assessments = [{"fieldname": assessment_criteria, "label": _(assessment_criteria), "fieldtype": "Data", "width": 200, } for assessment_criteria in assessments]
		columns = [ { "fieldname": "course", "label": _("Subjects"), "fieldtype": "Data", "width": 200 }]
		
		if program in ('Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):
			columns += [ { "fieldname": "raw_marks", "label": _("Raw Marks"), "fieldtype": "Data", "width": 150 }]
		
		columns += assessments
		columns+=[ { "fieldname": "Overall", "label": _("Final Overall"), "fieldtype": "Data", "width": 100 }]
		columns+=[ { "fieldname": "Final_60", "label": _("Final 60%"), "fieldtype": "Data", "width": 100 }]
		columns+=[ { "fieldname": "MidYear_40", "label": _("Mid Year 40%"), "fieldtype": "Data", "width": 100 }]
		columns+=[ { "fieldname": "Total_Overall", "label": _("TOTAL"), "fieldtype": "Data", "width": 100 }]
		columns+=[ { "fieldname": "Grade", "label": _("Grade"), "fieldtype": "Data", "width": 100 }]
		columns+=[ { "fieldname": "Comments", "label": _("Teacher's Comment"), "fieldtype": "Data", "width": 500}]

		data = dataframe.reset_index().to_dict('records')

	return columns, data