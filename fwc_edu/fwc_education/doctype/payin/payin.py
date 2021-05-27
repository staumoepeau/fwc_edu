# Copyright (c) 2021, Sione Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import cstr, flt, fmt_money, formatdate
from frappe import msgprint, _, scrub
from frappe.model.document import Document

class PAYIN(Document):
	
	def validate(self):
		if not self.total_cash:
			self.total_cash == 0
		
#		if not self.total_pos_amount:
#			self.total_pos_amount = 0
		
		if not self.total_entry_payment:
			self.total_entry_payment == 0

#		if not self.total_cheques:
#			self.total_cheques = 0
#			self.grand_total = self.total_cash + self.total_cheques
		
#		self.check_balance()

	def on_submit(self):
#		self.validate_grand_total()
		self.make_payin_entries()
#		self.update_pos()
		self.update_payment_entry()
#		self.update_status()
	
	def on_cancel(self):
#		self.cancel_pos()
		self.cancel_payment_entry()
#		self.update_status()

	def updates_list(self):
		self.get_mode_of_payment()

	def make_payin_entries(self):
		frappe.db.sql("""Update `tabPayment Entry` set status="PayIn" where name=%s""", (self.name))

	def update_payment_entry(self):
		for d in self.get("payment_entry_table"):
			frappe.db.sql("""Update `tabPayment Entry` set payin=1 where name=%s""", (d.receipt_document))


@frappe.whitelist()
def get_transaction_summary():
	return frappe.db.sql("""SELECT SUM(total_payment) AS amount, school
		FROM `tabPayin Payment Entry`
		WHERE payin_process = 1
		AND payin = 0
		GROUP BY school""", as_dict = 1)