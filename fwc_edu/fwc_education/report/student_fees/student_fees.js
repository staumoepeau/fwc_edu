// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Fees"] = {
	"filters": [
	{
		"fieldname": "program",
		"label": __("Program"),
		"fieldtype": "Link",
		"options": "Program",
		"width": "100px",
		"reqd" : 1
	},
	{
		"fieldname": "academic_year",
		"label": __("Academic Year"),
		"fieldtype": "Link",
		"options": "Academic Year",
		"width": "100px",
		"reqd" : 1
	},
	{
		"fieldname": "company",
		"label": __("School"),
		"fieldtype": "Link",
		"options": "Company",
		"width": "100px",
		"reqd": 1
	},

],
};
