# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class CashHolderSummary(Document):

    def submit(self):
        if (self.opening + self.deposit - self.withdrawal) != self.closing:
            frappe.throw(_("Invalid entries or closing amount."))
        super(CashHolderSummary, self).submit()

    @property
    def opening(self):
        gle = frappe.db.sql(
            """
                select sum(debit) - sum(credit) from `tabGL Entry`
                where posting_date < %(date_from)s and account = %(account)s and is_cancelled = 0
            """,
            values={"date_from": self.date_from, "account": self.cash_account},
            as_dict=0,
        )
        return gle[0][0] or 0

    @property
    def closing(self):
        gle = frappe.db.sql(
            """
            select sum(debit) - sum(credit) from `tabGL Entry`
            where posting_date <= %(date_to)s and account = %(account)s and is_cancelled = 0
            """,
            values={"date_to": self.date_to, "account": self.cash_account},
            as_dict=0,
        )
        return gle[0][0] or 0

    @property
    def deposit(self):
        return sum([r.debit for r in self.entries])

    @property
    def withdrawal(self):
        return sum([r.credit for r in self.entries])
