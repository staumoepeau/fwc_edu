# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.utils import flt
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}
	currency = None
	if filters.get('currency'):
		currency = filters.get('currency')
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips: return [], []

	columns, earning_types, ded_types = get_columns(salary_slips, filters)
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips,currency, company_currency)
	doj_map = get_employee_doj_map()
	basic_annual = get_employee_annual_basic()
	mycompany = filters.get("company")

	data = []
	for ss in salary_slips:
		if mycompany == "FWC Education" or mycompany == "Mailefihi Siuilikutapu College":
			row = [ss.branch,ss.employee,ss.employee_name, ss.qualify_teaching_staff, basic_annual.get(ss.employee)]
		else:
			row = [ss.employee,ss.employee_name, ss.qualify_teaching_staff, basic_annual.get(ss.employee)]
#		row = [ss.name, ss.employee, ss.employee_name, basic_annual.get(ss.employee), ss.branch, ss.department, ss.designation,
#			ss.company, ss.start_date, ss.end_date, ss.leave_without_pay, ss.payment_days]

#		if ss.branch is not None: columns[3] = columns[3].replace('-1','120')
#		if ss.department is not None: columns[4] = columns[4].replace('-1','120')
#		if ss.designation is not None: columns[5] = columns[5].replace('-1','120')
#		if ss.leave_without_pay is not None: columns[9] = columns[9].replace('-1','130')


		for e in earning_types:
			row.append(ss_earning_map.get(ss.name, {}).get(e))

		if currency == company_currency:
			row += [flt(ss.gross_pay) * flt(ss.exchange_rate)]
		else:
			row += [ss.gross_pay]

#		for d in ded_types:
#			row.append(ss_ded_map.get(ss.name, {}).get(d))

#		row.append(ss.total_loan_repayment)

#		if currency == company_currency:
#			row += [flt(ss.total_deduction) * flt(ss.exchange_rate), flt(ss.net_pay) * flt(ss.exchange_rate)]
#		else:
#			row += [ss.total_deduction, ss.net_pay]

		for d in ded_types:
			row.append(ss_ded_map.get(ss.name, {}).get(d))

#		row.append(ss.total_loan_repayment)

#		if currency == company_currency:
#			row += [flt(ss.total_deduction) * flt(ss.exchange_rate), flt(ss.net_pay) * flt(ss.exchange_rate)]
#		else:
		row += [ss.net_pay]

#		row.append(currency or company_currency)
		data.append(row)

	return columns, data

def get_columns(salary_slips, filters):
	mycompany = filters.get("company")
	if mycompany == "FWC Education" or mycompany == "Mailefihi Siuilikutapu College":
		columns = [
			_("Branch") + ":Link/Branch:100",
			_("Employee") + ":Link/Employee:120",
			_("Employee Name") + "::140",
			_("Qualify Teaching Staff") + ":Check:80",
			_("Basic Salary") + ":Currency:120",
		]
	else:
		columns = [
			_("Employee") + ":Link/Employee:120",
			_("Employee Name") + "::140",
			_("Qualify Teaching Staff") + ":Check:80",
			_("Basic Salary") + ":Currency:120",
		]
		
	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sc.type,
		IF(sd.salary_component IN ('MBF', 'MBF02','MBF03','MBF04', 'MBF05'),'MBF',
			IF(sd.salary_component IN ('BSP', 'BSP02','BSP03','BSP04', 'BSP05'),'BSP',
				IF(sd.salary_component IN ('TDB', 'TDB02','TDB03','TDB04', 'TDB05'), 'TDB', 
					IF(sd.salary_component IN ('Retirement Fund', 'Retirement Fund - Voluntary'),'Retirement Fund', sd.salary_component)))) as salary_component
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	columns = columns + [(e + ":Currency:120") for e in salary_components[_("Earning")]] + \
		[_("Gross Pay") + ":Currency:120"] + [(d + ":Currency:120") for d in salary_components[_("Deduction")]] + \
		[_("Net Pay") + ":Currency:120"]

#	columns = columns + [(e + ":Currency:120") for e in salary_components[_("Earning")]] + \
#		[_("Gross Pay") + ":Currency:120"] + [(d + ":Currency:120") for d in salary_components[_("Deduction")]] + \
#		[_("Loan Repayment") + ":Currency:120", _("Total Deduction") + ":Currency:120", _("Net Pay") + ":Currency:120"]

	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date":filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)

	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where %s
		order by reports_group""" % conditions, filters, as_dict=1)
	
#	msgprint(_("Salary Slip {0}").format(teachingStaff))

	return salary_slips or []

def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if filters.get("from_date"): conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"): conditions += " and end_date <= %(to_date)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"

	return conditions, filters

def get_employee_annual_basic():
	return	frappe._dict(frappe.db.sql("""
				SELECT
					employee,
					basic_salary
				FROM `tabEmployee`
				"""))
			
def get_employee_doj_map():
	return	frappe._dict(frappe.db.sql("""
				SELECT
					employee,
					date_of_joining
				FROM `tabEmployee`
				"""))

def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, 
	sum(sd.amount) as amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s) group by sd.parent, sd.salary_component""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)

	ss_earning_map = {}
	
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] = flt(d.amount) * flt(d.exchange_rate if d.exchange_rate else 1)
		else:
			ss_earning_map[d.parent][d.salary_component] = flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(salary_slips, currency, company_currency):
    	
	ss_deductions = frappe.db.sql("""select distinct sd.parent,
		IF(sd.salary_component IN ('MBF', 'MBF02','MBF03','MBF04', 'MBF05'),'MBF',
			IF(sd.salary_component IN ('BSP', 'BSP02','BSP03','BSP04', 'BSP05'),'BSP',
				IF(sd.salary_component IN ('TDB', 'TDB02','TDB03','TDB04', 'TDB05'), 'TDB', 
                   IF(sd.salary_component IN ('Retirement Fund', 'Retirement Fund - Voluntary'),'Retirement Fund', sd.salary_component)))) as salary_component,
		IF(sd.salary_component IN ('MBF', 'MBF02','MBF03','MBF04', 'MBF05'),'MBF',
			IF(sd.salary_component IN ('BSP', 'BSP02','BSP03','BSP04', 'BSP05'),'BSP',
				IF(sd.salary_component IN ('TDB', 'TDB02','TDB03','TDB04', 'TDB05'), 'TDB', 
                   IF(sd.salary_component IN ('Retirement Fund', 'Retirement Fund - Voluntary'),'Retirement Fund', sd.salary_component)))) as salarycomponent,
		sum(sd.amount) as amount, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss 
		where sd.parent=ss.name and sd.parent in (%s) group by salarycomponent, sd.parent""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]) , as_dict=1)

	ss_ded_map = {}
#	msgprint(_("Deduction {0}").format(ss_deductions))

	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		
		ss_ded_map[d.parent][d.salary_component] = flt(d.amount)
	
	return ss_ded_map
