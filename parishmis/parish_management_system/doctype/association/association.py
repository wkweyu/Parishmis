from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Association(Document):
	def validate(self):
		self._ensure_code()

	def _ensure_code(self):
		if not getattr(self, "code", None):
			self.code = make_autoname("ASC-.#####")
