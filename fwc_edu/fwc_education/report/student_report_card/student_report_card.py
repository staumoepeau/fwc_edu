# Copyright (c) 2023, Sione Taumoepeau and contributors
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
	if not filters:
		filters = {}
	columns, data = [], []

	get_term = filters.get("academic_term")
	program = filters.get("program")
	studentsql = "tabAR.student = '{student}'".format(student=filters.get('student')) if filters.get('student') else "1 = 1"

	if get_term == "2023 (Term 1)":
		
		commonTestSQL = """SELECT tabAR.course as course, tabAR.student, tabAR.student_name,
				SUM(tabARD.score) AS common_score
				FROM `tabAssessment Result` AS tabAR
				LEFT JOIN `tabAssessment Result Detail` AS tabARD ON tabAR.name = tabARD.parent
				WHERE tabAR.docstatus = 1
				AND tabARD.assessment_criteria IN ('Common Test 1', 'Common Test 2')
				AND tabAR.academic_term = '2023 (Term 1)'
				AND ({studentsql})
            GROUP BY tabAR.course, tabAR.student, tabAR.student_name""".format(studentsql=studentsql)

		midYearSQL = """SELECT tabAR.course as course, tabAR.student, tabAR.student_name, tabARD.raw_marks, tabARD.score as midyear_score
			FROM `tabAssessment Result` AS tabAR
			LEFT JOIN `tabAssessment Result Detail` AS tabARD ON tabAR.name = tabARD.parent
			WHERE tabAR.docstatus = 1
			AND tabARD.assessment_criteria = 'Mid Year Exam'
			AND tabAR.academic_term = '2023 (Term 1)'
			AND ({studentsql})
			GROUP BY tabAR.course, tabAR.student, tabAR.student_name""".format(studentsql=studentsql)

		totalSQL = """SELECT tabAR.name, tabAR.course as course, tabAR.student, tabAR.student_name,
			tabAR.grade, tabAR.total_score
			FROM `tabAssessment Result` AS tabAR
			WHERE tabAR.docstatus = 1
			AND tabAR.academic_term = '2023 (Term 1)'
			AND ({studentsql})""".format(studentsql=studentsql)
		
		totalData = frappe.db.sql(totalSQL, as_dict=1)
		commonData = frappe.db.sql(commonTestSQL, as_dict=1)
		midyearData = frappe.db.sql(midYearSQL, as_dict=1)

		df_common = pd.DataFrame.from_records(commonData)
		df_midyear = pd.DataFrame.from_records(midyearData)
		df_midyear_raw = pd.DataFrame.from_records(midyearData)
		df_total = pd.DataFrame.from_records(totalData)
		df_grade = pd.DataFrame.from_records(totalData)

		Subjects = {'English': 1, 'Mathematics': 2, 'Science': 3, 'Biblical': 4, 'Lea Fakatonga': 5, 'Tonga moe Angafakafonua': 6,
					'Tourism and Hospitality': 7, 'Creative Technology': 8, 'Music': 9, 'Accounting': 10, 'Mathematic with Calculus': 11,
					'Mathematic with Statistics': 12, 'Physic': 13, 'Chemistry': 14, 'Biology': 15, 'Computing': 16, 'Economic': 17, 'Geography': 18,
					'History': 19, 'Home Economic': 20, 'Agricultural Science': 21, 'French': 22, 'Tourism and Hospitality': 23, 'Design Technology': 24}

		df_common['Subject_Index'] = df_common['course'].map(Subjects)
		df_midyear['Subject_Index'] = df_midyear['course'].map(Subjects)
		df_midyear_raw['Subject_Index'] = df_midyear_raw['course'].map(Subjects)

		df_total['Subject_Index'] = df_total['course'].map(Subjects)
		df_grade['Subject_Index'] = df_grade['course'].map(Subjects)

		df_total = df_total.pivot_table(index=("Subject_Index", "course"), values='total_score')
		df_grade = df_grade.pivot_table(index=("Subject_Index", "course"), values='grade', aggfunc=lambda x: ','.join(str(v) for v in x))

		df_midyear = df_midyear.pivot_table(index=("Subject_Index", "course"), values='midyear_score')
		df_midyear_raw = df_midyear_raw.pivot_table(index=("Subject_Index", "course"), values='raw_marks')
		df_common = df_common.pivot_table(index=("Subject_Index", "course"), values='common_score')

		dataframe = df_total.copy()
		dataframe['Common Test'] = df_common
		dataframe['Mid Year Exam'] = df_midyear
		dataframe['Mid_Year_Raw_Marks'] = df_midyear_raw
		dataframe['Overall'] = df_total
		dataframe['Grade'] = df_grade
		dataframe['Comments'] = " "

		dataframe.fillna(0, inplace=True)
	#	dataframe['midyear_score'] = dataframe.loc[:, 'Mid Year Exam'] / 70 * 100
	#	dataframe["raw_marks"] = dataframe["raw_marks"].apply(lambda x: round(x, 3))

		columns = [{"fieldname": "course", "label": _("Subjects"), "fieldtype": "Data", "width": 200}]
		columns += [{"fieldname": "Mid_Year_Raw_Marks", "label": _("Mid Year Raw Marks"), "fieldtype": "Data", "width": 150}]
		columns += [{"fieldname": "Mid Year Exam", "label": _("Mid Year Exam"), "fieldtype": "Data", "width": 150}]
		columns += [{"fieldname": "Common Test", "label": _("Common Test"), "fieldtype": "Data", "width": 150}]
		columns += [{"fieldname": "Overall", "label": _("Overall"), "fieldtype": "Data", "width": 100}]
		columns += [{"fieldname": "Grade", "label": _("Grade"), "fieldtype": "Data", "width": 100}]
		columns += [{"fieldname": "Comments", "label": _("Teacher's Comment"), "fieldtype": "Data", "width": 500}]
		
		data = dataframe.reset_index().to_dict('records')
		
	return columns, data