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

	term = filters.get("academic_term")
	formLevel = filters.get("level")
	program = get_program(formLevel)
	subject = filters.get("subject")
	
#	frappe.msgprint(_("MID {0}").format(program))

	if formLevel in ("L1", "L2", "L3", "L4"):
		
		midyear_40 = frappe.db.sql("""SELECT tabAR.student,tabAR.student_name, tabAR.course,
					ROUND(((tabAR.total_score)*40/100), 2) AS 'MidYear_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.course = %s
					AND tabAR.academic_term = "2022 (Term 1)"
					GROUP BY tabAR.student""", ("%%%s%%" % program, subject), as_dict=1)
	
		final_60 = frappe.db.sql("""SELECT tabAR.student,tabAR.student_name, tabAR.course,
					ROUND(((tabAR.total_score)*60/100), 2) AS 'Total_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.academic_term = %s
					AND tabAR.course = %s
					GROUP BY tabAR.student""", ("%%%s%%" % program, term, subject), as_dict=1)
	
	if formLevel in ("L5", "L6", "L7"):

		midyear_40 = frappe.db.sql("""SELECT tabAR.student,tabAR.student_name,tabAR.course,
					ROUND(((tabAR.total_score)*40/100), 2) AS 'MidYear_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.course = %s
					AND tabAR.academic_term = "2022 (Term 1)"
					GROUP BY tabAR.student""", ("%%%s%%" % program, subject), as_dict=1)
	
		final_60 = frappe.db.sql("""SELECT tabAR.student,tabAR.student_name,tabAR.course,
					ROUND(((tabAR.total_score)*60/100), 2) AS 'Total_Score'
					FROM `tabAssessment Result` as tabAR
					WHERE tabAR.docstatus = 1
					AND tabAR.not_included = 0
					AND tabAR.program LIKE %s
					AND tabAR.academic_term = %s
					AND tabAR.course = %s
					GROUP BY tabAR.student""", ("%%%s%%" % program, term, subject), as_dict=1)
	
#	frappe.msgprint(_("Group {0}").format(subject))
#	frappe.msgprint(_("MID {0}").format(midyear_40))
#	frappe.msgprint(_("FINAL {0}").format(final_60))
	
	dataframe = pd.DataFrame.from_records(midyear_40)
	df_total = pd.DataFrame.from_records(final_60)

	df_total = df_total.pivot_table(index=('student_name'), values='Total_Score')
#	lessons = dataframe.course.unique().tolist()
	dataframe = dataframe.pivot_table(index=('student_name'), values=('MidYear_Score'))

	dataframe['Overall'] = df_total['Total_Score'] + dataframe['MidYear_Score']

	dataframe['Comments'] = " "
	
	dataframe['FinalSecond'] = dataframe['Overall'] - dataframe['MidYear_Score']

	dataframe['FinalSecond'] = round(dataframe['FinalSecond'], 2)

	dataframe['Overall'] = round(dataframe['Overall'] ,2)
	dataframe.fillna(0, inplace = True)

	dataframe = dataframe.sort_values(by="Overall", ascending=False)
	
	dataframe = dataframe.iloc[:20]

	columns = [ { "fieldname": "rank", "label": _("Position"), "fieldtype": "Data", "width": 200 }]
	columns = [ { "fieldname": "student_name", "label": _("Student"), "fieldtype": "Data", "width": 200 }]
	
	columns+=[ { "fieldname": "MidYear_Score", "label": _("Mid Year 40%"), "fieldtype": "Float", "width": 100 }]

	columns+=[ { "fieldname": "FinalSecond", "label": _("Second Half 60%"), "fieldtype": "Float", "width": 100 }]

	columns+=[ { "fieldname": "Overall", "label": _("Overall"), "fieldtype": "Float", "width": 100 }]

	data = dataframe.reset_index().to_dict('records')



	return columns, data


def get_program(level):
	
	if level == "L1":
		return "Form 1"
	if level == "L2":
		return "Form 2"
	if level == "L3":
		return "Form 3"
	if level == "L4":
		return "Form 4"
	if level == "L5":
		return "Form 5"
	if level == "L6":
		return "Form 6"
	if level == "L7":
		return "Form 7"
	
