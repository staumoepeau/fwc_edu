// Copyright (c) 2022, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Report Card"] = {
	"filters": [
		{
			"fieldname":"program",
			"label": __("Class"),
			"fieldtype": "Link",
			"options" : 'Program',
			"width": "100px",
			"reqd": 0,
			"hidden":1
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
			"fieldname": "student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student",
			"reqd": 1,
			on_change: () => {
				var student = frappe.query_report.get_filter_value('student');			
				var academic_term = frappe.query_report.get_filter_value('academic_term');		
	
				if (student) {
					frappe.db.get_value('Student', student, ["title"], function(value) {
					frappe.query_report.set_filter_value('title', value["title"]);
					});

					frappe.db.get_value('Program Enrollment', {'student': student}, ["program"], function(value) {
					frappe.query_report.set_filter_value('program', value["program"]);

					});

					
					frappe.call({
						method: "fwc_edu.fwc_education.api.get_total_score",
						args: {
								"student": student,
								"term": academic_term,						
							},
							callback: function(e) {
								//console.log(data)
								if(e.message) {
									frappe.query_report.set_filter_value('total_score', e.message);
								
								}
								console.log(e.message)
								//	report.page.clear_secondary_action()	
							}
					});

					frappe.call({
						method: "fwc_edu.fwc_education.api.get_midyear_score",
						args: {
							"student": student,
							"term": academic_term,						
						},
						callback: function(data) {
						//	console.log(data.message)
							if(data.message) {
								frappe.query_report.set_filter_value('score', data.message);
							}
						//	console.log(data.message)
						//	report.page.clear_secondary_action()	
						}
					});

					frappe.call({
						method: "fwc_edu.fwc_education.api.get_midyear_position",
						args: {
							"student": student,
							"term": academic_term,						
						},
						callback: function(r) {
							console.log(r)
							if(r.message) {
								frappe.query_report.set_filter_value('midyear_position', r.message[0]);
								frappe.query_report.set_filter_value('overall_position', r.message[1]);
								frappe.query_report.set_filter_value('class_total', r.message[2]);
							}
						//	console.log(r.message)
						//	report.page.clear_secondary_action()	
						}
					});
							
				} else {
					frappe.query_report.set_filter_value('title', "");
					frappe.query_report.set_filter_value('program', "");
					frappe.query_report.set_filter_value('total_score', "");
				}
			}

		},
		{
			"fieldname":"academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"width": "100px",
			"reqd": 0,
			"hidden" : 1
			
		},
		{
			"fieldname": "title",
			"label": __("Student Name"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "score",
			"label": __("Mid Year Score"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "total_score",
			"label": __("Total Score"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "overall_position",
			"label": __("Overall Position"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "midyear_position",
			"label": __("Mid Year Position"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "class_total",
			"label": __("Class Total"),
			"fieldtype": "Data",
			"hidden": 1
		},

	],
};