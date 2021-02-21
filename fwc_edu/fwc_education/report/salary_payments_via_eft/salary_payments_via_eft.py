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

def get_bank_data(postingdate, department, bankname):

	bankdata = []
	bank_data = []

	fields = ["employee", "bank_name", "bank_ac_no", "salary_mode", "department", "salary_comment"]
	
	employee_details = frappe.get_list("Employee", fields = fields)
	employee_data_dict = {}

	for d in employee_details:
		employee_data_dict.setdefault(
			d.employee,{
				"account_number" : d.bank_ac_no,
				"salary_mode" : d.salary_mode,
				"bank_name": d.bank_name,
				"department": d.department,
				"salary_comment": d.salary_comment

			}
		)


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
	
	entry = frappe.db.sql(""" SELECT employee, employee_name, net_pay as amount, mode_of_payment, bank_account_no, bank_name, department
		FROM `tabSalary Slip`
		WHERE docstatus = 1 
		AND posting_date = %s
		AND department = %s
        AND bank_name = %s
		""", (postingdate, department, bankname), as_dict=1)

	for e in other:
		employee = {
			"employee_name" : (e.employee_name).replace("'",""),
			"employee": e.employee,
#			"amount" : ((str(e.amount)).replace(".","")).zfill(10),
			"amount" : (str(int((e.amount)*100))).zfill(10),
			"bank_name" : e.bankname,
			"account_number": e.account_number.replace("-",""),
			"department": e.department
		}

		bank_data.append(employee)

	for d in entry:

		employee = {
			"employee_name" : (d.employee_name).replace("'",""),
#			"employee" : d.employee,
			"amount" : (str(int((d.amount)*100))).zfill(10),
			"payment_details" : d.payment_details,
			"bank_name" : d.bank_name,
			"account_number": d.bank_account_no.replace("-",""),
		}

		bank_data.append(employee)

	return bank_data


def get_sum_netpay(posting_date, department, bank_name):

	netpay_1 = frappe.db.sql(""" select sum(net_pay)
		from `tabSalary Slip`
		where docstatus = 1
		and posting_date = %s
		and department = %s
		and bank_name = %s """,(posting_date, department, bank_name))
	
	netpay_2 = frappe.db.sql("""SELECT sum(tsd.amount) from `tabSalary Detail` tsd, `tabSalary Slip` tss
			WHERE tsd.parent = tss.name
			AND tsd.abbr LIKE %s
			AND tsd.docstatus = 1
            AND tss.posting_date = %s
			AND tss.department = %s
			""", ("%" + bank_name + "%", posting_date, department))
	
	if bank_name == "BSP":
		netpay = netpay_1
		
	if bank_name == "TDB":
		netpay = np.add(netpay_1, netpay_2)
		netpay = str(netpay).replace("[[","")
		netpay = (str(netpay).replace("]]","")).replace(",","")

	netpay = str(netpay).replace("(","")
	netpay = (str(netpay).replace(")","")).replace(",","")
	netpay = ((str(netpay)).replace(".","")).zfill(10)

	return netpay

def get_sum_account(posting_date, department, bank_name):

	sum_account = frappe.db.sql(""" select sum(bank_account_no)
		from `tabSalary Slip`
		where docstatus = 1
		and posting_date = %s
		and department = %s
		and bank_name = %s """,(posting_date, department, bank_name))
	
	sum_account = (str(sum_account)).replace(".","")

	return sum_account


@frappe.whitelist()
def create_bank_eft_file(posting_date, department, bank_name):

	curr_date = posting_date
	if bank_name == "BSP":
		fname = "FWC_EDU_"+curr_date+".PC1"
#		bank_data = get_bank_data(posting_date, bank_name)

	if bank_name == "TDB":
		fname = "FWC_EDU_PAY-"+curr_date+".aba"
#		bank_data = get_other_bankdata(posting_date, bank_name)

	save_path = 'fwc.edu/private/files'
	file_name = os.path.join(save_path, fname)
	ferp = frappe.new_doc("File")
	ferp.file_name = fname
	ferp.folder = "Home"
	ferp.is_private = 1
	ferp.file_url = "/private/files/"+fname

	f= open(file_name,"w+")
	bank_data = []
	bank_data = get_bank_data(posting_date, department, bank_name)

	netpay = get_sum_netpay(posting_date, department, bank_name)
	netpay = (netpay.replace("(",""))
	netpay = (netpay.replace(")","")).replace(",","")

	if bank_name == "BSP":

#		bank_data = get_bank_data(posting_date, department, bank_name)
		account_total = get_sum_account(posting_date, department, bank_name)
		account_total = (account_total.replace("(",""))
		account_total = (account_total.replace(")","")).replace(",","")
		account_total = ('%.11s' % account_total)

		posting_date = frappe.utils.formatdate(posting_date, "dd-MM-yyyy").replace("-", "")

		direct_debit = "12"
		bank_number = "03"
		state_number = "9"
		branch_number = "001"
		fwc_account = "113903701"
		batch_no = "211"
		quickpay_header = direct_debit + bank_number + state_number + branch_number + fwc_account.zfill(12) + batch_no
		
		f.write(quickpay_header)
		f.write(" ")
		f.write(posting_date)
		f.write("EDS0769FWC\n")
		filler = " "
#		for data in range(len(bank_data)):
		for data in bank_data:
#			if bank_data[data]['bank_name'] == "BSP":
#				data['bank_name'] = "FWC                 EDS0769"		

			if not data['payment_details']:
				data['payment_details'] = filler.ljust(36)
			if data['payment_details']:
				data['payment_details'] = filler + data['payment_details'].rjust(36)

			f.write('1303900100')
			f.write('{0}053{1}{2}000000000000{3}'.format(data['account_number'], data['amount'], data['employee_name'].ljust(20), data['payment_details']))
			f.write("FWC                 EDS0769\n")
			
		f.write("1399")
		f.write(str(account_total))
		f.write("211   ")
		f.write(str(netpay).zfill(10))
		
#==================================================================== BSP END ====================================================================================

#==================================================================== TDB START ==================================================================================
	filler = "0000000000"
	numbers = len(bank_data)

	if bank_name == "TDB":
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
#		f.write(str(len(bank_data))).zfill(6)

#==================================================================== TDB END ====================================================================================

	frappe.msgprint(_("Text File created - Please check File List to download the file", ferp.file_url))
	ferp.save()
	f.close()



def download_file():
	print("Inside Download")
	response = Response()
	filename = "qrcode.txt"
	frappe.response.filename = "qrcode.txt"
	response.mimetype = 'text/plain'
	response.charset = 'utf-8'
	with open("site1.local/public/files/qrcode.txt", "rb") as fileobj:
		filedata = fileobj.read()
	print("Created Filedata")
	frappe.response.filecontent = filedata
	print("Created Filecontent")
	response.type = "download"
	response.headers[b"Content-Disposition"] = ("filename=\"%s\"" % frappe.response['filename'].replace(' ', '_')).encode("utf-8")
	response.data = frappe.response['filecontent']
	print(frappe.response)
#	frappe.tools.downloadify(filename);
#	return frappe.response