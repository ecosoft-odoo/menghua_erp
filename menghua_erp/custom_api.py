import frappe
from frappe import _
from erpnext.stock.doctype.delivery_note import delivery_note


def create_and_submit_sales_invoice(doc, method):
    """ Delivery Note
        * If create_and_submit_sales_invoice = True, auto create / submit invoice
    """
    if doc.create_and_submit_sales_invoice:
        invoice = delivery_note.make_sales_invoice(doc.name)
        invoice.save()
        invoice.submit()


def validate_topup_amount(doc, method):
    """ Payment Entry
        * Validate amount Top Up must equal with Cash Holder Summary' Withdrawal
    """
    if doc.cash_holder_summary:
        chs = frappe.get_doc("Cash Holder Summary", doc.cash_holder_summary)
        if round(doc.paid_amount, 2) != round(chs.withdrawal, 2) or round(doc.received_amount, 2) != round(chs.withdrawal, 2):
            frappe.throw(
                _(
                    "Transfer amount is not valid with Cash Holder Summary - {} - {}"
                ).format(
                    doc.cash_holder_summary,
                    frappe.format_value(chs.withdrawal, "Float")
                )
            )

def vehicle_log_compute_total(doc, method):
	doc.total = (doc.vat or 0) + (doc.total_exclude_vat or 0)

def update_default_branch_for_bank_entry(doc, method):
    if doc.voucher_type != "Bank Entry":
        return
    company = frappe.defaults.get_user_default("Company")
    branch = frappe.get_value('Company', company, 'default_branch')
    if not branch:
        return
    for l in doc.accounts:
        if not l.branch:
            l.branch = "สำนักงานใหญ่"
