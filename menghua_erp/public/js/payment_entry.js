frappe.ui.form.on('Payment Entry', {
    cash_holder_summary: function(frm) {
        frappe.db.get_doc('Cash Holder Summary', frm.doc.cash_holder_summary)
            .then(doc => {
                frm.set_value({
                    paid_amount: doc.withdrawal,
                    received_amount: doc.withdrawal
                })
            })
    }
})