// Copyright (c) 2022, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Level TOP by Subject"] = {
	filters: [
		{
			fieldname:"program",
			label: __("Program"),
			fieldtype: "Link",
			options : 'Program',
			width: "100px",
			reqd: 0,
			hidden:1
		},
		{
			fieldname:"academic_term",
			label:__("Academic Term"),
			fieldtype:"Link",
			options: "Academic Term",
			width: "90px",
			reqd: 1
		},
		{
			fieldname:"subject",
			label: __("Subject"),
			fieldtype: "Link",
			options : "Course",
			reqd: 1,
		},
		
		{
			fieldname:"level",
			label: __("Choose Level"),
			fieldtype: "Select",
			options : [
				"",
				{ "value": "L1", "label": __("FORM 1 LEVEL") },
				{ "value": "L2", "label": __("FORM 2 LEVEL") },
				{ "value": "L3", "label": __("FORM 3 LEVEL") },
				{ "value": "L4", "label": __("FORM 4 LEVEL") },
				{ "value": "L5", "label": __("FORM 5 LEVEL") },
				{ "value": "L6", "label": __("FORM 6 LEVEL") },
				{ "value": "L7", "label": __("FORM 7 LEVEL") },
			],
			reqd: 1,

		},
		
		
	]
};

