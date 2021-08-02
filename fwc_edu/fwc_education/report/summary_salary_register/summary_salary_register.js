// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Summary Salary Register"] = {
    "filters": [{
            "fieldname": "from_date",
            "label": __("From"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1,
            "width": "100px"
        },
        {
            "fieldname": "to_date",
            "label": __("To"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "100px"
        },
        {
            "fieldname": "docstatus",
            "label": __("Document Status"),
            "fieldtype": "Select",
            "options": ["Draft", "Submitted", "Cancelled"],
            "default": "Submitted",
            "width": "100px"
        },
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "width": "100px",
            "reqd": 1
        },

    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.id == "branch" && data && data["branch"] == "TOTAL") {
            value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
        }
        return value;
    }
};