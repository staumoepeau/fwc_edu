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
			"label": _("Income Tax Component"),
			"fieldname": "it_comp",
			"fieldtype": "Data",
			"width": 170
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
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 140
		}
	]

	return columns

def get_conditions(filters):
	conditions = [""]

	if filters.get("department"):
		conditions.append("sal.department = '%s' " % (filters["department"]) )

	if filters.get("branch"):
		conditions.append("sal.branch = '%s' " % (filters["branch"]) )

	if filters.get("company"):
		conditions.append("sal.company = '%s' " % (filters["company"]) )

	if filters.get("month"):
		conditions.append("month(sal.start_date) = '%s' " % (filters["month"]))

	if filters.get("year"):
		conditions.append("year(start_date) = '%s' " % (filters["year"]))

	return " and ".join(conditions)


def get_data(filters):

	data = []
	employee_tin_dict = frappe._dict(frappe.db.sql(""" select employee, tin from `tabEmployee`"""))
	component_types = frappe.db.sql(""" select name from `tabSalary Component`
		where is_income_tax_component = 1 """)

	employee_tax_amount = frappe.db.sql(""" SELECT sal.employee, sum(ded.amount)
		FROM `tabSalary Slip` sal
		LEFT JOIN `tabSalary Detail` ded ON
			sal.name = ded.parent
		AND ded.parentfield = 'deductions'
		AND ded.parenttype = 'Salary Slip'
		AND sal.docstatus = 1
		AND ded.salary_component = 'PAYE-TAX'
	""")

	component_types = [comp_type[0] for comp_type in component_types]

	if not len(component_types):
		return []

	conditions = get_conditions(filters)

	entry = frappe.db.sql(""" SELECT sal.employee, sal.employee_name, sal.posting_date, ded.salary_component, ded.amount, sal.gross_pay
		FROM `tabSalary Slip` sal
		LEFT JOIN `tabSalary Detail` ded ON
			sal.name = ded.parent
		AND ded.parentfield = 'deductions'
		AND ded.parenttype = 'Salary Slip'
		AND sal.docstatus = 1
		AND ded.salary_component = 'PAYE-TAX'
	""", as_dict=1)

	for d in entry:

		employee = {
			"employee_name": d.employee_name,
			"it_comp": d.salary_component,
			"posting_date": d.posting_date,
			"tin": employee_tin_dict.get(d.employee),
			"it_amount": employee_tax_amount.get(d.employee),
			"gross_pay": d.gross_pay
		}

		data.append(employee)

	return data