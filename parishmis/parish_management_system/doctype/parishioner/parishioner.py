# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document

class Parishioner(Document):
    def validate(self):
        # Auto-generate full name
        self.full_name = " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))

        # Ensure at least one belonging field is selected
        if not (self.scc or self.church or (self.association and self.association != "None")):
            frappe.throw("A Parishioner must belong to either an SCC, a Church/Outstation, or an Association.")

        # Auto-clear "Other Association" if not applicable
        if self.association != "Other":
            self.association_other = ""
