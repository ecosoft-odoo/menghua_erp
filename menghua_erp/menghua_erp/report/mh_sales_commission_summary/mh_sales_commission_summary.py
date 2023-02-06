# Copyright (c) 2023, Kitti U. and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	entries = get_entries(filters)
	data = []

	for d in entries:
		data.append(
			[
				d.sales_person,
				d.name,
				d.customer,
				d.territory,
				d.posting_date,
				d.due_date,
				d.base_net_amount,
				# d.allocated_percentage,
				# d.commission_rate,
				# d.allocated_amount,
				d.incentives,
				d.status,
				d.payment,
				d.clearance_date
			]
		)

	if data:
		total_row = [""] * len(data[0])
		data.append(total_row)

	return columns, data


def get_columns(filters):

	columns = [
		{
			"label": _("Sales Person"),
			"options": "Sales Person",
			"fieldname": "sales_person",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Sales Invoice"),
			"options": "Sales Invoice",
			"fieldname": "sales_invoice",
			"fieldtype": "Link",
			"width": 150,
		},
		{
			"label": _("Customer"),
			"options": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"width": 140,
		},
		{
			"label": _("Territory"),
			"options": "Territory",
			"fieldname": "territory",
			"fieldtype": "Link",
			"width": 100,
		},
		{
			"label": _("Posting Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Due Date"),
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120,
		},
		# {
		# 	"label": _("Contribution %"),
		# 	"fieldname": "contribution_percentage",
		# 	"fieldtype": "Data",
		# 	"width": 110,
		# },
		# {
		# 	"label": _("Commission Rate %"),
		# 	"fieldname": "commission_rate",
		# 	"fieldtype": "Data",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("Contribution Amount"),
		# 	"fieldname": "contribution_amount",
		# 	"fieldtype": "Currency",
		# 	"width": 120,
		# },
		{
			"label": _("Incentives"),
			"fieldname": "incentives",
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 90,
		},
		{
			"label": _("Payment Entry"),
			"options": "Payment Entry",
			"fieldname": "payment_entry",
			"fieldtype": "Link",
			"width": 150,
		},
		{
			"label": _("Clearance Date"),
			"fieldname": "clearance_date",
			"fieldtype": "Date",
			"width": 100,
		},
	]

	return columns


def get_entries(filters):
	conditions, values = get_conditions(filters)
	entries = frappe.db.sql(
		"""
		select * from
		(
		select
			dt.name, dt.customer_name as customer, dt.territory,
			dt.posting_date, dt.base_net_total as base_net_amount,
			st.commission_rate, st.sales_person, st.allocated_percentage,
			st.allocated_amount, st.incentives, dt.due_date, dt.status,
			dt.outstanding_amount
		from
			`tabSales Invoice` dt join `tabSales Team` st on dt.name = st.parent
		where
			st.parenttype = 'Sales Invoice'
			and dt.docstatus = 1 %s order by dt.name desc, st.sales_person
		) i
		left outer join
		(
		select 
			ref.reference_name as ref_invoice, pay.name as payment, max(clearance_date) clearance_date
		from `tabPayment Entry Reference` ref
			join `tabPayment Entry` pay on ref.parent = pay.name
		where ref.reference_doctype = 'Sales Invoice'
		group by ref.reference_name, pay.name
		) p
		on p.ref_invoice = i.name
		"""
		% (conditions),
		tuple(values),
		as_dict=1,
	)

	return entries

		# select
		# 	dt.name, dt.customer, dt.territory,
		# 	dt.posting_date, dt.base_net_total as base_net_amount,
		# 	st.commission_rate, st.sales_person, st.allocated_percentage,
		# 	st.allocated_amount, st.incentives
		# from
		# 	`tabSales Invoice` dt, `tabSales Team` st
		# where
		# 	st.parent = dt.name and st.parenttype = 'Sales Invoice'
		# 	and dt.docstatus = 1 %s order by dt.name desc, st.sales_person


def get_conditions(filters):
	conditions = [""]
	values = []

	for field in ["company", "customer", "territory"]:
		if filters.get(field):
			conditions.append("dt.{0}=%s".format(field))
			values.append(filters[field])

	if filters.get("sales_person"):
		conditions.append("st.sales_person = '{0}'".format(filters.get("sales_person")))

	if filters.get("from_date"):
		conditions.append("dt.posting_date>=%s")
		values.append(filters["from_date"])

	if filters.get("to_date"):
		conditions.append("dt.posting_date<=%s")
		values.append(filters["to_date"])

	return " and ".join(conditions), values
