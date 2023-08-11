import frappe
from frappe.utils import flt, cint
from erpnext.loan_management.doctype.loan_repayment.loan_repayment import get_pending_principal_amount


# Proposed PR: https://github.com/frappe/erpnext/pull/36589
def regenerate_repayment_schedule(loan, cancel=0):
	from erpnext.loan_management.doctype.loan.loan import (
		add_single_month,
		get_monthly_repayment_amount,
	)

	precision = cint(frappe.db.get_default("currency_precision")) or 2   # OVERWRITE
	loan_doc = frappe.get_doc("Loan", loan)
	next_accrual_date = None
	accrued_entries = 0
	last_repayment_amount = None
	last_balance_amount = None

	for term in reversed(loan_doc.get("repayment_schedule")):
		if not term.is_accrued:
			next_accrual_date = term.payment_date
			loan_doc.remove(term)
		else:
			accrued_entries += 1
			if last_repayment_amount is None:
				last_repayment_amount = term.total_payment
			if last_balance_amount is None:
				last_balance_amount = term.balance_loan_amount

	loan_doc.save()

	balance_amount = get_pending_principal_amount(loan_doc)

	if loan_doc.repayment_method == "Repay Fixed Amount per Period":
		monthly_repayment_amount = flt(
			balance_amount / len(loan_doc.get("repayment_schedule")) - accrued_entries
		)
	else:
		repayment_period = loan_doc.repayment_periods - accrued_entries
		if not cancel and repayment_period > 0:
			monthly_repayment_amount = get_monthly_repayment_amount(
				balance_amount, loan_doc.rate_of_interest, repayment_period
			)
		else:
			monthly_repayment_amount = last_repayment_amount
			balance_amount = last_balance_amount

	payment_date = next_accrual_date

	while flt(balance_amount, precision) > 0:   # OVERWRITE
		interest_amount = flt(balance_amount * flt(loan_doc.rate_of_interest) / (12 * 100))
		principal_amount = monthly_repayment_amount - interest_amount
		balance_amount = flt(balance_amount + interest_amount - monthly_repayment_amount)
		if balance_amount < 0:
			principal_amount += balance_amount
			balance_amount = 0.0

		total_payment = principal_amount + interest_amount
		loan_doc.append(
			"repayment_schedule",
			{
				"payment_date": payment_date,
				"principal_amount": principal_amount,
				"interest_amount": interest_amount,
				"total_payment": total_payment,
				"balance_loan_amount": balance_amount,
			},
		)
		next_payment_date = add_single_month(payment_date)
		payment_date = next_payment_date

	loan_doc.save()
