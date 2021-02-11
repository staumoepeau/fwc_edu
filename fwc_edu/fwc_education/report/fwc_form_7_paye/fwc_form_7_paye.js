// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.require("assets/erpnext/js/salary_slip_deductions_report_filters.js", function() {
	frappe.query_reports["FWC FORM 7 PAYE"] = erpnext.salary_slip_deductions_report_filters;
});