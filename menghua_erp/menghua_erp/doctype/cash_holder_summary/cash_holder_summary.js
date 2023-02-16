// Copyright (c) 2023, Kitti U. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cash Holder Summary', {

	refresh(frm) {
	    frm.set_query("cash_account", function() {
            return {
				filters: {
				    account_type: "Cash"
				}
            }
        })

		// Button to Top Up - Create Payment Entry
		if(frm.doc.docstatus==1) {
			frm.add_custom_button(__("Top Up"), function () {
				frappe.route_options = {
					"payment_type": "Internal Transfer",
					"paid_to": frm.doc.cash_account,
					"cash_holder_summary": frm.doc.name
				};
				frappe.set_route("payment-entry", "new-payment-entry");
			});
		}
	},

	date_from: function(frm) {
		get_cash_holder_entries(frm)
	},
	date_to: function(frm) {
		get_cash_holder_entries(frm)
	},
	cash_account: function(frm) {
		get_cash_holder_entries(frm)
	},

});

function get_cash_holder_entries(frm) {
	frappe.db.get_list('GL Entry', {
		fields: [
			'voucher_type',
			'voucher_no',
			'debit',
			'credit',
			'posting_date',
			'remarks',
		],
		filters: {
			account: frm.doc.cash_account,
			posting_date: ['between', [frm.doc.date_from, frm.doc.date_to]],
			is_cancelled: 0,
		},
		limit: 0,
		order_by: "posting_date"
	}).then(records => {
		frm.set_value("entries", records)
	})
}