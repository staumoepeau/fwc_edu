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

	#programSQL = "tabAR.program = '{program}'".format(program=filters.program) if filters.program else "1 = 1"

#	if filters.program in ('Form 1S', 'Form 1M'):
#	programSQL = "tabAR.program LIKE 'Form 1%'.format(program=filters.program)"
#	getProgram = frappe.db.get_value('Student Group', {'name': groupSQL}, ['program'])
#	getCourse = frappe.db.get_value('Student Group', {'name': groupSQL}, ['course'])


	studentList = """SELECT tabAR.student, tabAR.student_name, tabAR.course,
			tabAR.total_score, tabAR.total_score as 'mark_index'
			FROM `tabAssessment Result` as tabAR
			WHERE tabAR .docstatus = 1
			AND tabAR.not_included = 0
			AND tabAR.program LIKE 'Form 1%'		
			"""
	
#	frappe.msgprint(_("GetValue {0}").format(studentList))
	

	totalSQL = """SELECT tabAR.student, tabAR.student_name, tabAR.course,
			tabAR.total_score, tabAR.total_score as 'mark_index'
			FROM `tabAssessment Result` as tabAR
			WHERE tabAR .docstatus = 1
			AND tabAR.not_included = 0
			AND tabAR.program LIKE 'Form 1%'
			"""

	dataTotal = frappe.db.sql(totalSQL, as_dict=1)
	data = frappe.db.sql(studentList, as_dict=1)
	dataframe = pd.DataFrame.from_records(data)
	df_total = pd.DataFrame.from_records(dataTotal)

#	frappe.msgprint(_("Dataframe {0}").format(df_total))
	#dataframe = dataframe.set_index('Overall')

	df_total = df_total.pivot_table(index=('mark_index','student_name'), values='total_score')
#	df_grade = df_grade.pivot_table(index='student_name', values='grade',aggfunc = lambda x: ','.join(str(v) for v in x))
#	frappe.msgprint(_("Dataframe {0}").format(dataframe))
	lessons = dataframe.course.unique().tolist()

	dataframe = dataframe.pivot_table(index=('mark_index','student_name'), columns="course", values=('total_score'))
	
	dataframe['Overall'] = df_total
#	dataframe['Grade'] = df_grade
#	dataframe['Comments'] = " "
	
	dataframe.fillna(0, inplace = True)
#	dataframe['raw_marks'] = dataframe.loc[:, 'Mid Year Exam'] / 70 * 100
	dataframe = dataframe.sort_index(), ascending=[0])
#	dataframe["raw_marks"] = dataframe["raw_marks"].apply(lambda x: round(x, 2))
	
	lessons = [{"fieldname": course, "label": _(course), "fieldtype": "Data", "width": 200, } for course in lessons]
	columns = [ { "fieldname": "student_name", "label": _("Student"), "fieldtype": "Data", "width": 200 }]
#	columns += [ { "fieldname": "Overall_Total", "label": _("Overall"), "fieldtype": "Data", "width": 150 }]
	columns += lessons
	columns+=[ { "fieldname": "Overall", "label": _("Overall"), "fieldtype": "Data", "width": 100 }]
#	columns+=[ { "fieldname": "Grade", "label": _("Grade"), "fieldtype": "Data", "width": 100 }]
#	columns+=[ { "fieldname": "Comments", "label": _("Teacher's Comment"), "fieldtype": "Data", "width": 500}]


#	frappe.msgprint(_("Column {0}").format(columns))
#	columns += [ { "fieldname": "assessment_criteria", "label": _("Assessment"), "fieldtype": "Data", "width": 200 }]
	data = dataframe.reset_index().to_dict('records')
#	data = dataframe.reset_index(drop=True)

	return columns, data