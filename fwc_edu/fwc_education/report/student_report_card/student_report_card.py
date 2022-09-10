# Copyright (c) 2022, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import json
import time
import math
import ast
import os.path
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
	columns, data = [], []

	studentsql = "tabAR.student = '{student}'".format(student=filters.student) if filters.student else "1 = 1"
#	companysql = "tbf.company = '{company}'".format(company=filters.company) if filters.company else "1 = 1"
	academic_yearsql = "tabAR.academic_year = '{academic_year}'".format(academic_year=filters.academic_year) if filters.academic_year else "1 = 1"
	academic_termsql = "tabAR.academic_term = '{academic_term}'".format(academic_term=filters.academic_term) if filters.academic_term else "1 = 1"
#	programsql = "tabAR.program = '{program}'".format(program=filters.program) if filters.program else "1 = 1"

	reportSQL = """
		SELECT tabAR.name, tabAR.assessment_plan, tabAR.program, tabAR.course, tabAR.academic_year, 
		tabAR.academic_term, tabAR.student, tabAR.student_name,
		tabARD.parent, tabARD.parenttype, tabARD.assessment_criteria, tabARD.maximum_score, 
		tabARD.score, tabARD.raw_marks, tabARD.total_raw_marks, tabARD.grade
		FROM `tabAssessment Result` AS tabAR
		LEFT JOIN `tabAssessment Result Detail` AS tabARD
		ON tabAR.name = tabARD.parent
		WHERE tabAR.docstatus = 1
		AND ({studentsql})""".format(studentsql = studentsql)

	frappe.msgprint(_("Data {0}").format(reportSQL))
	data = frappe.db.sql(reportSQL, as_dict=1)

	
	dataframe = pd.DataFrame.from_records(data)

	dataframe = dataframe.pivot_table(index=["course"], columns="assessment_criteria", values=["maximum_score","score","raw_marks","total_raw_marks"])
	dataframe.fillna(0, inplace = True)

	columns = [ { "fieldname": "course", "label": _("Subjects"), "fieldtype": "Data", "width": 200 }]
	columns += [ { "fieldname": "assessment_criteria", "label": _("Assessment"), "fieldtype": "Data", "width": 200 }]

	data = dataframe.reset_index().to_dict('records')
	return columns, data

