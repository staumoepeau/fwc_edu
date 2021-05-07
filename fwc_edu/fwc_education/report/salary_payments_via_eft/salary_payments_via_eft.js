// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Salary Payments via EFT"] = {
	"filters": [
		{
			"fieldname": "salary_mode",
			"label": __("Salary Mode"),
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
			"options":[" ", "BSP", "TDB", "ANZ", "MBF"],
			"width": "90px",
//			"reqd": 1
		},
//		{
//			"fieldname":"branch",
//			"label": __("Branch"),
//			"fieldtype": "Link",
//			"options": "Branch",
//			"width": "100px",
//			"reqd": 1
//		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		
	],
//				method: "fwc_edu.fwc_education.report.salary_payments_via_eft.salary_payments_via_eft.create_bank_eft_file",

//window.open("/api/method/frappe.mypyfile.download_test");
	onload: function(report) {

		report.page.set_primary_action('Transfer to Bank', function() {
			var args = "as a draft"
				var reporter = frappe.query_reports["Salary Payments via EFT"];
					reporter.maketextfile(report);
		},)
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
				"company": filters.company,
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
