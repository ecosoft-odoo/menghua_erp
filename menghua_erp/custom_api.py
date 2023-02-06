from erpnext.stock.doctype.delivery_note import delivery_note


def create_and_submit_sales_invoice(doc, method):
    if doc.create_and_submit_sales_invoice:
        invoice = delivery_note.make_sales_invoice(doc.name)
        invoice.save()
        invoice.submit()
