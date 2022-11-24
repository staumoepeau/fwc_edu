# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

import frappe
import json
import time
import math
import ast
import os.path
import sys
import datetime
import pandas as pd 
import numpy as np

from frappe import _, msgprint, utils
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, datetime, comma_and
from collections import defaultdict
from werkzeug.wrappers import Response
format = "%Y-%m-%d %H:%M:%S"

global BSP_Bank 
global MBF_Bank
global TDB_Bank
global SIA
global CompanyList
global netpay

CompanyList = ["Tupou Tertiary Institute","FWC Education","Queen Salote College","Tupou High School","Tupou College Toloa","Tupou College Toloa Faama"]

SIA = "SIA%"
BSP_Bank = "BSP%"
MBF_Bank = ["MBF", "MBF01", "MBF02","MBF03","MBF04", "MBF05", "Pakiua Ma"]
TDB_Bank = "TDB%"


def execute(filters=None):
	if not filters: filters = {}
	
	
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
			"label": _("Bank"),
			"fieldname": "bank_name",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Reference"),
			"fieldname": "description",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Account No"),
			"fieldname": "account_number",
			"fieldtype": "Data",
			"width": 140
		}
		
	]

	return columns

def get_conditions(filters):
	conditions = [""]

	if filters.get("company"):
		conditions.append("company = '%s' " % (filters["company"]) )

	if filters.get("posting_date"):
		conditions.append("posting_date = '%s' " % (filters["posting_date"]))

	if filters.get("department"):
		conditions.append("department = '%s' " % (filters["department"]) )

	if filters.get("bank_name"):
		conditions.append("bank_name = '%s' " % (filters["bank_name"]))

	return " and ".join(conditions)

def get_payroll_names(filters):

	postingdate = filters.get("posting_date")

	data_to_be_printed = frappe.db.sql("""SELECT payroll_entry FROM `tabSalary Slip`
		WHERE posting_date = %s
		""", (postingdate))

	return data_to_be_printed

def get_data(filters):

	data = []

	fields = ["employee", "bank_name", "bank_ac_no", "salary_mode", "department", "company"]
	
	employee_details = frappe.get_list("Employee", fields = fields)
	employee_data_dict = {}

	for d in employee_details:
		employee_data_dict.setdefault(
			d.employee,{
				"account_number" : d.bank_ac_no,
				"salary_mode" : d.salary_mode,
				"bank_name": d.bank_name,
				"department": d.department,
				"company": d.company
			}
		)
#	conditions = get_conditions(filters)

	bankname = filters.get("bank_name")
	postingdate = filters.get("posting_date")
	company = filters.get("company")

	employee_list = frappe.db.sql("""SELECT sal.employee, sal.employee_name, 
			ded.salary_component as bankname, ded.amount, ded.account_number, ded.description
			FROM `tabSalary Slip` sal
			INNER JOIN `tabSalary Detail` ded ON
				sal.name = ded.parent
			AND ded.parentfield = 'deductions'
			AND ded.parenttype = 'Salary Slip'
			AND ded.amount > 0
			AND ded.docstatus = 1
            AND sal.posting_date = %s
			AND sal.company = %s
            HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)
	
	employee_list_dict = {}

	for e in employee_list:
		employee_list_dict.setdefault(
			e.employee,{
				"employee_name": e.employee_name.upper(),
				"employee": e.employee,
				"account_number" : e.account_number,
				"bank_name": e.bankname,
				"company": e.company
			}
		)

	other = frappe.db.sql("""SELECT sal.employee, sal.employee_name,
			IF(ded.salary_component LIKE %s, "BSP",
				IF(ded.salary_component IN %s, "MBF",
					IF(ded.salary_component LIKE %s, "TDB", 
						IF(ded.salary_component LIKE %s, "SIA", ded.salary_component)))) AS bankname,
			ded.amount, ded.account_number, ded.description
			FROM `tabSalary Slip` sal
			INNER JOIN `tabSalary Detail` ded ON
				sal.name = ded.parent
			AND ded.parentfield = 'deductions'
			AND ded.parenttype = 'Salary Slip'
			AND ded.docstatus = 1
			AND ded.amount > 0
			AND sal.posting_date = %s
			AND sal.company = %s
			HAVING bankname = %s
			""", (BSP_Bank, MBF_Bank, TDB_Bank, SIA, postingdate, company, bankname), as_dict=1)
	
	entry = frappe.db.sql("""select employee, employee_name, net_pay as amount, mode_of_payment, 
		bank_account_no, bank_name, company, department, payment_details
		from `tabSalary Slip`
		where docstatus = 1
		and net_pay > 0 
		AND posting_date = %s
		AND company = %s
        AND bank_name = %s
		""", (postingdate, company, bankname), as_dict=1)

	employee = {}
	for e in other:
		if not e.account_number:
				e.account_number = ''
		
		if bankname == 'TDB' or bankname == 'MBF':
			description = e.description
			emp_name = e.employee_name

			if e.description:
				e.employee_name = description
				e.description = emp_name.upper() 
			else:
				e.description = ''
#				e.e.employee_name = emp_name
		if bankname == 'BSP':
			if e.description:
				e.description = e.description.upper() 
			else:
				e.description = ''

		employee = {
			"employee_name" : e.employee_name.upper(),
			"employee": e.employee,
			"amount" : e.amount,
			"bank_name" : e.bankname,
			"account_number": e.account_number,
			"company": e.company,
			"description" : e.description
		}

		data.append(employee)
	
	for d in entry:
		if not d.account_number:
				d.account_number = ''
		
		if bankname == 'TDB' or bankname == 'MBF':
			description = e.description
			emp_name = e.employee_name

			if e.description:
				e.employee_name = description
				e.description = emp_name.upper() 
			else:
				e.description = ''
				e.employee_name = emp_name
		if bankname == 'BSP':
			if d.description:
				d.description = d.description.upper() 
			else:
				d.description = ''
		employee = {
			"employee_name" : d.employee_name.upper(),
			"employee": d.employee,
			"amount" : d.amount,
			"bank_name" : d.bank_name,
			"account_number": d.bank_account_no,
			"company": d.company,
			"description": d.description

		}
		data.append(employee)
	
	tti_account = []
	tti_association = []
	SIA_Finance = []
	
	if company in CompanyList and bankname == "BSP":
		tti_account = frappe.db.sql("""SELECT sal.employee, 
			IF(ded.salary_component = "TTI ACCOUNT","TTI ACCOUNT", sal.employee_name) AS employee_name, 
			IF(ded.salary_component = "TTI ACCOUNT", "BSP", ded.salary_component) AS bankname,
			SUM(ded.amount) AS amount, 
			ded.account_number as account_number
				FROM `tabSalary Slip` sal
				INNER JOIN `tabSalary Detail` ded ON sal.name = ded.parent
				AND ded.parentfield = 'deductions'
				AND ded.parenttype = 'Salary Slip'
				AND ded.docstatus = 1
				AND ded.amount > 0
				AND ded.salary_component = "TTI ACCOUNT"
				AND sal.posting_date = %s
				AND sal.company = %s
				GROUP BY ded.salary_component
				HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)

		for t in tti_account:
			employee = {
			"employee_name" : t.employee_name.upper(),
			"employee": t.employee,
			"amount" : t.amount,
			"bank_name" : t.bankname,
			"account_number": t.account_number,
			"company": t.company
			}
			data.append(employee)

		tti_association = frappe.db.sql("""SELECT sal.employee, 
			IF(ded.salary_component = "TTI STAFF ASSOCIATION","TTI STAFF ASSOCIATION", sal.employee_name) AS employee_name, 
				IF(ded.salary_component = "TTI STAFF ASSOCIATION", "BSP", ded.salary_component) AS bankname, 
				SUM(ded.amount) AS amount, ded.account_number as account_number
				FROM `tabSalary Slip` sal
				INNER JOIN `tabSalary Detail` ded ON sal.name = ded.parent
				AND ded.parentfield = 'deductions'
				AND ded.parenttype = 'Salary Slip'
				AND ded.docstatus = 1
				AND ded.amount > 0
				AND ded.salary_component = "TTI STAFF ASSOCIATION"
				AND sal.posting_date = %s
				AND sal.company = %s
				GROUP BY ded.salary_component
				HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)

		for a in tti_association:
			employee = {
			"employee_name" : a.employee_name.upper(),
			"employee": a.employee,
			"amount" : a.amount,
			"bank_name" : a.bankname,
			"account_number": a.account_number,
			"company": a.company
			}
			data.append(employee)

		SIA_Finance = frappe.db.sql("""SELECT sal.employee, 
			IF(ded.salary_component = "SIA Finance","SIA Finance", sal.employee_name) AS employee_name, 
				IF(ded.salary_component = "SIA Finance", "BSP", ded.salary_component) AS bankname, 
				SUM(ded.amount) AS amount, ded.account_number as account_number
				FROM `tabSalary Slip` sal
				INNER JOIN `tabSalary Detail` ded ON sal.name = ded.parent
				AND ded.parentfield = 'deductions'
				AND ded.parenttype = 'Salary Slip'
				AND ded.docstatus = 1
				AND ded.amount > 0
				AND ded.salary_component = "SIA Finance"
				AND sal.posting_date = %s
				AND sal.company = %s
				GROUP BY ded.salary_component
				HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)

		for sia in SIA_Finance:
			employee = {
			"employee_name" : sia.employee_name.upper(),
			"employee": sia.employee,
			"amount" : sia.amount,
			"bank_name" : sia.bankname,
			"account_number": sia.account_number,
			"company": sia.company
			}
			data.append(employee)
 
	return data

def get_bank_data(postingdate, company, bankname):

	BSP_Bank = "BSP%"
#	MBF_Bank = "MBF%"
	TDB_Bank = "TDB%"
	SIA = "SIA%"

	bank_data = []

	fields = ["employee", "bank_name", "bank_ac_no", "salary_mode", "company", "salary_comment"]
	
	employee_details = frappe.get_list("Employee", fields = fields)
	employee_data_dict = {}

	for d in employee_details:
		employee_data_dict.setdefault(
			d.employee,{
				"account_number" : d.bank_ac_no,
				"salary_mode" : d.salary_mode,
				"bank_name": d.bank_name,
				"company": d.company,
				"salary_comment": d.salary_comment

			}
		)

	employee_list = frappe.db.sql("""SELECT sal.employee, sal.employee_name, 
			ded.salary_component AS bankname, ded.amount, ded.account_number, ded.description
			FROM `tabSalary Slip` sal
			INNER JOIN `tabSalary Detail` ded ON
				sal.name = ded.parent
			AND ded.parentfield = 'deductions'
			AND ded.parenttype = 'Salary Slip'
			AND ded.docstatus = 1
			AND ded.amount > 0
            AND sal.posting_date = %s
			AND sal.company = %s
            HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)
	
	employee_list_dict = {}

	for e in employee_list:
		employee_list_dict.setdefault(
			e.employee,{
				"employee_name": e.employee_name,
				"employee": e.employee,
				"account_number" : e.account_number,
				"bank_name": e.bankname,
				"company": e.company
			}
		)

	other = frappe.db.sql("""SELECT sal.employee, sal.employee_name,
			IF(ded.salary_component LIKE %s, "BSP",
				IF(ded.salary_component IN %s, "MBF",
					IF(ded.salary_component LIKE %s, "TDB", 
						IF(ded.salary_component LIKE %s, "SIA", ded.salary_component)))) AS bankname,
			ded.amount, ded.account_number, ded.description
			FROM `tabSalary Slip` sal
			INNER JOIN `tabSalary Detail` ded ON
				sal.name = ded.parent
			AND ded.parentfield = 'deductions'
			AND ded.parenttype = 'Salary Slip'
			AND ded.docstatus = 1
			AND ded.amount > 0
			AND sal.posting_date = %s
			AND sal.company = %s
			HAVING bankname = %s
			""", (BSP_Bank, MBF_Bank, TDB_Bank, SIA, postingdate, company, bankname), as_dict=1)
	
	entry = frappe.db.sql("""SELECT employee, employee_name, net_pay as amount, 
		mode_of_payment, bank_account_no, bank_name, company, department, payment_details
		FROM `tabSalary Slip`
		WHERE net_pay > 0
		AND posting_date = %s
		AND company = %s
		AND docstatus = 1
        AND bank_name = %s
		""", (postingdate, company, bankname), as_dict=1)
	
	employee = {}

	for d in entry:

		if not d.account_number:
				d.account_number = ''
		
#		if bankname == 'TDB' or bankname == 'MBF':	
#			if d.description:
#				d.description = d.description.upper() 
#			else:
#				d.description = ''
		if bankname == 'BSP':
			if d.description:
				d.description = d.description.upper() 
			else:
				d.description = ''
		employee = {
			"employee_name" : ((d.employee_name.upper()).replace(".","").replace("'","").replace("  "," ")[:20]),
			"employee" : d.employee,
			"amount" : str(int(round(d.amount*100))).zfill(10),
			"payment_details" : d.payment_details,
			"bank_name" : d.bank_name,
			"account_number": d.bank_account_no.replace("-",""),
			"description": d.description
		}

		bank_data.append(employee)
	
	for e in other:
		if bankname == 'TDB' or bankname == 'MBF':
			description = e.description
			emp_name = e.employee_name

			if e.description:
				e.employee_name = description
				e.description = emp_name.upper() 
			else:
				e.description = ''
				e.employee_name = emp_name
		if bankname == 'BSP':
			if e.description:
				e.description = e.description.upper() 
			else:
				e.description = ''
		employee = {
			"employee_name" : ((e.employee_name.upper()).replace(".","").replace("'","").replace("  "," ")[:20]),
			"employee": e.employee,
			"amount" : str(int(round(e.amount*100))).zfill(10),
			"bank_name" : e.bankname,
			"account_number": e.account_number.replace("-",""),
			"company": e.company,
			"description" : e.description
		}

		bank_data.append(employee)
	
	tti_account = []
	tti_association = []
	SIA_Finance = []

	if company in CompanyList and bankname == "BSP":
		tti_account = frappe.db.sql("""SELECT sal.employee, 
			IF(ded.salary_component = "TTI ACCOUNT","TTI ACCOUNT", sal.employee_name) AS employee_name, 
			IF(ded.salary_component = "TTI ACCOUNT", "BSP", ded.salary_component) AS bankname,
				SUM(ded.amount) AS amount, ded.account_number as account_number,ded.description
				FROM `tabSalary Slip` sal
				INNER JOIN `tabSalary Detail` ded ON sal.name = ded.parent
				AND ded.parentfield = 'deductions'
				AND ded.parenttype = 'Salary Slip'
				AND ded.docstatus = 1
				AND ded.amount > 0
				AND ded.salary_component = "TTI ACCOUNT"
				AND sal.posting_date = %s
				AND sal.company = %s
				GROUP BY ded.salary_component
				HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)

#		msgprint(_("After TTI {0}"). format(tti_account))

		for ta in tti_account:
			employee = {
			"employee_name" : ((ta.employee_name.upper()).replace(".","").replace("'","").replace("  "," ")[:20]),
#			"employee": ta.employee,
			"amount" : str(int(round(ta.amount*100))).zfill(10),
			"bank_name" : ta.bankname,
			"account_number": ta.account_number.replace("-",""),
			"company": ta.company,
			"description" : ta.description
			}

			bank_data.append(employee)
		
#		msgprint(_("After TTI {0}"). format(bank_data))

		tti_association = frappe.db.sql("""SELECT sal.employee, IF(ded.salary_component = "TTI STAFF ASSOCIATION","TTI STAFF ASSOCIATION", sal.employee_name)
				AS employee_name, IF(ded.salary_component = "TTI STAFF ASSOCIATION", "BSP", ded.salary_component)
				AS bankname, SUM(ded.amount) AS amount, ded.account_number as account_number, ded.description
				FROM `tabSalary Slip` sal
				INNER JOIN `tabSalary Detail` ded ON sal.name = ded.parent
				AND ded.parentfield = 'deductions'
				AND ded.parenttype = 'Salary Slip'
				AND ded.docstatus = 1
				AND ded.amount > 0
				AND ded.salary_component = "TTI STAFF ASSOCIATION"
				AND sal.posting_date = %s
				AND sal.company = %s
				GROUP BY ded.salary_component
				HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)

		for a in tti_association:
			employee = {
			"employee_name" : ((a.employee_name.upper()).replace(".","").replace("'","").replace("  "," ")[:20]),
			"employee": a.employee,
			"amount" : str(int(round(a.amount*100))).zfill(10),
			"bank_name" : a.bankname,
			"account_number": a.account_number.replace("-",""),
			"company": a.company,
			"description" : a.description
			}

			bank_data.append(employee)

		SIA_Finance = frappe.db.sql("""SELECT sal.employee, 
			IF(ded.salary_component = "SIA Finance","SIA Finance", sal.employee_name) AS employee_name, 
				IF(ded.salary_component = "SIA Finance", "BSP", ded.salary_component) AS bankname,
				SUM(ded.amount) AS amount, ded.account_number as account_number, ded.description
				FROM `tabSalary Slip` sal
				INNER JOIN `tabSalary Detail` ded ON sal.name = ded.parent
				AND ded.parentfield = 'deductions'
				AND ded.parenttype = 'Salary Slip'
				AND ded.docstatus = 1
				AND ded.amount > 0
				AND ded.salary_component = "SIA Finance"
				AND sal.posting_date = %s
				AND sal.company = %s
				GROUP BY ded.salary_component
				HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)

		for sia in SIA_Finance:
			employee = {
			"employee_name" : ((sia.employee_name.upper()).replace(".","").replace("'","").replace("  "," ")[:20]),
			"employee": sia.employee,
			"amount" : str(int(round(sia.amount*100))).zfill(10),
			"bank_name" : sia.bankname,
			"account_number": sia.account_number.replace("-",""),
			"company": sia.company,
			"description" : sia.description

			}
			bank_data.append(employee)
#	frappe.msgprint(_("BANK {0}").format(bank_data))
	return bank_data

def get_sum_netpay(posting_date, company, bank_name):
#	CompanyList = ["Tupou Tertiary Institute","FWC Education","Queen Salote College","Tupou High School","Tupou College Toloa","Tupou College Toloa Faama"]

	netpay = ""
	netpay_1, netpay_2 = [], []

	netpay_1 = frappe.db.sql("""select sum(net_pay)
		FROM `tabSalary Slip`
		where docstatus = 1
		and net_pay > 0
		and posting_date = %s
		and company = %s
		and bank_name = %s """,(posting_date, company, bank_name))
	
	if company in CompanyList and bank_name == "BSP":
		netpay_2 = frappe.db.sql("""SELECT sum(tsd.amount)
				FROM `tabSalary Detail` tsd, `tabSalary Slip` tss
				WHERE tsd.parent = tss.name
				AND tsd.amount > 0
				AND tsd.docstatus = 1
				AND tsd.salary_component IN ("BSP", "TTI STAFF ASSOCIATION", "TTI ACCOUNT", "SIA Finance", "BSP02", "BSP03","BSP04")
				AND tss.posting_date = %s
				AND tss.company = %s
				""", (posting_date, company))
	
	if company not in CompanyList:
		netpay_2 = frappe.db.sql("""SELECT sum(tsd.amount)
				FROM `tabSalary Detail` tsd, `tabSalary Slip` tss
				WHERE tsd.parent = tss.name
				AND tsd.amount > 0
				AND tsd.docstatus = 1
				AND tsd.salary_component IN ("BSP","BSP02", "BSP03","BSP04")
				AND tss.posting_date = %s
				AND tss.company = %s
				""", (posting_date, company))
				
#	frappe.msgprint(_("PAY 2 : {0}").format(netpay_2))

	if np.array(netpay_1):
		netpay = netpay_1
#		frappe.msgprint(_("PAY 1 : {0}").format(netpay_1))

	if np.array(netpay_2):
		netpay = netpay_2
#		frappe.msgprint(_("PAY 2 : {0}").format(netpay_2))


	if	np.array(netpay_1) and np.array(netpay_2):
		netpay = np.add(netpay_1, netpay_2)
#		frappe.msgprint(_("NAT PAY : {0}").format(netpay))


	netpay = str(netpay).replace("[[","")
	netpay = (str(netpay).replace("]]","")).replace(",","")
	netpay = str(netpay).replace("(","")
	netpay = (str(netpay).replace(")","")).replace(",","")
	netpay = ((str(netpay)).replace(".",""))

#	frappe.msgprint(_("NET01: {0}").format(netpay))

#	netpay = int(float(netpay)*100)

#	frappe.msgprint(_("NET1: {0}").format(netpay))

	#netpay = ((str(netpay)).replace(".",""))
#	frappe.msgprint(_("NET2: {0}").format(netpay))
	
	netpay = str(netpay).zfill(10)

#	frappe.msgprint(_("NET: {0}").format(netpay))
	return netpay

def get_sum_account(posting_date, company, bank_name):
	sum_account = ""

	sum_account_1 = frappe.db.sql("""select sum(bank_account_no)
		from `tabSalary Slip`
		where docstatus = 1
		and net_pay != 0
		and posting_date = %s
		and company = %s
		and bank_name = %s """,(posting_date, company, bank_name))
	
	if company in CompanyList and bank_name == "BSP":
		sum_account_2 = frappe.db.sql("""SELECT sum(account_number) 
				FROM `tabSalary Detail` tsd, `tabSalary Slip` tss
				WHERE tsd.parent = tss.name
				AND tsd.salary_component in ("BSP","TTI STAFF ASSOCIATION","TTI ACCOUNT", "SIA Finance","BSP02", "BSP03","BSP04","BSP05")
				AND tsd.docstatus = 1
				AND tss.posting_date = %s
				AND tss.company = %s
				""", (posting_date, company))
	
	if company not in CompanyList and bank_name == "BSP":
		sum_account_2 = frappe.db.sql("""SELECT sum(account_number) 
				FROM `tabSalary Detail` tsd, `tabSalary Slip` tss
				WHERE tsd.parent = tss.name
				AND tsd.salary_component IN ("BSP","BSP02","BSP03","BSP04","BSP05")
				AND tsd.docstatus = 1
				AND tss.posting_date = %s
				AND tss.company = %s
				""", (posting_date, company))
	
	if np.array(sum_account_1):
		sum_1 = np.array(sum_account_1)
		sum_account = sum_1.astype(int)
#		frappe.msgprint(_("SUM 1 : {0}").format(sum_account))

	if np.array(sum_account_2):
		sum_2 = np.array(sum_account_2)
		sum_account = sum_2.astype(int)
#		frappe.msgprint(_("SUM 2 : {0}").format(sum_account))

	if	np.array(sum_account_1) and np.array(sum_account_2):
		sum_1 = np.array(sum_account_1)
		sum_2 = np.array(sum_account_2)
		sum_account = np.add(sum_1.astype(int), sum_2.astype(int))
		

	sum_account = str(sum_account).replace("[[","")
	sum_account = (str(sum_account).replace("]]","")).replace(",","")

	sum_account = str(sum_account).replace("(","")
	sum_account = (str(sum_account).replace(")","")).replace(",","")
	sumaccount = str(sum_account)
	sumaccount = hash(int(sumaccount))
	
#	frappe.msgprint(_("TOTAL : {0}").format(sum_account))

	return sumaccount


@frappe.whitelist()
def create_bank_eft_file(posting_date, company, bank_name):
	fname = ""
	batch_no = ""
	x = " "

	if bank_name == "BSP":
		curr_date = posting_date
		abbr = frappe.db.get_value("Company", company, "abbr")
		
		fname = abbr+"_"+curr_date+"_DISDATA.PC1"

		save_path = 'fwcedu.org/public/files'
		filename = os.path.join(save_path, fname)

		ferp = frappe.new_doc("File")
		ferp.file_name = fname
		ferp.folder = "Home/QuickPay"
		ferp.is_private = 1

	f= open(filename,"w+")
	bank_data = []

	netpay = get_sum_netpay(posting_date, company, bank_name)
#	netpay = (netpay.replace("(",""))
#	netpay = (netpay.replace(")","")).replace(",","")

	if bank_name == "BSP":
		dr_account = ""

		bank_data = get_bank_data(posting_date, company, bank_name)
#		frappe.msgprint(_("Data : {0}").format(bank_data))

		account_total = get_sum_account(posting_date, company, bank_name)
#		frappe.msgprint(_("Account Total 1 : {0}").format(account_total))
#		account_total = (account_total.replace("(",""))
#		account_total = (account_total.replace(")","")).replace(",","").replace(".","")
#		frappe.msgprint(_("Account Total 2 : {0}").format(account_total))
#		account_total = ('%.11s' % account_total)
		length = 11
		fillchar = '0'

		if len(str(account_total)) == 11:
			account_total = str(account_total)
#			frappe.msgprint(_("TOTAL 1 : {0}").format(account_total))
		if len(str(account_total)) < 11:
			account_total = str(account_total).rjust(length, fillchar)
#			frappe.msgprint(_("TOTAL 2 : {0}").format(account_total))
		if len(str(account_total)) > 11:
			account_total = str(account_total)[1:]
#			frappe.msgprint(_("TOTAL 3 : {0}").format(account_total))

		posting_date = frappe.utils.formatdate(posting_date, "dd-MM-yyyy").replace("-", "")

		direct_debit = "12"
		bank_number = "03"
		state_number = "9"
		branch_number = "001"
		filler = " "

		if company == "FWC Education":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "113903701"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0679FWC                                                                                                                      \r\n"
			spacer = "FWC                 EDS0679                              \r\n"
		
		elif company == "Tupou Tertiary Institute":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "2000304531"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0679TTI                                                                                                                      \r\n"
			spacer = "TTI TUPOU TERTIARY  EDS0679                              \r\n"
		
		elif company == "Tupou College Toloa":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0119106901"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0769TOLOA FEES                                                                                                               \r\n"
			spacer = "TOLOA  TOLOA FEES   EDS0769                              \r\n"


		elif company == "Tupou College Toloa Faama":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0120232002"
			dr_account = dr_account.zfill(12)
			batch_no = "212"
			header = "EDS0769TOLOA FAAMA                                                                                                              \r\n"
			spacer = "TOLOA  TOLOA FARM   EDS0769                              \r\n"
		
		elif company == "Queen Salote College":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0117600301"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0769QUEEN SALOTE                                                                                                             \r\n"
			spacer = "QUEEN SALOTE        EDS0769                              \r\n"		
		
		elif company == "Tupou High School":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0119259201"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0769TUPOU HIGH SCOOL                                                                                                         \r\n"
			spacer = "TUPOU HIGH          EDS0769                              \r\n"
		
		quickpay_header = direct_debit + bank_number + state_number + branch_number + dr_account + batch_no
		
		f.write(quickpay_header)
		f.write(" ")
		f.write(posting_date)
		f.write(header)
		
#		for data in range(len(bank_data)):
		for data in bank_data:
			if not data['description'] or data['description'] is None:
					data['description'] = ''
			f.write('1303900100')
#			f.write('{0}053{1}{2}000000000000{3}'.format(data['account_number'], data['amount'], data['employee_name'].ljust(20), filler.ljust(24), data['description']))
			f.write('{0}053{1}{2}000000000000{3}'.format(data['account_number'], data['amount'], data['employee_name'].ljust(20), data['description'].rjust(36)))
			f.write(filler)
			f.write(spacer)
			
		f.write("1399")
#		f.write("00000000000")
		f.write(account_total)
		f.write(batch_no + 3*x)
		f.write(netpay+129*x+"\r\n")
#		f.write(str(netpay).zfill(10)+129*x+"\r\n")

#		f.write(account_total)
#==================================================================== BSP END ====================================================================================


#==================================================================== TDB START ==================================================================================


	if bank_name == "TDB":
		filler = "0000000000"
		numbers = len(bank_data)
		posting_date = frappe.utils.formatdate(posting_date, "dd-MM-yy").replace("-", "")
		
		f.write("0                             FWC                       077100            ")
		f.write(posting_date)
		f.write("s")
		f.write("\n")
		
		for data in bank_data:
			f.write('1077-100')
			f.write('{0} 53{1}{2}'.format(data['account_number'].rjust(9), data['amount'], data['employee_name'].ljust(32)))
			f.write("Pay"+posting_date+"-FWC     077-100\n")
		f.write("7")
		f.write("                   ")
		f.write(str(netpay).zfill(10))
		f.write(str(netpay).zfill(10))
		f.write(filler + "                        ")
		f.write(str(numbers).zfill(6))
		f.write(str(len(bank_data))).zfill(6)
#==================================================================== TDB END ====================================================================================

	frappe.msgprint(_("Bank File created - Please download the file : {0}").format(fname))
#	ferp.file_url = "/public/files/"+fname
	ferp.save()
	frappe.db.sql('''UPDATE `tabFile` SET company = %s, file_url = %s WHERE file_name = %s''',(company, "/files/"+fname, fname), as_dict=True)
	f.close()

