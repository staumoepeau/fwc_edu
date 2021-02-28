# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe

def execute(filters=None):
	global netpay
	netpay = []

	columns = get_columns(filters)
	data = get_data(filters)

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
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 140
		},
		{
			"label": _("Payroll Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 140
		},
		
	]

	return columns

def get_conditions(filters):
	conditions = [""]

	if filters.get("posting_date"):
		conditions.append("posting_date = '%s' " % (filters["posting_date"]))

	if filters.get("department"):
		conditions.append("department = '%s' " % (filters["department"]) )


	return " and ".join(conditions)

def get_payroll_names(filters):

	postingdate = filters.get("posting_date")

	data_to_be_printed = frappe.db.sql(""" SELECT payroll_entry FROM `tabSalary Slip`
		WHERE posting_date = %s
		""", (postingdate))

	return data_to_be_printed

def get_data(filters):

	data = []

	fields = ["employee", "bank_name", "bank_ac_no", "salary_mode", "department"]
	
	employee_details = frappe.get_list("Employee", fields = fields)
	employee_data_dict = {}

	for d in employee_details:
		employee_data_dict.setdefault(
			d.employee,{
				"account_number" : d.bank_ac_no,
				"salary_mode" : d.salary_mode,
				"bank_name": d.bank_name,
				"department": d.department
			}
		)

	conditions = get_conditions(filters)

	bankname = filters.get("bank_name")
	postingdate = filters.get("posting_date")
	department = filters.get("department")

	employee_list = frappe.db.sql(""" SELECT sal.employee, sal.employee_name, 
			IF(ded.salary_component LIKE "BSP%%", "BSP",
				IF (ded.salary_component LIKE "TDB%%", "TDB",
					IF (ded.salary_component LIKE "MBF%%", "MBF", ded.salary_component)))
			as bankname, ded.amount, ded.account_number
			FROM `tabSalary Slip` sal
			INNER JOIN `tabSalary Detail` ded ON
				sal.name = ded.parent
			AND ded.parentfield = 'deductions'
			AND ded.parenttype = 'Salary Slip'
			AND ded.docstatus = 1
            AND sal.posting_date = %s
			AND sal.department = %s
            HAVING bankname = %s
			""", (postingdate, department, bankname), as_dict=1)
	
	employee_list_dict = {}

	for e in employee_list:
		employee_list_dict.setdefault(
			e.employee,{
				"employee_name": e.employee_name,
				"employee": e.employee,
				"account_number" : e.account_number,
				"bank_name": e.bankname,
				"department": e.department
			}
		)

	other = frappe.db.sql(""" SELECT sal.employee, sal.employee_name, 
			IF(ded.salary_component LIKE "BSP%%", "BSP",
				IF (ded.salary_component LIKE "TDB%%", "TDB",
					IF (ded.salary_component LIKE "MBF%%", "MBF", ded.salary_component)))
			as bankname, ded.amount, ded.account_number
			FROM `tabSalary Slip` sal
			INNER JOIN `tabSalary Detail` ded ON
				sal.name = ded.parent
			AND ded.parentfield = 'deductions'
			AND ded.parenttype = 'Salary Slip'
			AND ded.docstatus = 1
            AND sal.posting_date = %s
			AND sal.department = %s
            HAVING bankname = %s
			""", (postingdate, department, bankname), as_dict=1)
	
	entry = frappe.db.sql(""" select employee, employee_name, net_pay as amount, mode_of_payment, bank_account_no, bank_name, department
		from `tabSalary Slip`
		where docstatus = 1 %s """
		%(conditions), as_dict =1)

	for e in other:
		employee = {
			"employee_name" : e.employee_name,
			"employee": e.employee,
			"amount" : e.amount,
			"bank_name" : e.bankname,
			"account_number": e.account_number,
			"department": e.department
		}

		data.append(employee)
	
	for d in entry:
		employee = {
			"employee_name" : d.employee_name,
			"employee": d.employee,
			"amount" : d.amount,
			"bank_name" : d.bank_name,
			"account_number": d.bank_account_no,
			"department": d.department

		}

		data.append(employee)
	return data
