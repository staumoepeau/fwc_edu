// Copyright (c) 2023, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Update"] = {
	"filters": [
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
