// Copyright (c) 2022, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["QSC TOP 20 Report"] = {
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
			"fieldname":"academic_term",
			"label":__("Academic Term"),
			"fieldtype":"Link",
			"options": "Academic Term",
			"width": "90px",
			"reqd": 1
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

			on_change: function() {
				var levelClass = ""
				var level = frappe.query_report.get_filter_value('level');
				if (level){
					if (level = 'L1'){
						levelClass = "Form 1"
					}else if (level = 'L2'){
						levelClass = "Form 2"
					}else if (level = 'L3'){
						levelClass = "Form 3"
					}else if (level = 'L4'){
						levelClass = "Form 4"
					}else if (level = 'L5'){
						levelClass = "Form 5"
					}else if (level = 'L6'){
						levelClass = "Form 6"
					}else if (level = 'L7'){
						levelClass = "Form 7"
					}
					frappe.query_report.set_filter_value('classLevel', levelClass)

				} else {
					frappe.query_report.set_filter_value('classLevel', "");
				}
			} 
		},
		{
			fieldname:"classLevel",
			label: __("Class Level"),
			fieldtype: "Data",
			reqd: 0,
			hidden:1
		},
	]
};
