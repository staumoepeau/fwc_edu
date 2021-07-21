// Copyright (c) 2016, Sione Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["FWC FORM 7 PAYE"] = {
    "filters": [{
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company"),
            width: "90px",
            reqd: 1
        },
        {
            fieldname: "month",
            label: __("Month"),
            fieldtype: "Select",
            width: "90px",
            reqd: 1,
            options: [
                { "value": 1, "label": __("Jan") },
                { "value": 2, "label": __("Feb") },
                { "value": 3, "label": __("Mar") },
                { "value": 4, "label": __("Apr") },
                { "value": 5, "label": __("May") },
                { "value": 6, "label": __("June") },
                { "value": 7, "label": __("July") },
                { "value": 8, "label": __("Aug") },
                { "value": 9, "label": __("Sep") },
                { "value": 10, "label": __("Oct") },
                { "value": 11, "label": __("Nov") },
                { "value": 12, "label": __("Dec") },
            ],
            default: frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1
        },
        {
            fieldname: "year",
            label: __("Year"),
            fieldtype: "Select",
            width: "80px",
            reqd: 1
        },
        //		{
        //			fieldname: "department",
        //			label: __("Department"),
        //			fieldtype: "Link",
        //			options: "Department",
        //			width: "250px",
        //			reqd: 1 
        //		},
    ],

    onload: function(report) {

        report.page.set_primary_action('PAYE', function() {
            var args = "as a draft"
            var reporter = frappe.query_reports["FWC FORM 7 PAYE"];
            reporter.maketextfile(report);
        })

        return frappe.call({
            method: "erpnext.regional.report.provident_fund_deductions.provident_fund_deductions.get_years",
            callback: function(r) {
                var year_filter = frappe.query_report.get_filter('year');
                year_filter.df.options = r.message;
                year_filter.df.default = r.message.split("\n")[0];
                year_filter.refresh();
                year_filter.set_input(year_filter.df.default);
            }
        });
    },
    isNumeric: function(obj) {
        return !jQuery.isArray(obj) && (obj - parseFloat(obj) + 1) >= 0;
    },
    maketextfile: function(report) {
        var filters = report.get_values();
        if (filters.department) {
            return frappe.call({
                method: "fwc_edu.fwc_education.report.fwc_form_7_paye.fwc_form_7_paye.save_data_to_Excel",
                args: {
                    "month": filters.month,
                    "department": filters.department,
                    "year": filters.year
                },
                callback: function(r) {
                    console.log(r)
                }
            })
        } else {
            frappe.msgprint("Please select all filters for creating Text File")
        }
    },
}