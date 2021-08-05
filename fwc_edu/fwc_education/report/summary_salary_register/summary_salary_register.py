# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
import pandas as pd

def execute(filters=None):
	columns, data = [], []
	
	mycompany=filters.company
	companysql = "ss.company = '{company}'".format(company=filters.company) if filters.company else "1 = 1"
	fromdatesql = "ss.start_date >= DATE('{from_date}')".format( from_date=filters.from_date) if filters.from_date else '1=1'
	todatesql = "ss.end_date <= DATE('{to_date}')".format( to_date=filters.to_date) if filters.to_date else '1=1'
	
	net_amountsql = """SELECT ss.branch,reports_group,
	SUM(ss.net_pay) AS net_pay
	FROM `tabSalary Slip` ss
	WHERE ss.docstatus = 1
	AND ({companysql})
	AND ({fromdatesql})
	AND ({todatesql})
	AND ss.branch IS NOT NULL
	GROUP BY ss.branch""".format( companysql=companysql, todatesql = todatesql, fromdatesql = fromdatesql)

	salary_summarysql = """
	select ss.branch, reports_group,
	IF(sd.salary_component LIKE 'BSP%', 'BSP', 
		IF(sd.salary_component LIKE 'MBF%', 'MBF', 
			IF(sd.salary_component LIKE 'TDB%', 'TDB',
				IF(sd.salary_component LIKE 'ANZ%', 'ANZ', 
                   IF(sd.salary_component LIKE  'Retirement%','Retirement Fund', sd.salary_component))))) as salary_component,
    IF(sd.salary_component LIKE 'BSP%', 'BSP', 
		IF(sd.salary_component LIKE 'MBF%', 'MBF', 
			IF(sd.salary_component LIKE 'TDB%', 'TDB',
				IF(sd.salary_component LIKE 'ANZ%', 'ANZ', 
                   IF(sd.salary_component LIKE  'Retirement%','Retirement Fund', sd.salary_component))))) as salarycomponent,
	SUM(sd.amount) as amount
	FROM `tabSalary Slip` ss, `tabSalary Detail` sd
	WHERE ss.name = sd.parent
	AND ss.docstatus = 1
	AND ({companysql})
	AND ({fromdatesql})
	AND ({todatesql})
	AND ss.branch IS NOT NULL
	GROUP BY ss.branch, salarycomponent
	""".format( companysql=companysql, todatesql = todatesql, fromdatesql = fromdatesql)
	
	net_data = frappe.db.sql(net_amountsql, as_dict=1)
	data = frappe.db.sql(salary_summarysql, as_dict=1)

#	data = sqldata.append(net_data)
#	frappe.msgprint(_("Data : {0}").format(net_data))

	if len(data) == 0:
		frappe.msgprint('No data yet')
		return [], []

	
	dataframe = pd.DataFrame.from_records(data)
	df_net = pd.DataFrame.from_records(net_data)

	salary_components = dataframe.salary_component.unique().tolist()

	df_net = df_net.pivot_table(index=["branch","reports_group"], values="net_pay")

#	if mycompany == "FWC Education":
	dataframe = dataframe.pivot_table(index=["branch","reports_group"], columns="salary_component", values="amount")
#	if mycompany != "FWC Education":
#		dataframe = dataframe.pivot_table(index="branch", columns="salary_component", values="amount")
#	frappe.msgprint(_("Data : {0}").format(df_net))
	
#	dataframe.insert(11, "netpay", df_net, True)
	dataframe['NetPay'] = df_net

#	frappe.msgprint(_("Dataframe {0}").format(dataframe))

	dataframe.fillna(0, inplace = True)

	dataframe['basicsalary'] = dataframe.loc[:, 'Basic'] * 26

	
	
#	frappe.msgprint(_("Dataframe {0}").format(dataframe))
	salary_components = [{"fieldname": salary_component, "label": _(salary_component), "fieldtype": "Currency", "width": 120, } for salary_component in salary_components]
#


	columns  = [ { "fieldname": "branch", "label": _("Branch"), "fieldtype": "Data", "width": 200 }]
#	if mycompany == "FWC Education":
	columns  += [ { "fieldname": "reports_group", "label": _("Group"), "fieldtype": "Data", "width": 80 }]
	columns += [ { "fieldname": "basicsalary", "label": _("Basic Salary"), "fieldtype": "Currency", "width": 100 }]
	columns += salary_components
	columns+=[ { "fieldname": "NetPay", "label": _("Net Pay"), "fieldtype": "Currency", "width": 100 }]

	if mycompany == "FWC Education":
		dataframe = pd.concat([d.append(d.sum().rename(('TOTAL', '')))
		for k, d in dataframe.groupby(level=1)
			]).append(dataframe.sum().rename(('Grand', 'Total')))

#	netdata = pd.merge(dataframe, df_net, on=['branch'])
	
	data = dataframe.reset_index().to_dict('records')

	
	return columns, data


