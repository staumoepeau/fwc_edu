# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import pandas as pd

def execute(filters=None):
	columns, data = [], []
	
	companysql = "ss.company = '{company}'".format(company=filters.company) if filters.company else "1 = 1"
	fromdatesql = "ss.start_date >= DATE('{from_date}')".format( from_date=filters.from_date) if filters.from_date else '1=1'
	todatesql = "ss.end_date <= DATE('{to_date}')".format( to_date=filters.to_date) if filters.to_date else '1=1'
	
#	frappe.msgprint(_('No data!!!').format(company))

	salary_summarysql = """
	select ss.name, ss.branch, sd.salary_component, sum(sd.amount) as amount
	from `tabSalary Slip` ss, `tabSalary Detail` sd
	where ss.name = sd.parent
	AND ({companysql})
	AND ({fromdatesql})
	AND ({todatesql})
	AND ss.branch IS NOT NULL
	GROUP BY ss.branch, sd.salary_component
	""".format( companysql=companysql, todatesql = todatesql, fromdatesql = fromdatesql)

	data = frappe.db.sql(salary_summarysql, as_dict=1)

#	frappe.msgprint(_("Data : {0}").format(data))
	if len(data) == 0:
		frappe.msgprint('No data yet')
		return [], []

	dataframe = pd.DataFrame.from_records(data)

	salary_components = dataframe.salary_component.unique().tolist()

	dataframe = dataframe.pivot(index="branch", columns="salary_component", values="amount")

	dataframe.fillna(0, inplace = True)
	dataframe['total']=dataframe.loc[:, salary_components].sum(axis=1) - dataframe.loc[:, 'Basic']
	dataframe['basicsalary'] = dataframe.loc[:, 'Basic'] * 26
	
	salary_components = [{"fieldname": salary_component, "label": _(salary_component), "fieldtype": "Currency", "width": 120, } for salary_component in salary_components]

	columns  = [ { "fieldname": "branch", "label": _("Branch"), "fieldtype": "Data", "width": 200 }]
	columns += [ { "fieldname": "basicsalary", "label": _("Basic Salary"), "fieldtype": "Currency", "width": 100 }]
	columns += salary_components
	columns+=[ { "fieldname": "total", "label": _("Net Pay"), "fieldtype": "Currency", "width": 100 }]

	
	data = dataframe.reset_index().to_dict('records')
	
	return columns, data


