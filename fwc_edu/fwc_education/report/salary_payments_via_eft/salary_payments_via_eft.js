// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Salary Payments via EFT"] = {
		"filters": [
			{
				"fieldname": "type",
				"label": __("Type"),
				"fieldtype": "Select",
				"options":["", "Bank", "Cash"]

			},
			{
				"fieldname":"posting_date",
				"label": __("Payroll Date"),
				"fieldtype": "Date",
				"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
				"reqd": 1,
				"width": "100px"
			},
			{
				"fieldname":"bank_name",
				"label":__("Bank Name"),
				"fieldtype":"Select",
				"options":["BSP", "TDB", "ANZ", "MBF"],
				"default": "BSP",
				"width": "90px"
			},
		],
//				method: "fwc_edu.fwc_education.report.salary_payments_via_eft.salary_payments_via_eft.create_bank_eft_file",


		onload: function(report) {

			report.page.set_primary_action('Bank', function() {
				var args = "as a draft"
					var reporter = frappe.query_reports["Salary Payments via EFT"];
						reporter.maketextfile(report);
			}, 'octicon octicon-plus')
		},

		isNumeric: function( obj ) {
		return !jQuery.isArray( obj ) && (obj - parseFloat( obj ) + 1) >= 0;
		},
		maketextfile: function(report){
		var filters = report.get_values();
		if (filters.bank_name) {
			return frappe.call({
				method: "fwc_edu.fwc_education.report.salary_payments_via_eft.salary_payments_via_eft.create_bank_eft_file",
				args: {
					"posting_date": filters.posting_date,
					"bank_name": filters.bank_name
				},
				callback: function(r) {
					console.log(r)
//				if(r.message) {
//					frappe.set_route('List',r.message );
//				}
				}
			})
		} else {
			frappe.msgprint("Please select all filters for creating Text File")
		}
	},
}
