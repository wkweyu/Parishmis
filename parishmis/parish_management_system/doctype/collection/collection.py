import frappe
from frappe.model.document import Document
from frappe import _

class Collection(Document):
    def validate(self):
        self._set_parish_from_church()

    def _set_parish_from_church(self):
        if self.church:
            parish = frappe.db.get_value("Church", self.church, "parish")
            if parish:
                self.parish = parish

    def on_submit(self):
        self._create_ledger_entry()
        self._update_batch_total()
        self._update_candidate_paid_amount()

    def on_cancel(self):
        if self.journal_entry:
            je = frappe.get_doc("Journal Entry", self.journal_entry)
            je.cancel()
            self.journal_entry = None
            self.save()
        self._update_batch_total()
        self._update_candidate_paid_amount()

    def _update_candidate_paid_amount(self):
        if self.sacrament_candidate:
            candidate = frappe.get_doc("Sacrament Candidate", self.sacrament_candidate)
            candidate.update_paid_amount()
            candidate.save()

    def _update_batch_total(self):
        if self.batch:
            frappe.get_doc("Collection Batch", self.batch).calculate_total()

    def _create_ledger_entry(self):
        settings = frappe.get_single("Payment Settings")
        coll_type = frappe.get_doc("Collection Type", self.collection_type)
        
        if not coll_type.income_account:
            frappe.throw(_("Please set Income Account for Collection Type: {0}").format(self.collection_type))
            
        debit_account = ""
        if self.payment_method == "Cash":
            debit_account = settings.default_cash_account
        elif self.payment_method == "M-Pesa":
            debit_account = settings.default_mpesa_account
        else: # Bank Transfer or Cheque
            debit_account = settings.default_bank_account
            
        if not debit_account:
            frappe.throw(_("Please set default accounts in Payment Settings for {0}").format(self.payment_method))

        company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.get_all("Company", limit=1)[0].name
        
        je = frappe.new_doc("Journal Entry")
        je.voucher_type = "Journal Entry"
        je.posting_date = self.date
        je.company = company
        je.remark = _("Collection from {0} for {1}").format(self.parishioner or "Loose Cash", self.collection_type)
        
        je.append("accounts", {
            "account": debit_account,
            "debit_in_account_currency": self.amount,
            "reference_type": "Collection",
            "reference_name": self.name
        })
        
        je.append("accounts", {
            "account": coll_type.income_account,
            "credit_in_account_currency": self.amount,
            "reference_type": "Collection",
            "reference_name": self.name
        })
        
        je.insert()
        je.submit()
        
        self.journal_entry = je.name
        self.save()

