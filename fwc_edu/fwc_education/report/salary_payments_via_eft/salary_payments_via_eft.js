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
		onload: function(report) {
//			report.page.remove_inner_toolbar()
//			report.page.add_inner_button(__("Transfer"), function() {
//				frappe.msgprint("Transfer");
//			});
		report.page.add_action_icon(__("fa fa-credit-card fa-2x text-success"), function() {
			return  frappe.call({
				method: "fwc_edu.fwc_education.report.salary_payments_via_eft.create_bank_eft_file",
				callback: function(r) {
					console.log(r)
				}
			});		
		});
		}
	}
