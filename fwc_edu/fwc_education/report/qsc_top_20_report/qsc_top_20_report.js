// Copyright (c) 2022, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["QSC TOP 20 Report"] = {
	"filters": [
		{
			"fieldname":"program",
			"label": __("Program"),
			"fieldtype": "Link",
			"options" : 'Program',
			"width": "100px",
			"reqd": 0
		},
		{
			"fieldname":"level",
			"label": __("Level"),
			"fieldtype": "Select",
			"options" : ['L1','L2','L3','L4','L5','L6','L7','TVET'],
			"width": "100px",
			"reqd": 0

		},
	]
};
