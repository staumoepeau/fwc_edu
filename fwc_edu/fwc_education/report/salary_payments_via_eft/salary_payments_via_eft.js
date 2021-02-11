// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.require("assets/erpnext/js/salary_slip_deductions_report_filters.js", function() {

	let eft_checklist_filter = erpnext.salary_slip_deductions_report_filters
	eft_checklist_filter['filters'].push({
		fieldname: "type",
		label: __("Type"),
		fieldtype: "Select",
		options:["", "Bank", "Cash"]
	})

	frappe.query_reports["Salary Payments via EFT"] = eft_checklist_filter
});
