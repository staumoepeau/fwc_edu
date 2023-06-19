// Copyright (c) 2013, Sione Taumoepeau and contributors
// For license information, please see license.txt

frappe.query_reports["FWC Salary Register Qualify"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1,
			"width": "100px"
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default": "Submitted",
			"width": "100px"
		},
		{
			"fieldname":"qualify_teaching_staff",
			"label":__("Qualify Teacher"),
			"fieldtype":"Select",
			"options":["All","Yes", "No"],
			"width": "50px",
		},
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
//	"formatter": function (value, row, column, data, default_formatter) {
//        if (column.fieldname == "company") {
//            value = data.company;
//            column.is_tree = true;
//        }

//        value = default_formatter(value, row, column, data);
//        if (!data.branch) {
//            var $value = $(value).css("font-weight", "bold");
//            if (data.warn_if_negative && data[column.fieldname] < 0) {
//                $value.addClass("text-danger");
//            }

//            value = $value.wrap("<p></p>").parent().html();
//        }
//        return value
//    },
	
//	"treeView": true,
//	"name_field": "company",
//	"parent_field": "branch",
//	"initial_depth": 2
}
