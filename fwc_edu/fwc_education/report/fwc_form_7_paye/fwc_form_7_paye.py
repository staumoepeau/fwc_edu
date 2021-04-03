# Copyright (c) 2013, Sione Taumoepeau and contributors
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

from openpyxl import load_workbook
from frappe import _, msgprint, utils
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, datetime, comma_and
from collections import defaultdict
from werkzeug.wrappers import Response
import frappe, erpnext


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
	
	if department == "All Departments":
		entry = frappe.db.sql("""SELECT tmp.employee, Concat(Ifnull(temp.last_name,' ') ,' ', Ifnull(temp.middle_name,' '),' ', Ifnull(temp.first_name,' ')) as employee_name,
					tmp.tax, tmp.gross, tmp.department
					FROM `tabEmployee` temp INNER JOIN
					(SELECT sal.employee, sal.employee_name, (ded.amount*2)as tax, (sal.gross_pay*2) as gross, sal.department, month(sal.posting_date) as month, year(sal.posting_date) as year
					FROM `tabSalary Slip` sal LEFT JOIN 
					`tabSalary Detail` ded ON sal.name = ded.parent
					AND ded.docstatus = 1
					AND ded.parentfield = 'deductions'
					AND ded.parenttype = 'Salary Slip'
					AND ded.salary_component = 'PAYE-TAX'
					GROUP BY sal.employee) tmp ON tmp.employee = temp.employee
					WHERE tmp.month = %s
					AND tmp.year = %s 
			""", (posting_month, posting_year), as_dict=1)

	if department != "All Departments":
		entry = frappe.db.sql("""SELECT tmp.employee, Concat(Ifnull(temp.last_name,' ') ,' ', Ifnull(temp.middle_name,' '),' ', Ifnull(temp.first_name,' ')) as employee_name,
					tmp.tax, tmp.gross, tmp.department
					FROM `tabEmployee` temp INNER JOIN
					(SELECT sal.employee, sal.employee_name, (ded.amount*2)as tax, (sal.gross_pay*2) as gross, sal.department, month(sal.posting_date) as month, year(sal.posting_date) as year
					FROM `tabSalary Slip` sal LEFT JOIN 
					`tabSalary Detail` ded ON sal.name = ded.parent
					AND ded.docstatus = 1
					AND ded.parentfield = 'deductions'
					AND ded.parenttype = 'Salary Slip'
					AND ded.salary_component = 'PAYE-TAX'
					GROUP BY sal.employee) tmp ON tmp.employee = temp.employee
					WHERE temp.department = %s
					AND tmp.month = %s
					AND tmp.year = %s 
			""", (department, posting_month, posting_year), as_dict=1)

	for e in entry:
		employee = {
			"employee_name" : e.employee_name,
			"tin" : employee_data_dict.get(e.employee).get("tin"),
			"it_amount" : e.tax,
			"gross_pay": e.gross,
			"department": e.department
		}
		data.append(employee)
	return data

def get_paye_data(posting_month, posting_year, department):
	data = []
	fields = ["employee", "tin", "department"]

	employee_details = frappe.get_list("Employee", fields = fields)
	employee_data_dict = {}

	for d in employee_details:
		employee_data_dict.setdefault(
			d.employee,{
				"tin": d.tin,
				"employee" : d.employee,
				"department": d.department
			}
		)

	if department == "All Departments":
		entry = frappe.db.sql("""SELECT tmp.employee, Concat(Ifnull(temp.last_name,' ') ,' ', Ifnull(temp.middle_name,' '),' ', Ifnull(temp.first_name,' ')) as employee_name,
					tmp.tax, tmp.gross, tmp.department
					FROM `tabEmployee` temp INNER JOIN
					(SELECT sal.employee, sal.employee_name, (ded.amount*2)as tax, (sal.gross_pay*2) as gross, sal.department, month(sal.posting_date) as month, year(sal.posting_date) as year
					FROM `tabSalary Slip` sal LEFT JOIN  
					`tabSalary Detail` ded ON sal.name = ded.parent
					AND ded.docstatus = 1
					AND ded.parentfield = 'deductions'
					AND ded.parenttype = 'Salary Slip'
					AND ded.salary_component = 'PAYE-TAX'
					GROUP BY sal.employee) tmp ON tmp.employee = temp.employee
					WHERE tmp.month = %s
					AND tmp.year = %s 
			""", (posting_month, posting_year), as_dict=1)
	
	if department != "All Departments":
		entry = frappe.db.sql("""SELECT tmp.employee, Concat(Ifnull(temp.last_name,' ') ,' ', Ifnull(temp.middle_name,' '),' ', Ifnull(temp.first_name,' ')) as employee_name,
					tmp.tax, tmp.gross, tmp.department
					FROM `tabEmployee` temp INNER JOIN
					(SELECT sal.employee, sal.employee_name, (ded.amount*2)as tax, (sal.gross_pay*2) as gross, sal.department, month(sal.posting_date) as month, year(sal.posting_date) as year
					FROM `tabSalary Slip` sal LEFT JOIN 
					`tabSalary Detail` ded ON sal.name = ded.parent
					AND ded.docstatus = 1
					AND ded.parentfield = 'deductions'
					AND ded.parenttype = 'Salary Slip'
					AND ded.salary_component = 'PAYE-TAX'
					GROUP BY sal.employee) tmp ON tmp.employee = temp.employee
					WHERE temp.department = %s
					AND tmp.month = %s
					AND tmp.year = %s 
			""", (department, posting_month, posting_year), as_dict=1)

	for e in entry:
		employee = {
			"tin" : employee_data_dict.get(e.employee).get("tin"),
			"employee_name" : e.employee_name,
			"payment_date" : None,
			"payment_period" : "Monthly",
			"gross_pay": e.gross,
			"total_benefit": None,
			"it_amount" : e.tax,
			
		}

		data.append(employee)

	return data


@frappe.whitelist()
def save_data_to_Excel(month, department, year):

	filename = "PAYE.xltm"

	new_filename = "FWC-FORM7-PAYE-" + month + year+".xlsm"

	save_path = 'fwc.edu/private/files/Form_7'
	file_name = os.path.join(save_path, filename)
	new_file_name = os.path.join(save_path, new_filename)
	ferp = frappe.new_doc("File")
	ferp.file_name = filename

	fileerp = frappe.new_doc("File")
	fileerp.new_file_name = new_filename
	fileerp.folder = "Home/Form_7"
	fileerp.is_private = 1
	fileerp.file_url = "/private/files/Form_7/"+new_filename

#	ferp.folder = "Home"
#	ferp.is_private = 1
#	ferp.file_url = "/private/files/Form_7/"+new_filename

	Month = datetime.date(1900, int(month), 1).strftime('%B')

	paye_data = []
	paye_data = get_paye_data(month, year, department)

	df = pd.DataFrame(paye_data)

	workbook1 = openpyxl.load_workbook(file_name, read_only=False, keep_vba= True)
	workbook1.template = True
	sheetname = workbook1.get_sheet_by_name('PAYE')
	sheetname['B5']= str('263317')
	sheetname['B7']= str(Month)
	sheetname['D7']= str(year)
	sheetname['B9']= str('FWC Education')

	writer = pd.ExcelWriter(new_file_name, engine='openpyxl')
	writer.book = workbook1
	writer.sheets = dict((ws.title, ws) for ws in workbook1.worksheets)

	df.to_excel(writer, sheet_name='PAYE', index=False, header=False, startrow=12, startcol=1)

#	with pd.ExcelWriter(file_name) as writer:
#		writer.book = openpyxl.load_workbook(file_name, read_only=False, keep_vba= True)
#		df.to_excel(writer, sheet_name=sheetname, index=False, header=False, startrow=13, startcol=1)
    

#	frappe.msgprint(_("File created - Please check File List to download the file"))
#	writer.save()
	frappe.msgprint(_("Form 7 have been created"))
	
#	writer.close()
#	frappe.msgprint(_("Executing the below:"))
#	frappe.local.response.filename = new_file_name
#	with open(new_file_name, "rb") as fileobj:
#		filedata = fileobj.read()
#	frappe.logger().debug("Inside") 
#	frappe.local.response.filecontent = filedata
#	frappe.local.response.type = "download"