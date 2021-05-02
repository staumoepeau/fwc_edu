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
			"label": _("Bank"),
			"fieldname": "bank_name",
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
	conditions = get_conditions(filters)

	bankname = filters.get("bank_name")
	postingdate = filters.get("posting_date")
	company = filters.get("company")

	employee_list = frappe.db.sql("""SELECT sal.employee, sal.employee_name, 
			IF(ded.salary_component = "BSP", "BSP",
				IF(ded.salary_component = "TTI STAFF ASSOCIATION", "BSP",
					IF(ded.salary_component = "TTI ACCOUNT", "BSP",
						IF (ded.salary_component = "TDB", "TDB",
							IF(ded.salary_component = "SIA Finance" AND company = "Tupou Tertiary Institute", "BSP",
								IF (ded.salary_component = "MBF", "MBF", ded.salary_component))))))
			as bankname, ded.amount, ded.account_number
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
				"employee_name": e.employee_name,
				"employee": e.employee,
				"account_number" : e.account_number,
				"bank_name": e.bankname,
				"company": e.company
			}
		)

	other = frappe.db.sql("""SELECT sal.employee, sal.employee_name, 
			IF(ded.salary_component = "BSP", "BSP",
				IF(ded.salary_component = "TTI STAFF ASSOCIATION", "BSP",
					IF(ded.salary_component = "TTI ACCOUNT", "BSP",
						IF (ded.salary_component = "TDB", "TDB",
							IF(ded.salary_component = "SIA Finance" AND company = "Tupou Tertiary Institute", "BSP",
								IF (ded.salary_component = "MBF", "MBF", ded.salary_component))))))
			as bankname, ded.amount, ded.account_number
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
	
	entry = frappe.db.sql("""select employee, employee_name, net_pay as amount, mode_of_payment, 
		bank_account_no, bank_name, company, department, payment_details
		from `tabSalary Slip`
		where docstatus = 1
		and net_pay > 0 %s """
		%(conditions), as_dict =1)

	for e in other:
		employee = {
			"employee_name" : e.employee_name,
			"employee": e.employee,
			"amount" : e.amount,
			"bank_name" : e.bankname,
			"account_number": e.account_number,
			"company": e.company
		}

		data.append(employee)
	
	for d in entry:
		employee = {
			"employee_name" : d.employee_name,
			"employee": d.employee,
			"amount" : d.amount,
			"bank_name" : d.bank_name,
			"account_number": d.bank_account_no,
			"company": d.company

		}

		data.append(employee)
	return data

def get_bank_data(postingdate, company, bankname):

	bankdata = []
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


	employee_list = frappe.db.sql(""" SELECT sal.employee, sal.employee_name, 
			IF(ded.salary_component = "BSP", "BSP",
				IF(ded.salary_component = "TTI STAFF ASSOCIATION", "BSP",
					IF(ded.salary_component = "TTI ACCOUNT", "BSP",
						IF (ded.salary_component = "TDB", "TDB",
							IF(ded.salary_component = "SIA Finance" AND company = "Tupou Tertiary Institute", "BSP",
								IF (ded.salary_component = "MBF", "MBF", ded.salary_component))))))
			as bankname, ded.amount, ded.account_number
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

	other = frappe.db.sql(""" SELECT sal.employee, sal.employee_name, 
			IF(ded.salary_component = "BSP", "BSP",
				IF(ded.salary_component = "TTI STAFF ASSOCIATION", "BSP",
					IF(ded.salary_component = "TTI ACCOUNT", "BSP",
						IF (ded.salary_component = "TDB", "TDB",
							IF(ded.salary_component = "SIA Finance" AND company = "Tupou Tertiary Institute", "BSP",
								IF (ded.salary_component = "MBF", "MBF", ded.salary_component))))))
			as bankname, ded.amount, ded.account_number
			FROM `tabSalary Slip` sal
			INNER JOIN `tabSalary Detail` ded ON
				sal.name = ded.parent
			AND ded.parentfield = 'deductions'
			AND ded.parenttype = 'Salary Slip'
			AND ded.docstatus = 1
            AND sal.posting_date = %s
			AND sal.company = %s
			AND ded.amount > 0
            HAVING bankname = %s
			""", (postingdate, company, bankname), as_dict=1)
	
	entry = frappe.db.sql(""" SELECT employee, employee_name, net_pay as amount, 
		mode_of_payment, bank_account_no, bank_name, company, department, payment_details
		FROM `tabSalary Slip`
		WHERE net_pay != 0 
		AND posting_date = %s
		AND company = %s
		AND docstatus = 1
        AND bank_name = %s
		""", (postingdate, company, bankname), as_dict=1)

	for d in entry:
		employee = {
			"employee_name" : ((d.employee_name.upper()).replace(".","").replace("'","").replace("  "," ")[:20]),
#			"employee" : d.employee,
			"amount" : (str(int((d.amount)*100))).zfill(10),
			"payment_details" : d.payment_details,
			"bank_name" : d.bank_name,
			"account_number": d.bank_account_no.replace("-",""),
		}

		bank_data.append(employee)
	
	for e in other:
		employee = {
			"employee_name" : ((e.employee_name.upper()).replace(".","").replace("'","").replace("  "," ")[:20]),
			"employee": e.employee,
			"amount" : (str(int((e.amount)*100))).zfill(10),
			"bank_name" : e.bankname,
			"account_number": e.account_number.replace("-",""),
			"company": e.company
		}

		bank_data.append(employee)

	return bank_data

def get_sum_netpay(posting_date, company, bank_name):
	netpay = ""
	netpay_1, netpay_2 = [], []

	netpay_1 = frappe.db.sql(""" select sum(net_pay)
		from `tabSalary Slip`
		where docstatus = 1
		and posting_date = %s
		and company = %s
		and bank_name = %s """,(posting_date, company, bank_name))
	
	netpay_2 = frappe.db.sql("""SELECT sum(tsd.amount) from `tabSalary Detail` tsd, `tabSalary Slip` tss
			WHERE tsd.parent = tss.name
			AND tsd.salary_component = %s
			AND tsd.docstatus = 1
            AND tss.posting_date = %s
			AND tss.company = %s
			""", (bank_name, posting_date, company))
	
	if np.array(netpay_1):
		netpay = netpay_1
		frappe.msgprint(_("PAY 1 : {0}").format(netpay_1))

	if np.array(netpay_2):
		netpay = netpay_2
		frappe.msgprint(_("PAY 2 : {0}").format(netpay_2))


	if	np.array(netpay_1) and np.array(netpay_2):
		netpay = np.add(netpay_1, netpay_2)
		frappe.msgprint(_("NAT PAY : {0}").format(netpay))


	netpay = str(netpay).replace("[[","")
	netpay = (str(netpay).replace("]]","")).replace(",","")
	netpay = str(netpay).replace("(","")
	netpay = (str(netpay).replace(")","")).replace(",","")
	netpay = ((str(netpay)).replace(".","")).zfill(10)

	return netpay

def get_sum_account(posting_date, company, bank_name):
	sum_account = ""

	sum_account_1 = frappe.db.sql(""" select sum(bank_account_no)
		from `tabSalary Slip`
		where docstatus = 1
		and posting_date = %s
		and company = %s
		and bank_name = %s """,(posting_date, company, bank_name))
	
	sum_account_2 = frappe.db.sql("""SELECT sum(account_number) from `tabSalary Detail` tsd, `tabSalary Slip` tss
			WHERE tsd.parent = tss.name
			AND tsd.salary_component = %s
			AND tsd.docstatus = 1
            AND tss.posting_date = %s
			AND tss.company = %s
			""", (bank_name, posting_date, company))
	
	
	if np.array(sum_account_1):
		sum_1 = np.array(sum_account_1)
		sum_account = sum_1.astype(int)
		frappe.msgprint(_("SUM 1 : {0}").format(sum_account))

	if np.array(sum_account_2):
		sum_2 = np.array(sum_account_2)
		sum_account = sum_2.astype(int)
		frappe.msgprint(_("SUM 2 : {0}").format(sum_account))

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
	
	frappe.msgprint(_("TOTAL : {0}").format(sum_account))

	return sumaccount


@frappe.whitelist()
def create_bank_eft_file(posting_date, company, bank_name):
	fname = ""
	batch_no = ""
	x = " "

	curr_date = posting_date
	abbr = frappe.db.get_value("Company", company, "abbr")
	
	fname = abbr+"_"+curr_date+"_DISDATA.PC1"

	save_path = 'edu.fwc.to/public/files'
	filename = os.path.join(save_path, fname)

	ferp = frappe.new_doc("File")
	ferp.file_name = fname
	ferp.folder = "Home/QuickPay"
	ferp.is_private = 1
#	ferp.file_url = "/public/files/"+fname


	f= open(filename,"w+")
	bank_data = []

	netpay = get_sum_netpay(posting_date, company, bank_name)
	netpay = (netpay.replace("(",""))
	netpay = (netpay.replace(")","")).replace(",","")

	if bank_name == "BSP":
		dr_account = ""

		bank_data = get_bank_data(posting_date, company, bank_name)

		account_total = get_sum_account(posting_date, company, bank_name)
		frappe.msgprint(_("Account Total 1 : {0}").format(account_total))
#		account_total = (account_total.replace("(",""))
#		account_total = (account_total.replace(")","")).replace(",","").replace(".","")
#		frappe.msgprint(_("Account Total 2 : {0}").format(account_total))
#		account_total = ('%.11s' % account_total)
		length = 11
		fillchar = '0'

#		if len(account_total) == 11:
#			account_total = str(account_total)
#		if len(account_total) < 11:
#			account_total = str(account_total).rjust(length, fillchar)
#		if len(account_total) > 11:
		account_total = str(account_total)[:11]

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
			header = "EDS0679TTI                                                                                                                      \r\n"
			spacer = "FWC                 EDS0679                              \r\n"
		
		elif company == "Tupou Tertiary Institute":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "2000304531"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0679TTI                                                                                                                      \r\n"
			spacer = "TTI                 EDS0679                               \r\n"
		
		elif company == "Tupou College Toloa":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0119106901"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0769TOLOA FEES                                                                                                               \r\n"
			spacer = "TOLOA        TOLOA FEES          EDS0769                               \r\n"

		elif company == "Tupou College Toloa Faama":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0120232002"
			dr_account = dr_account.zfill(12)
			batch_no = "212"
			header = "EDS0769TCT                                                                                                                      \r\n"
			spacer = "TOLOA        TOLOA FARM          EDS0769                               \r\n"
		
		elif company == "Queen Salote College":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0117600301"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0769QSC                                                                                                                      \r\n"
			spacer = "QSC                 EDS0769                               \r\n"
		
		elif company == "Tupou High School":
			abbr = frappe.db.get_value("Company", company, "abbr")
			dr_account = "0119259201"
			dr_account = dr_account.zfill(12)
			batch_no = "211"
			header = "EDS0769THS                                                                                                                      \r\n"
			spacer = "THS                 EDS0769                               \r\n"
		
		quickpay_header = direct_debit + bank_number + state_number + branch_number + dr_account + batch_no
		
		f.write(quickpay_header)
		f.write(" ")
		f.write(posting_date)
		f.write(header)
		
#		for data in range(len(bank_data)):
		for data in bank_data:

			f.write('1303900100')
			f.write('{0}053{1}{2}000000000000{3}'.format(data['account_number'], data['amount'], data['employee_name'].ljust(20), filler.ljust(24)))
			f.write(spacer)
			
		f.write("1399")
#		f.write("00000000000")
		f.write(account_total)
		f.write(batch_no + 3*x)
		f.write(str(netpay).zfill(10)+129*x+"\r\n")

#		f.write(account_total)
#==================================================================== BSP END ====================================================================================


#==================================================================== TDB START ==================================================================================
#	filler = "0000000000"
#	numbers = len(bank_data)
#	if bank_name == "TDB":
#		posting_date = frappe.utils.formatdate(posting_date, "dd-MM-yy").replace("-", "")
#		f.write("0                             FWC                       077100            ")
#		f.write(posting_date)
#		f.write("s")
#		f.write("\n")
#		for data in bank_data:
#			f.write('1077-100')
#			f.write('{0} 53{1}{2}'.format(data['account_number'].rjust(9), data['amount'], data['employee_name'].ljust(32)))
#			f.write("Pay"+posting_date+"-FWC     077-100\n")
#		f.write("7")
#		f.write("                   ")
#		f.write(str(netpay).zfill(10))
#		f.write(str(netpay).zfill(10))
#		f.write(filler + "                        ")
#		f.write(str(numbers).zfill(6))
#		f.write(str(len(bank_data))).zfill(6)
#==================================================================== TDB END ====================================================================================

	frappe.msgprint(_("Bank File created - Please download the file : {0}").format(fname))
#	ferp.file_url = "/public/files/"+fname
	ferp.save()
	frappe.db.sql('''UPDATE `tabFile` SET file_url = %s WHERE file_name = %s''',("/files/"+fname, fname), as_dict=True)
	f.close()
