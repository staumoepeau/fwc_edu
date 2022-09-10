// Copyright (c) 2022, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Report Card"] = {
	"filters": [
		{
			"fieldname": "student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student",
			"reqd": 1

		},
		{
			"fieldname":"academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"width": "100px",
			"reqd": 0
			
		},
		{
			"fieldname":"academic_term",
			"label":__("Academic Term"),
			"fieldtype":"Link",
			"options": "Academic Term",
			"width": "90px",
			"reqd": 0
		},
//		{
//			"fieldname":"branch",
//			"label": __("Branch"),
//			"fieldtype": "Link",
//			"options": "Branch",
//			"width": "100px",
//			"reqd": 1
//		},
//		{
//			"fieldname":"program",
//			"label": __("Class"),
//			"fieldtype": "Link",
//			"options": "Program",
//			"width": "100px",
//			"reqd": 1
//		},
	],
//	refresh: function (report){

//		report.page.clear_secondary_action()	

//	},
//	onload: function(report) {

			
//		report.page.set_primary_action('Print Report Card', function() {
//			var args = "as a draft"
//				var reporter = frappe.query_reports["Print Report Card"];
//					reporter.printreportcard(report);
//		},)
//	},

//	printreportcard: function(report){

//		var filters = report.get_values();
//		if (filters.student) {
//			return frappe.call({
//				method: "fwc_edu.fwc_education.report.student_report_card.student_report_card.print_report_card",
//				args: {
//					"student": filters.student,
//					"academic_year": filters.academic_year,
//					"academic_term": filters.academic_term,	
					
//				},
//				callback: function(r) {
//					console.log(r)
	//				if(r.message) {
	//					frappe.set_route('List',r.message );
	//				}
//					report.page.clear_secondary_action()	
//				}
//			})
//		} else {
//			frappe.msgprint("Please select all filters for creating Text File")
//		}
//	},
}

