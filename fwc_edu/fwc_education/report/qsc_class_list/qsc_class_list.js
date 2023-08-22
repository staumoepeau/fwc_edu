// Copyright (c) 2023, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["QSC Class List"] = {
	filters: [
		{
			fieldname:"program",
			label: __("Program"),
			fieldtype: "Link",
			options : 'Program',
			width: "100px",
			reqd: 1,
			hidden:0
		},
		{
			"fieldname":"academic_term",
			"label":__("Academic Term"),
			"fieldtype":"Link",
			"options": "Academic Term",
			"width": "90px",
			"reqd": 1
		},	
	]
};
