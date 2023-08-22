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
    if not filters:
        filters = {}
    columns, data = [], []

    term = filters.get('academic_term')
    program = filters.get('program')
    print_detail = filters.get("printall")
    midyear_common_test = ""

    if program and (program.startswith('Form 1') or program.startswith('Form 2') or program.startswith('Form 3') or program.startswith('Form 4')):
        midyear_common_test = frappe.db.sql("""
            SELECT tabAR.course, tabAR.student, tabAR.student_name, SUM(tabARD.score) AS common_score
                FROM `tabAssessment Result` AS tabAR
                LEFT JOIN `tabAssessment Result Detail` AS tabARD ON tabAR.name = tabARD.parent
                WHERE tabAR.docstatus = 1
                AND tabARD.assessment_criteria IN ('Common Test 1', 'Common Test 2')
                AND tabAR.academic_term = %s
                AND tabAR.program = %s
                GROUP BY tabAR.student""", (term, program), as_dict=True)

        midyear_exam = frappe.db.sql("""
            SELECT tabAR.course, tabAR.student, tabAR.student_name, tabARD.raw_marks, SUM(tabARD.score) as midyear_score
                FROM `tabAssessment Result` AS tabAR
                LEFT JOIN `tabAssessment Result Detail` AS tabARD ON tabAR.name = tabARD.parent
                WHERE tabAR.docstatus = 1
                AND tabARD.assessment_criteria = "Mid Year Exam"
                AND tabAR.academic_term = %s
                AND tabAR.program = %s
                GROUP BY tabAR.student""", (term, program), as_dict=True)

    elif program and (program.startswith('Form 5') or program.startswith('Form 6') or program.startswith('Form 7')):
        midyear_common_test = frappe.db.sql("""
            SELECT tabAR.course, tabAR.student, tabAR.student_name, SUM(tabARD.score) AS common_score
                FROM `tabAssessment Result` AS tabAR
                LEFT JOIN `tabAssessment Result Detail` AS tabARD ON tabAR.name = tabARD.parent
                WHERE tabAR.docstatus = 1
                AND tabAR.not_included = 0
                AND tabARD.assessment_criteria IN ('Common Test 1', 'Common Test 2')
                AND tabAR.academic_term = %s
                AND tabAR.program = %s
                GROUP BY tabAR.student""", (term, program), as_dict=True)

        midyear_exam = frappe.db.sql("""
            SELECT tabAR.course, tabAR.student, tabAR.student_name, tabARD.raw_marks, SUM(tabARD.score) as midyear_score
                FROM `tabAssessment Result` AS tabAR
                LEFT JOIN `tabAssessment Result Detail` AS tabARD ON tabAR.name = tabARD.parent
                WHERE tabAR.docstatus = 1
                AND tabAR.not_included = 0
				AND tabARD.assessment_criteria = "Mid Year Exam"
                AND tabAR.academic_term = %s
                AND tabAR.program = %s
                GROUP BY tabAR.student""", (term, program), as_dict=True)

    else:
        # Handle the case when the program level is not recognized
        frappe.msgprint(_("Invalid program selection"))

    if midyear_common_test and midyear_exam:
        # Convert data to pandas DataFrames and perform data manipulation
        df_common = pd.DataFrame.from_records(midyear_common_test)
        dataframe = pd.DataFrame.from_records(midyear_exam)

        df_common = df_common.pivot_table(index='student_name', values='common_score')
        dataframe = dataframe.pivot_table(index='student_name', values='midyear_score')

        dataframe['common_test'] = df_common['common_score']
        dataframe['Overall'] = df_common['common_score'] + dataframe['midyear_score']
        dataframe['Comments'] = " "
        dataframe['Overall'] = round(dataframe['Overall'], 2)
        if program and (program.startswith('Form 1') or program.startswith('Form 2') or program.startswith('Form 3') or program.startswith('Form 4')):
        	
            dataframe['Percentage'] = (dataframe['Overall'] /800) * 100
        
        elif program and (program.startswith('Form 5') or program.startswith('Form 6') or program.startswith('Form 7')):

            dataframe['Percentage'] = (dataframe['Overall']/600) * 100
        
        dataframe['Percentage'] = round(dataframe['Percentage'], 2)

        dataframe.fillna(0, inplace=True)

        dataframe['Rank'] = dataframe['Percentage'].rank(ascending=0).astype(int)

        dataframe = dataframe.sort_values(by="Rank", ascending=True)

        if print_detail == "TOP 20":
            dataframe = dataframe.iloc[:20]

        columns = [
            {"fieldname": "Rank", "label": _("Position"), "fieldtype": "Int", "width": 80},
            {"fieldname": "student_name", "label": _("Student"), "fieldtype": "Data", "width": 200},
            {"fieldname": "common_test", "label": _("Common Test"), "fieldtype": "Float", "width": 90},
            {"fieldname": "midyear_score", "label": _("Mid Year Exam"), "fieldtype": "Float", "width": 90},
            {"fieldname": "Overall", "label": _("Overall"), "fieldtype": "Float", "width": 90},
            {"fieldname": "Percentage", "label": _("Percentage"), "fieldtype": "Float", "width": 90}
        ]

        data = dataframe.reset_index().to_dict('records')

        return columns, data
    else:
        return [], []


