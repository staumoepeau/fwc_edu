# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext, string
from frappe import _

def execute(filters=None):
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
		}
		
	]

	return columns

def get_conditions(filters):
	conditions = [""]

	if filters.get("department"):
		conditions.append("department = '%s' " % (filters["department"]) )

	if filters.get("company"):
		conditions.append("company = '%s' " % (filters["company"]) )

	if filters.get("posting_date"):
		conditions.append("posting_date = '%s' " % (filters["posting_date"]))

	if filters.get("bank_name"):
		conditions.append("bank_name = '%s' " % (filters["bank_name"]))

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
			"bank_name" : d.bank_name
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


@frappe.whitelist()
def create_bank_eft_file():

	dataFile = get_data(filters)

	numbers = list()
	# Open the input text file for reading
	dataFile = open('numbers.txt', 'r')

	# Loop through each line of the input data file
	for eachLine in dataFile:
	# setup a temporay variable
		tmpStr = ''
		# loop through each character in the line
		for char in eachLine:
			# check whether the char is a number
			if char.isdigit():
				# if it is a number add it to the tmpStr
				tmpStr += char
				# if a comma is identified and tmpStr has a
				# value then append it to the numbers list
			elif char == ',' and tmpStr != '':
				numbers.append(int(tmpStr))
				tmpStr = ''
		# if the tmpStr contains a number add it to the
		# numbers list.
		if tmpStr.isdigit():
			numbers.append(int(tmpStr))
	# Print the number list
	#print numbers
	# Close the input data file.
	dataFile.close()

	# 2) Uses the string function split to line from the file
	# into a list of substrings
	numbers = list()
	dataFile = open('C:\\PythonCourse\\unit3\\numbers.txt', 'r')

	for eachLine in dataFile:
		# Simplify the script by using a python inbuilt
		# function to separate the tokens
		substrs = eachLine.split(',',eachLine.count(','))
		# Iterate throught the output and check that they
		# are numbers before adding to the numbers list
		for strVar in substrs:
			if strVar.isdigit():
				numbers.append(int(strVar))
	#print numbers
	dataFile.close()