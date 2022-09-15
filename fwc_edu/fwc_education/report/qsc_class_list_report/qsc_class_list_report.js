// Copyright (c) 2022, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["QSC Class List Report"] = {
	filters: [
		{
			fieldname:"program",
			label: __("Class"),
			fieldtype: "Link",
			options : 'Program',
			width: "100px",
			reqd: 1,
			hidden:0
		},
	]
};
