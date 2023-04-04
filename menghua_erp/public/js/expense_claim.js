frappe.ui.form.on('Expense Claim', {

    refresh: function(frm) {
        frm.doc.expenses.forEach(function(d) {
            d.sanctioned_amount = d.amount
		})
        frm.refresh_field("expenses")
    }

})
