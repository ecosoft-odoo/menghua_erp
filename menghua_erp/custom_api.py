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
        if doc.paid_amount != chs.withdrawal or doc.received_amount != chs.withdrawal:
            frappe.throw(
                _(
                    "Transfer amount is not valid with Cash Holder Summary - {} - {}"
                ).format(
                    doc.cash_holder_summary,
                    frappe.format_value(chs.withdrawal, "Float")
                )
            )

def vehicle_log_compute_total(doc, method):
	doc.total = doc.vat + doc.total_exclude_vat

