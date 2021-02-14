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
import pandas as p 

from frappe import _, msgprint, utils
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, datetime, comma_and
from collections import defaultdict
from werkzeug.wrappers import Response
format = "%Y-%m-%d %H:%M:%S"

#reload(sys)
#sys.setdefaultencoding('utf-8')


def execute(filters=None):
	global data
	data = []

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

def get_bank_data(posting_date, bank_name):

	bankdata = []

	fields = ["employee", "bank_name", "bank_ac_no", "salary_mode", "salary_comment"]
	
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
#	conditions = get_conditions(filters)

	entry = frappe.db.sql(""" select employee, employee_name, net_pay, payment_details
		from `tabSalary Slip`
		where docstatus = 1
		and posting_date = %s
		and bank_name = %s """,(posting_date, bank_name), as_dict =1)

	for d in entry:

		employee = {
			"employee_name" : (d.employee_name).replace("'",""),
#			"employee" : d.employee,
			"net_pay" : (str(d.net_pay)).replace(".","").zfill(10),
			"payment_details" : d.payment_details,
			"bank" : d.bank_name
		}

		if employee_data_dict.get(d.employee).get("salary_mode") == "Bank":
			employee["bank"] = employee_data_dict.get(d.employee).get("bank_name")
			employee["account_no"] = employee_data_dict.get(d.employee).get("bank_ac_no")
		
			bankdata.append(employee)

	return bankdata


@frappe.whitelist()
def create_bank_eft_file(posting_date, bank_name):

	curr_date = posting_date
	if bank_name == "BSP":
		fname = "FWC_EDU_"+curr_date+".PC1"
	if bank_name == "TDB":
		fname = "FWC_EDU_PAY-"+curr_date+".aba"
	save_path = 'fwc.edu/private/files'
	file_name = os.path.join(save_path, fname)
	ferp = frappe.new_doc("File")
	ferp.file_name = fname
	ferp.folder = "Home"
	ferp.is_private = 1
	ferp.file_url = "/private/files/"+fname

	f= open(file_name,"w+")
	bank_data = []

	bank_data = get_bank_data(posting_date, bank_name)

	netpay = get

	if bank_name == "BSP":
		f.write("1203900100")
		f.write("0123456789")
		f.write(" ")
		f.write(posting_date.replace("-", ""))
		f.write("EDS0769FWC\n")

	if bank_name == "TDB":
		f.write("0                             TDB                       077100            ")
		f.write(posting_date.replace("-", ""))
		f.write("\n")

#	txt = "^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR2,2~SD15^JUS^LRN^CI0^XZ^XA^MMT^PW812^LL0406^LS0"
	filler = ""

	for data in bank_data:
		if data['bank'] == "BSP":
			data['bank'] = "FWC                 EDS0769"
		if data['bank'] == 'TDB':
			data['bank'] = "Pay"+posting_date+"-TDB     077-100"
		
		if not data['payment_details']:
			data['payment_details'] = filler.ljust(36)
		if data['payment_details']:
			data['payment_details'] = filler + data['payment_details'].rjust(36)

##		number_labels = int(number_labels)
#		nol = int(number_labels) + 1
#		for x in xrange(1, nol):
#		f.write("^XA^MMT^PW812^LL0406^LS0")
#		f.write(str(data))

		f.write('1303900100')
		f.writelines('{0}053{1}{2}000000000000{3} {4}\n'.format(data['account_no'], data['net_pay'], data['employee_name'].ljust(20), data['payment_details'], data['bank']))

#		f.write("^FT250,79^A0R,28,28^FH\^FD%s^FS" % (rows[0]))
#		f.write("^FT533,53^A0R,28,28^FH\^FD%s^FS" % (rows[1]))
#		f.write("^FT300,301^BQN,2,8^FH\^FDMA1%s^FS" % (rows[0]))
#		f.write("^PQ1,0,1,Y^XZ")
#			txt += "^FT250,79^A0R,28,28^FH\^FD%s^FS" % rows[0]
#	f.insert(txt)
	frappe.msgprint(_("Text File created - Please check File List to download the file"))
	ferp.save()
	f.close()
#	return bank_data

