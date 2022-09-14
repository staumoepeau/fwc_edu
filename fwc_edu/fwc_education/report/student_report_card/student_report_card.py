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

	studentsql = "tabAR.student = '{student}'".format(student=filters.student) if filters.student else "1 = 1"

#	academic_yearsql = "tabAR.academic_year = '{academic_year}'".format(academic_year=filters.academic_year) if filters.academic_year else "1 = 1"
#	academic_termsql = "tabAR.academic_term = '{academic_term}'".format(academic_term=filters.academic_term) if filters.academic_term else "1 = 1"
#	programsql = "tabAR.program = '{program}'".format(program=filters.program) if filters.program else "1 = 1"


	#programSQL = """
	#			SELECT program
	#			FROM `tabProgram Enrollment`
	#			WHERE ({studentsql})""".format(studentsql = studentsql)

	
	#getProgram = functools.reduce(lambda sub, ele: sub * 10 + ele, programSQL)
	#frappe.msgprint(_("Data {0}").format(getProgram))


	scoreSQL = """
		SELECT tabAR.name, tabAR.course, tabAR.student, tabAR.student_name,
		tabARD.assessment_criteria, tabARD.maximum_score, 
		tabARD.score, tabARD.raw_marks, tabARD.total_raw_marks, tabARD.grade
		FROM `tabAssessment Result` AS tabAR
		LEFT JOIN `tabAssessment Result Detail` AS tabARD
		ON tabAR.name = tabARD.parent
		WHERE tabAR.docstatus = 1
		AND ({studentsql})
		ORDER BY tabARD.assessment_criteria DESC""".format(studentsql = studentsql)
	
	totalSQL = """
		SELECT tabAR.name, tabAR.course, tabAR.student, tabAR.student_name,
		tabAR.grade, tabAR.total_score
		FROM `tabAssessment Result` AS tabAR
		WHERE tabAR.docstatus = 1
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
				'Accounting' : 10, 'Mathematic with Calculus' : 11, 'StatisticBiology' : 12, 'Physic' : 13, 'Chemistry' : 14, 'Biology' : 15, 'Computing' : 16, 'Economic' : 17, 'Geography' :18,
				'History' : 19, 'Home Economic' : 20, 'Agricultural' : 21, 'French' : 22, 'Tourism and Hospitality' : 23}
	
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
	
	dataframe["raw_marks"] = dataframe["raw_marks"].apply(lambda x: round(x, 2))

	assessments = [{"fieldname": assessment_criteria, "label": _(assessment_criteria), "fieldtype": "Data", "width": 200, } for assessment_criteria in assessments]
	columns = [ { "fieldname": "course", "label": _("Subjects"), "fieldtype": "Data", "width": 200 }]
	columns += [ { "fieldname": "raw_marks", "label": _("Raw Marks"), "fieldtype": "Data", "width": 150 }]
	columns += assessments
	columns+=[ { "fieldname": "Overall", "label": _("Overall"), "fieldtype": "Data", "width": 100 }]
	columns+=[ { "fieldname": "Grade", "label": _("Grade"), "fieldtype": "Data", "width": 100 }]
	columns+=[ { "fieldname": "Comments", "label": _("Teacher's Comment"), "fieldtype": "Data", "width": 500}]


#	frappe.msgprint(_("Column {0}").format(columns))
#	columns += [ { "fieldname": "assessment_criteria", "label": _("Assessment"), "fieldtype": "Data", "width": 200 }]
	data = dataframe.reset_index().to_dict('records')
#	data = dataframe.reset_index(drop=True)
	return columns, data
