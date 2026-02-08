# -*- coding: utf-8 -*-
import frappe
from frappe.model.document import Document
from frappe.utils import get_url

class MPesaSettings(Document):
    def onload(self):
        self.callback_url = get_url("/api/method/parishmis.integrations.mpesa.callback")
