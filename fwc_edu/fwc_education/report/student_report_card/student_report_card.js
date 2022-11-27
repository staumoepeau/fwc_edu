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
					frappe.query_report.set_filter_value('title', value["title"].toUpperCase());
					});

					frappe.db.get_value('Program Enrollment', {'student': student}, ["program"], function(value) {
					frappe.query_report.set_filter_value('program',value["program"]);
					});

					if (academic_term = "2022 (Term 1)"){
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
									
									if(r.message) {
										frappe.query_report.set_filter_value('midyear_position', r.message[0]);
										frappe.query_report.set_filter_value('overall_position', r.message[1]);
										frappe.query_report.set_filter_value('class_total', r.message[2]);
									}
								//	console.log(r.message)
								//	report.page.clear_secondary_action()	
								}
							});
						}
					if (academic_term = "2022 (Term 4)"){
						
						frappe.call({
							method: "fwc_edu.fwc_education.api.get_final_second_half",
							args: {
									"student": student,
									"term": academic_term,						
								},
								callback: function(e) {
									//console.log(data)
									if(e.message) {
										frappe.query_report.set_filter_value('final_second_half_score', e.message[0]);
										frappe.query_report.set_filter_value('grand_total', e.message[1]);
										
									
									}
									console.log(e.message)
									//	report.page.clear_secondary_action()	
								}
						});

						frappe.call({
							method: "fwc_edu.fwc_education.api.get_finalsecond_half_position",
							args: {
									"student": student,
									"term": academic_term,						
								},
								callback: function(e) {
									//console.log(data)
									if(e.message) {
										frappe.query_report.set_filter_value('finalsecond_half_position', e.message[0]);
										frappe.query_report.set_filter_value('finalclass_total', e.message[1]);
										frappe.query_report.set_filter_value('overall_level', e.message[2]);
									
									}
									console.log(e.message)
									//	report.page.clear_secondary_action()	
								}
						});

						frappe.call({
							method: "fwc_edu.fwc_education.api.get_final_overall_position",
							args: {
									"student": student,
									"term": academic_term,						
								},
								callback: function(e) {
									//console.log(data)
									if(e.message) {
										frappe.query_report.set_filter_value('final_overall_position', e.message);
									
									}
									console.log(e.message)
									//	report.page.clear_secondary_action()	
								}
						});

						frappe.call({
							method: "fwc_edu.fwc_education.api.get_honour_board",
							args: {
									"student": student,
									"term": academic_term,						
								},
								callback: function(e) {
									//console.log(data)
									if(e.message) {
										frappe.query_report.set_filter_value('honour_board', e.message[0]);
									
									}
									console.log(e.message)
									//	report.page.clear_secondary_action()	
								}
						});
					}
							
				} else {
					frappe.query_report.set_filter_value('title', "");
					frappe.query_report.set_filter_value('program', "");
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
//=========================================================================================================================
		{
			"fieldname": "final_second_half_score",
			"label": __("Final Second Half"),
			"fieldtype": "Data",
			"hidden": 1
		},

		{
			"fieldname": "finalsecond_half_position",
			"label": __("Final Second Half Position"),
			"fieldtype": "Data",
			"hidden": 1
		},

		{
			"fieldname": "finalclass_total",
			"label": __("Class Total"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "grand_total",
			"label": __("Grand Total"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "final_overall_position",
			"label": __("Final Overall Position"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "overall_level",
			"label": __("Total Level"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "honour_board",
			"label": __("Honour Board"),
			"fieldtype": "Data",
			"hidden": 1
		},
		{
			"fieldname": "level",
			"label": __("Level"),
			"fieldtype": "Data",
			"hidden": 1
		},

	],
};