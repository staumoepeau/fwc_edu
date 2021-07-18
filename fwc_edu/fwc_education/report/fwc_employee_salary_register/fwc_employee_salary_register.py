# Copyright (c) 2013, Sione Taumoepeau and contributors
# For license information, please see license.txt

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
	
	employee_salary = get_employee_salary(filters)
	if not employee_salary: return [], []

	columns, earning_types, ded_types = get_columns(employee_salary)
	ss_earning_map = get_ss_earning_map()
	ss_ded_map = get_ss_ded_map()

	data = []
	for ss in employee_salary:
		row = [ss.employee, ss.employee_name, ss.department]

		if ss.duty_allowance is not None: columns[3] = columns[3].replace('-1','120')
		if ss.duty is not None: columns[4] = columns[4].replace('-1','120')
#		if ss.designation is not None: columns[5] = columns[5].replace('-1','120')
#		if ss.leave_without_pay is not None: columns[9] = columns[9].replace('-1','130')


		for e in earning_types:
			row.append(ss_earning_map.get(ss.employee, {}).get(e))
		
	
		for d in ded_types:
			row.append(ss_ded_map.get(ss.employee, {}).get(d))

			row += [ss.duty_allowance, ss.duty]
		
		data.append(row)

	return columns, data

def get_columns(employee_salary):
	"""
	columns = [
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + "::140",
	]
	"""
	columns = [
		_("Employee") + ":Link/Employee:120", 
		_("Employee Name") + "::140",
 		_("Department") + ":Link/Department:200",
#		_("Annual Salary") + ":Currency:120",
#		_("Basic") + ":Currency:120", 
#		_("Annual Duty") + ":Currency:80",
#		_("Duty") + ":Currency:80", 
#		_("Payment Days") + ":Float:120"
	]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)""" %
		(', '.join(['%s']*len(employee_salary))), tuple([d.name for d in employee_salary]), as_dict=1):
		salary_components[_(component.type)].append(component.salary_component)

	columns = columns + [(e + ":Currency:120") for e in salary_components[_("Earning")]] + [(d + ":Currency:120") for d in salary_components[_("Deduction")]] + \
		[_("Total Deduction") + ":Currency:120", _("Net Pay") + ":Currency:120"]

	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_employee_salary(filters):
		
	conditions = get_conditions(filters)

	status = filters.get("status")
	department = filters.get("department")
	
	employee_salary = frappe.db.sql("""SELECT temp.employee, temp.employee_name, tssa.salary_structure, tsd.salary_component, tsd.amount, tsd.parent, temp.status, temp.department
		FROM `tabEmployee` temp
			INNER JOIN `tabSalary Structure Assignment` tssa ON temp.employee = tssa.employee
			INNER JOIN `tabSalary Detail` tsd ON temp.employee = tsd.parent
			AND temp.status = %s
			AND temp.department = %s
		ORDER BY temp.employee""", (status, department), as_dict=1)

	return employee_salary or []

def get_conditions(filters):
	conditions = ""
	
	if filters.get("status"): conditions += " and status = %(status)s"
	if filters.get("department"): conditions += " and department = %(department)s"
#	if filters.get("employee"): conditions += " and employee = %(employee)s"
	
	return conditions, filters

def get_employee_doj_map():
	return	frappe._dict(frappe.db.sql("""
				SELECT
					employee,
					date_of_joining
				FROM `tabEmployee`
				"""))

#def get_ss_earning_map(employee_salary):
#	ss_earnings = frappe.db.sql("""select sd.parent, sd.salary_component, sd.amount, ss.employee
#		from `tabSalary Detail` sd, `tabEmployee` ss where sd.parent=ss.employee and sd.parent in (%s)""" %
#		(', '.join(['%s']*len(employee_salary))), tuple([d.employee for d in employee_salary]), as_dict=1)

#	ss_earning_map = {}
#	for d in ss_earnings:
#
#	return ss_earning_map

def get_ss_earning_map():
	ss_earnings = frappe.db.sql(""" SELECT temp.employee, temp.employee_name, tssa.salary_structure, tsd.salary_component, tsd.amount, tsd.parent
			FROM `tabEmployee` temp
				INNER JOIN `tabSalary Structure Assignment` tssa ON temp.employee = tssa.employee
				INNER JOIN `tabSalary Detail` tsd ON temp.employee = tsd.parent
			ORDER BY temp.employee""", as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_earning_map[d.parent][d.salary_component] = flt(d.amount)

	
	return ss_earning_map

def get_ss_ded_map():
	ss_deductions = frappe.db.sql(""" SELECT temp.employee, temp.employee_name, tssa.salary_structure,
			IF(tsd.salary_component LIKE 'MBF%', 'MBF', 
				IF(sd.salary_component LIKE 'BSP%, 'BSP',
				  IF(sd.salary_component LIKE 'TDB%', 'TDB', sd.salary_component))) as salary_component, sum(tsd.amount), tsd.parent
			FROM `tabEmployee` temp
				INNER JOIN `tabSalary Structure Assignment` tssa ON temp.employee = tssa.employee
				INNER JOIN `tabSalary Detail` tsd ON temp.employee = tsd.parent
			GROUP BY tsd.salary_component
			ORDER BY temp.employee""", as_dict=1)
	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_ded_map[d.parent][d.salary_component] = flt(d.amount)
	msgprint(_("Data {0}"). format(ss_ded_map))
	return ss_ded_map