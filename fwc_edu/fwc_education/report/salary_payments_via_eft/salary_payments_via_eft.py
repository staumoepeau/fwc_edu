# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("Employee"),
			"options":"Employee",
			"fieldname": "employee",
			"fieldtype": "Link",
			"width": 140
		},
		{
			"label": _("Employee Name"),
			"options": "Employee",
			"fieldname": "employee_name",
			"fieldtype": "Link",
			"width": 160
		},
		
		{
			"label": _("Net Pay"),
			"fieldname": "net_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 140
		},
		{
			"label": _("Bank"),
			"fieldname": "bank",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Account No"),
			"fieldname": "account_no",
			"fieldtype": "Data",
			"width": 140
		},
	]

	return columns

def get_conditions(filters):
	conditions = [""]

	if filters.get("department"):
		conditions.append("department = '%s' " % (filters["department"]) )

	if filters.get("branch"):
		conditions.append("branch = '%s' " % (filters["branch"]) )

	if filters.get("company"):
		conditions.append("company = '%s' " % (filters["company"]) )

	if filters.get("month"):
		conditions.append("month(start_date) = '%s' " % (filters["month"]))

	if filters.get("year"):
		conditions.append("year(start_date) = '%s' " % (filters["year"]))

	return " and ".join(conditions)

def get_data(filters):

	data = []

	fields = ["employee", "bank_name", "bank_ac_no", "salary_mode"]
	
	employee_details = frappe.get_list("Employee", fields = fields)
	employee_data_dict = {}

	for d in employee_details:
		employee_data_dict.setdefault(
			d.employee,{
				"bank_ac_no" : d.bank_ac_no,
				"salary_mode" : d.salary_mode,
				"bank_name": d.bank_name
			}
		)

	conditions = get_conditions(filters)

	entry = frappe.db.sql(""" select employee, employee_name, net_pay
		from `tabSalary Slip`
		where docstatus = 1 %s """
		%(conditions), as_dict =1)

	for d in entry:

		employee = {
			"employee_name" : d.employee_name,
			"employee" : d.employee,
			"net_pay" : d.net_pay,
		}

		if employee_data_dict.get(d.employee).get("salary_mode") == "Bank":
			employee["bank"] = employee_data_dict.get(d.employee).get("bank_name")
			employee["account_no"] = employee_data_dict.get(d.employee).get("bank_ac_no")
		else:
			employee["account_no"] = employee_data_dict.get(d.employee).get("salary_mode")

		if filters.get("type") and employee_data_dict.get(d.employee).get("salary_mode") == filters.get("type"):
			data.append(employee)
		elif not filters.get("type"):
			data.append(employee)
	return data
