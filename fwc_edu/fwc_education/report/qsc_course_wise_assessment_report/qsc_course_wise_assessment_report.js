// Copyright (c) 2022, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["QSC Course Wise Assessment Report"] = {
	"filters": [
		{
			"fieldname":"academic_term",
			"label": __("Term"),
			"fieldtype": "Link",
			"options" : 'Academic Term',
			"width": "100px",
			"reqd": 1,
			"hidden": 0
		},
		{
			"fieldname":"student_group",
			"label": __("Student Group"),
			"fieldtype": "Link",
			"options" : 'Student Group',
			"width": "100px",
			"reqd": 1,
			on_change: () => {
				var student_group = frappe.query_report.get_filter_value('student_group');				
	
				if (student_group) {
					frappe.db.get_value('Student Group', student_group, ["program"], function(value) {
					frappe.query_report.set_filter_value('program', value["program"]);
					});

					frappe.db.get_value('Student Group', student_group, ["course"], function(value) {
					frappe.query_report.set_filter_value('course', value["course"]);

					});

							
				} else {
					frappe.query_report.set_filter_value('program', "");
					frappe.query_report.set_filter_value('course', "");
				}
			}

		},
		{
			"fieldname":"program",
			"label": __("Class"),
			"fieldtype": "Link",
			"options" : 'Program',
			"width": "100px",
			"reqd": 0,
			"hidden": 1
		},
		{
			"fieldname":"course",
			"label": __("Subjects"),
			"fieldtype": "Data",
			"width": "100px",
			"reqd": 0,
			"hidden": 1
		},
	]
};

