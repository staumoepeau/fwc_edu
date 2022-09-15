# Copyright (c) 2022, Sione Taumoepeau and contributors
# For license information, please see license.txt

# import frappe


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

	#levelSQL = "tabAR.program LIKE '{%level%}'".format(program=filters.level) if filters.level else "1 = 1"

#	if filters.program in ('Form 1S', 'Form 1M'):
#	programSQL = "tabAR.program LIKE 'Form 1%'.format(program=filters.program)"
#	getProgram = frappe.db.get_value('Student Group', {'name': groupSQL}, ['program'])
#	getCourse = frappe.db.get_value('Student Group', {'name': groupSQL}, ['course'])

	QSCclass = filters.get("program")


	if QSCclass not in ('Form 5K','Form 5L','Form 5M','Form 5S','Form 5T','Form 5V',
		'Form 6K','Form 6M','Form 6S','Form 6T','Form 7A','Form 7L'):
#			frappe.msgprint(_("LOWER {0}").format(QSCclass))
			studentList = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name, tabAR.course,
					tabAR.total_score
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					""", QSCclass, as_dict=1)

			totalSQL = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name, tabAR.course,
					ROUND(SUM(tabAR.total_score)/(800)*100, 1) AS 'total_score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					GROUP BY tabAR.student
					""", QSCclass, as_dict=1)
	else:	
#			frappe.msgprint(_("UPPER {0}").format(QSCclass))
			studentList = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name, tabAR.course,
					tabAR.total_score
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					""", QSCclass, as_dict=1)

			totalSQL = frappe.db.sql("""SELECT tabAR.student, tabAR.student_name, tabAR.course,
					ROUND(SUM(tabAR.total_score)/(600)*100, 1) AS 'total_score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program = %s
					GROUP BY tabAR.student
					""",QSCclass, as_dict=1)
	
		
#	dataTotal = frappe.db.sql(totalSQL, as_dict=1)
#	data = frappe.db.sql(studentList, as_dict=1)

	dataframe = pd.DataFrame.from_records(studentList)
	df_total = pd.DataFrame.from_records(totalSQL)

	#df_total['Mark_Rank'] = df_total['total_score'].rank(ascending = 0)
	
	frappe.msgprint(_("Dataframe {0}").format(df_total))
	#dataframe = dataframe.set_index('Overall')

	df_total = df_total.pivot_table(index=('student_name'), values='total_score')
#	df_grade = df_grade.pivot_table(index='student_name', values='grade',aggfunc = lambda x: ','.join(str(v) for v in x))
#	frappe.msgprint(_("Dataframe {0}").format(df_total))
	#lessons = dataframe.course.unique().tolist()

	dataframe = dataframe.pivot_table(index=('student_name'), columns="course", values=('total_score'))
	
	dataframe['Overall'] = df_total
#	dataframe['Grade'] = df_grade
	dataframe['Comments'] = " "
	
	dataframe.fillna(0, inplace = True)
#	dataframe['raw_marks'] = dataframe.loc[:, 'Mid Year Exam'] / 70 * 100
	#dataframe = dataframe.sort_index(), ascending=[0])
#	dataframe["raw_marks"] = dataframe["raw_marks"].apply(lambda x: round(x, 2))
	dataframe = dataframe.sort_values(by="Overall", ascending=False)
#	dataframe = dataframe.iloc[:20]

	#lessons = [{"fieldname": course, "label": _(course), "fieldtype": "Data", "width": 100, } for course in lessons]

	columns = [ { "fieldname": "student_name", "label": _("Student"), "fieldtype": "Data", "width": 200 }]
#	columns += [ { "fieldname": "Overall_Total", "label": _("Overall"), "fieldtype": "Data", "width": 150 }]
#	columns += 
	columns+=[ { "fieldname": "Comments", "label": _("Comment"), "fieldtype": "Data", "width": 500}]
	columns+=[ { "fieldname": "Overall", "label": _("Overall"), "fieldtype": "Data", "width": 100 }]


#	frappe.msgprint(_("Column {0}").format(columns))
#	columns += [ { "fieldname": "assessment_criteria", "label": _("Assessment"), "fieldtype": "Data", "width": 200 }]
	data = dataframe.reset_index().to_dict('records')

	return columns, data