// Copyright (c) 2021, Sione Taumoepeau and contributors
// For license information, please see license.txt
frappe.provide("fwc_edu.payin");

frappe.ui.form.on('PAYIN', {
	// refresh: function(frm) {

	// }
	setup: function(frm){
//		fwc_edu.setup_queries(frm);
	},
	on_submit: function(frm){
		cur_frm.refresh();
	},

	onload: function(frm) {
		fwc_edu.payin.setup_queries(frm);
	},


	total_entry_payment: function(frm){

		if (!frm.doc.total_entry_payment || frm.doc.total_entry_payment == ""){
			var total_entry_payment = 0;
		}
		if (!frm.doc.total_pos_amount || frm.doc.total_pos_amount == ""){
			var total_pos_amount = 0;
		}

		get_total(frm);
	},

	total_cash: function(frm){
		
		if (!frm.doc.total_cheques || frm.doc.total_cheques == ""){
			frm.doc.total_cheques = 0;
		}
		if (!frm.doc.total_cash || frm.doc.total_cash == ""){
			frm.doc.total_cash = 0;
		}

		get_grand_total(frm);
		
	},

	payment_total: function(frm){
		calculate_different(frm);
	},

	

	total_cheques: function(frm){

		if (!frm.doc.total_cheques || frm.doc.total_cheques == ""){
			frm.doc.total_cheques = 0;
		}
		if (!frm.doc.total_cash || frm.doc.total_cash == ""){
			frm.doc.total_cash = 0;
		}

		get_grand_total(frm);
	},

	get_transactions: function(frm) {
        get_summary(frm);
    },
	
});

var calculate_different = function(frm){
	frm.doc.different_amount = frm.doc.payment_total - frm.doc.grand_total
	refresh_field("different_amount")
	
};

var get_total = function(frm){
	frm.doc.total = frm.doc.total_pos_amount + frm.doc.total_entry_payment
	refresh_field("total")

};

var get_grand_total = function(frm){
	frm.doc.grand_total = frm.doc.total_cash + frm.doc.total_cheques
	calculate_different(frm)
	refresh_field("grand_total")
};

var get_summary = function(frm) {

    frappe.call({
        method: "fwc_edu.fwc_education.doctype.payin.payin.get_transaction_summary",
        args: {
            "posting_date": frm.doc.posting_date,
        },
        callback: function(r) {
            console.log(r.message)
            if (r.message) {
                $.each(r.message, function(i, item) {
                    var item_row = frm.add_child("payment_summary")
                    item_row.school = item.school,
                        item_row.amount = item.total
                });
                frm.refresh()
            }

        }

});

$.extend(fwc_edu.payin, {
	setup_queries: function(frm) {

	frm.fields_dict['payment_entry_table'].grid.get_field("receipt_document").get_query = function(doc, cdt, cdn) {
		return {
			filters: [
				['Payment Entry', 'docstatus', '=', 1],
				['Payment Entry', 'payment_type', '=', 'Receive'],
				['Payment Entry', 'payin', '=', 0]
			]
			}
		}
	}
});

frappe.ui.form.on("Payin Payment Entry", "receipt_document", function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	frappe.call({
		"method": "frappe.client.get",
		args: {
				doctype: "Payment Entry",
				name : d.receipt_document,
				filters : {
					docstatus:1
				}			
			},
				callback: function (data) {
				frappe.model.set_value(d.doctype, d.name, "posting_date",  data.message["posting_date"]);
				frappe.model.set_value(d.doctype, d.name, "cashier", data.message["owner"]);
				frappe.model.set_value(d.doctype, d.name, "payin", "1");
				frappe.model.set_value(d.doctype, d.name, "mode_of_payment", data.message["mode_of_payment"]);
				frappe.model.set_value(d.doctype, d.name, "total_payment", data.message["paid_amount"]);
			}
	})
});

frappe.ui.form.on("Denomination Table", {
	qty: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		
		frappe.model.set_value(d.doctype, d.name, "total", d.denomination * d.qty);
	
		var totalcash = 0;
		frm.doc.cash_details.forEach(function(d) { totalcash += d.total; });
	
		frm.set_value("total_cash", totalcash);
		cur_frm.refresh();
	},

	cash_details_remove: function(frm, cdt, cdn){
		var totalcash = 0;
		frm.doc.cash_details.forEach(function(d) { totalcash += d.total; });
	
		frm.set_value("total_cash", totalcash);
		cur_frm.refresh();
	}
  
});
  
frappe.ui.form.on("Cheques Details", {
	amount: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];

		var totalcheques = 0;
		frm.doc.cheques_details.forEach(function(d) { totalcheques += d.amount; });

		frm.set_value("total_cheques", totalcheques);
		cur_frm.refresh();
	},

	cheques_details_remove: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		var totalcheques = 0;
		frm.doc.cheques_details.forEach(function(d) { totalcheques += d.amount; });

		frm.set_value("total_cheques", totalcheques);
//		frm.set_value("grand_total")
		cur_frm.refresh();
	}
});

frappe.ui.form.on("Payin Payment Entry", {
	total_payment: function(frm, cdt, cdn){
	var d = locals[cdt][cdn];

	var totalpayment = 0;
	frm.doc.payment_entry_table.forEach(function(d) { totalpayment += d.total_payment; });

	frm.set_value("total_entry_payment", totalpayment);
	frm.set_value("payment_total", totalpayment);
	cur_frm.refresh();
	},
	
	payment_entry_table_remove: function(frm, cdt, cdn){
		var d = locals[cdt][cdn];
		var totalpayment = 0;
		frm.doc.payment_entry_table.forEach(function(d) { totalpayment += d.total_payment; });
		frm.set_value("total_entry_payment", totalpayment);
		frm.set_value("payment_total", totalpayment);
		cur_frm.refresh();
	}
});
