# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def make_expense_claim(docname):
	expense_claim = frappe.db.exists("Expense Claim", {"vehicle_log": docname})
	if expense_claim:
		frappe.throw(_("Expense Claim {0} already exists for the Vehicle Log").format(expense_claim))

	vehicle_log = frappe.get_doc("Vehicle Log", docname)
	service_expense = sum([flt(d.expense_amount) for d in vehicle_log.service_detail])

	if not (vehicle_log.total_exclude_vat + service_expense):
		frappe.throw(_("No additional expenses has been added"))

	exp_claim = frappe.new_doc("Expense Claim")
	exp_claim.employee = vehicle_log.employee
	exp_claim.employee_name = frappe.get_value('Employee', vehicle_log.employee, 'employee_name')
	exp_claim.title = exp_claim.employee_name
	exp_claim.payable_account = frappe.get_value(
		'Company', frappe.defaults.get_user_default("Company"), 'default_expense_claim_payable_account'
	)
	exp_claim.tax_invoice_number = vehicle_log.invoice
	exp_claim.tax_invoice_date = vehicle_log.date
	exp_claim.supplier = vehicle_log.supplier
	exp_claim.vehicle_log = vehicle_log.name
	exp_claim.remark = _("Expense Claim for Vehicle Log {0}").format(vehicle_log.name)
	if vehicle_log.total_exclude_vat:
		exp_claim.append(
			"expenses", {
				"expense_type": vehicle_log.fuel_claim_type,
				"expense_date": vehicle_log.date,
				"description": vehicle_log.license_plate,
				"quantity": vehicle_log.fuel_qty,
				"price": vehicle_log.price,
				"amount": vehicle_log.total_exclude_vat,
			},
		)
		exp_claim.append(
			"taxes", {
				"tax_amount": vehicle_log.vat,
				"total": vehicle_log.total,
			}
		)
	if service_expense:
		exp_claim.append(
			"expenses", {
				"expense_type": vehicle_log.service_claim_type,
				"expense_date": vehicle_log.date,
				"description": vehicle_log.license_plate,
				"quantity": 1,
				"price": service_expense,
				"amount": service_expense,
				"sanctioned_amount": service_expense,
			},
		)
	return exp_claim.as_dict()
