# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt
from frappe import _

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns(filters) if len(data) else []

	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("Employee Name"),
			"options": "Employee",
			"fieldname": "employee_name",
			"fieldtype": "Link",
			"width": 160
		},
		{
			"label": _("TIN"),
			"fieldname": "tin",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Income Tax Amount"),
			"fieldname": "it_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 140
		},
		{
			"label": _("Gross Pay"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
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
		conditions.append("month(posting_date) = '%s' " % (filters["month"]))

	if filters.get("year"):
		conditions.append("year(posting_date) = '%s' " % (filters["year"]))

	return " and ".join(conditions)


def get_data(filters):

	data = []

	fields = ["employee", "tin", "department"]
	
	employee_details = frappe.get_list("Employee", fields = fields)
	employee_data_dict = {}

	for d in employee_details:
		employee_data_dict.setdefault(
			d.employee,{
				"employee" : d.employee,
				"tin": d.tin,
				"department": d.department
			}
		)

	conditions = get_conditions(filters)

	posting_month = filters.get("month")
	posting_year = filters.get("year")
	department = filters.get("department")

	entry = frappe.db.sql("""SELECT sal.employee, sal.employee_name, sum(ded.amount) as tax, sum(sal.gross_pay) as gross
		FROM `tabSalary Slip` sal
		LEFT JOIN `tabSalary Detail` ded ON
			sal.name = ded.parent
		AND ded.parentfield = 'deductions'
		AND ded.parenttype = 'Salary Slip'
		AND sal.docstatus = 1
		AND ded.salary_component = 'PAYE-TAX'
		AND month(sal.posting_date) = %s
		AND year(sal.posting_date) = %s
		AND sal.department = %s
        GROUP BY sal.employee
	""", (posting_month, posting_year, department), as_dict=1)
	
	for e in entry:
		employee = {
			"employee_name" : e.employee_name,
			"tin" : employee_data_dict.get(e.employee).get("tin"),
			"it_amount" : e.tax,
			"gross_pay": e.gross,	
		}

		data.append(employee)

	return data