# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import pandas as pd
import numpy as np

def execute(filters=None):
	columns, data = [], []

	companysql = "tbf.company = '{company}'".format(company=filters.company) if filters.company else "1 = 1"
	academic_yearsql = "tbf.academic_year = '{academic_year}'".format(academic_year=filters.academic_year) if filters.academic_year else "1 = 1"
	programsql = "tbf.program = '{program}'".format(program=filters.program) if filters.program else "1 = 1"
	
	feessql = """
	SELECT
		tbf.student, tbf.student_name, tbs.gender, tbf.program, 
		tbf.academic_term, tbf.grand_total AS total_amount,
		tbf.outstanding_amount AS amount
	FROM
	`tabFees` tbf, `tabStudent` tbs
	WHERE tbf.student = tbs.name
	AND tbf.docstatus = 1
	AND ({companysql})
	AND ({academic_yearsql})
	AND ({programsql})
	""".format( companysql=companysql, academic_yearsql = academic_yearsql, programsql = programsql)
	
	data = frappe.db.sql(feessql, as_dict=1)
		
	dataframe = pd.DataFrame.from_records(data)

	term = dataframe.academic_term.unique().tolist()

	dataframe = dataframe.pivot_table(index=["gender", "student_name"], columns="academic_term", values="amount", aggfunc = 'sum')

	dataframe.fillna(0, inplace = True)
	
	mapping = { 0: 'PAID', 87 : 'UNPAID'}
	dataframe['total_unpaid']=dataframe.loc[:,term].sum(axis=1)
	dataframe = dataframe.replace(to_replace=0, value=1, regex=True)
	dataframe = dataframe.replace(to_replace=[87,70], value="UNPAID", regex=True)

	
#	dataframe = dataframe.assign(A='foo')
#	frappe.msgprint(_("Data {0}").format(dataframe))
#	columns  = [ { "fieldname": "program", "label": _("Program"), "fieldtype": "Link", "options": "Program", "width": 200 }]
#	columns  = [ { "fieldname": "amount", "label": _("Term"), "fieldtype": "Data", "width": 200 }]
	columns = [ { "fieldname": "gender", "label": _("Gender"), "fieldtype": "Data", "width": 200 }]
	columns += [ { "fieldname": "student_name", "label": _("Name"), "fieldtype": "Data", "width": 200 }]
	term = [{"fieldname": academic_term, "label": _(academic_term), "fieldtype": "Int", "width": 150, } for academic_term in term]
	columns += term
	columns+=[ { "fieldname": "total_unpaid", "label": _("Outstanding"), "fieldtype": "Currency", "width": 100 }]

	data = dataframe.reset_index().to_dict('records')
#	frappe.msgprint(_("Data {0}").format(data))
	return columns, data
