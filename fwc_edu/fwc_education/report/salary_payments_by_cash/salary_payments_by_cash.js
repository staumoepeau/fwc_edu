// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary Payments by Cash"] = {
	"filters": [
		{
			"fieldname":"posting_date",
			"label": __("Payroll Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"department",
			"label":__("Department"),
			"fieldtype":"Link",
			"options": "Department",
			"width": "100px",
			"reqd": 1
		},
	],
}
