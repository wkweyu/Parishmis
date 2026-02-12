# Copyright (c) 2025, Concoct Systems and contributors
# For license information, please see license.txt

# import frappe
import re
import secrets
import string

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint
from parishmis.api.portal_setup import ensure_portal_user

PASSWORD_MIN_LENGTH = 10
PASSWORD_REQUIREMENTS = (
    "Password must be at least 10 characters and include uppercase, lowercase, "
    "a number, and a symbol."
)


def _is_valid_password(password: str) -> bool:
    if len(password) < PASSWORD_MIN_LENGTH:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[^A-Za-z0-9]", password):
        return False
    return True


def _generate_password() -> str:
    symbols = "!@#$%^&*()-_=+[]{}:,.?"
    required = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice(symbols),
    ]
    alphabet = string.ascii_letters + string.digits + symbols
    remaining = PASSWORD_MIN_LENGTH - len(required)
    password_chars = required + [secrets.choice(alphabet) for _ in range(max(0, remaining))]
    secrets.SystemRandom().shuffle(password_chars)
    password = "".join(password_chars)
    if not _is_valid_password(password):
        return _generate_password()
    return password

class Parishioner(Document):
    def validate(self):
        self._format_names()
        
        prev = frappe._dict()
        if self.name:
            prev = frappe.db.get_value("Parishioner", self.name, ["church", "parish"], as_dict=True) or frappe._dict()

        # Auto-generate code
        if not self.parishioner_code:
            self.parishioner_code = make_autoname("PRN-.#####")

        # Require church and set parish from church
        if not self.church:
            frappe.throw("Church / Outstation is required for a Parishioner.")
        
        church_parish = frappe.db.get_value("Church", self.church, "parish")
        if not church_parish:
            frappe.throw("Selected church is missing a linked Parish; fix the church record first.")
        self.parish = church_parish

        # Validate uniqueness of phone/email
        self._validate_unique_contact()

        # Optional: ensure SCC belongs to same parish
        if self.scc:
            scc_parish = frappe.db.get_value("SCC", self.scc, "parish")
            if scc_parish and scc_parish != self.parish:
                frappe.throw("Selected SCC belongs to a different Parish than the Parishioner.")

        # Optional: ensure Family belongs to same church/parish
        self._validate_family_link()

        # Log transfer when church changes
        self._log_transfer_if_changed(prev.get("church"), prev.get("parish"))

    def _format_names(self):
        """Format names to Title Case and update full_name"""
        for field in ["first_name", "middle_name", "last_name"]:
            if self.get(field):
                self.set(field, self.get(field).strip().title())
        
        self.full_name = " ".join(filter(None, [self.first_name, self.middle_name, self.last_name]))

    def _validate_family_link(self):
        if not self.family:
            return
        fam_church, fam_parish = frappe.db.get_value("Family", self.family, ["church", "parish"])
        if fam_church and fam_church != self.church:
            frappe.throw("Selected Family belongs to a different Church than the Parishioner.")
        if fam_parish and fam_parish != self.parish:
            frappe.throw("Selected Family belongs to a different Parish than the Parishioner.")

    def _validate_unique_contact(self):
        if self.phone_number:
            dup = frappe.db.exists("Parishioner", {"phone_number": self.phone_number, "name": ("!=", self.name)})
            if dup:
                frappe.throw("Phone Number must be unique across Parishioners.")
        if self.email:
            dup = frappe.db.exists("Parishioner", {"email": self.email, "name": ("!=", self.name)})
            if dup:
                frappe.throw("Email must be unique across Parishioners.")

    def _log_transfer_if_changed(self, old_church, old_parish):
        if not old_church or old_church == self.church:
            return
        # Append a transfer record capturing old/new parish/church
        self.append(
            "transfer_history",
            {
                "from_parish": old_parish,
                "from_church": old_church,
                "to_parish": self.parish,
                "to_church": self.church,
                "transfer_date": frappe.utils.today(),
                "remarks": "Auto-logged on church change",
            },
        )


@frappe.whitelist()
def create_portal_user(parishioner: str, user_email: str | None = None, send_welcome_email: int = 1):
    if not parishioner:
        frappe.throw("Parishioner is required.")

    if not frappe.has_permission("Parishioner", "write", parishioner):
        frappe.throw("Not permitted to create portal users for this Parishioner.")

    parishioner_doc = frappe.get_doc("Parishioner", parishioner)
    email = user_email or parishioner_doc.email
    if not email:
        frappe.throw("An email address is required to create a portal user.")

    result = ensure_portal_user(parishioner_doc.name, email)
    if cint(send_welcome_email):
        result["welcome_email"] = send_portal_welcome_email(parishioner_doc.name)
    return result


@frappe.whitelist()
def send_portal_welcome_email(parishioner: str, temp_password: str | None = None):
    if not parishioner:
        frappe.throw("Parishioner is required.")

    if not frappe.has_permission("Parishioner", "read", parishioner):
        frappe.throw("Not permitted to email this Parishioner.")

    parishioner_doc = frappe.get_doc("Parishioner", parishioner)
    if not parishioner_doc.user_account:
        frappe.throw("This Parishioner has no linked portal user.")

    user_doc = frappe.get_doc("User", parishioner_doc.user_account)
    recipient = user_doc.email or parishioner_doc.email
    if not recipient:
        frappe.throw("No email is linked to this Parishioner.")

    password = temp_password or _generate_password()
    if not _is_valid_password(password):
        frappe.throw(PASSWORD_REQUIREMENTS)
    frappe.utils.password.update_password(user_doc.name, password)

    portal_url = frappe.utils.get_url("/portal")
    login_url = frappe.utils.get_url("/login")
    subject = "Welcome to ParishMIS Portal"
    message = (
        f"Hello {parishioner_doc.full_name or 'Parishioner'},<br><br>"
        "Your ParishMIS portal account is ready.<br>"
        f"Username: <b>{recipient}</b><br>"
        f"Temporary password: <b>{password}</b><br>"
        f"Portal: <a href=\"{portal_url}\">{portal_url}</a><br>"
        "Please change your password after logging in.<br>"
        f"Login: <a href=\"{login_url}\">{login_url}</a><br><br>"
        "If you need help, please contact the parish office."
    )

    frappe.sendmail(recipients=[recipient], subject=subject, message=message)
    return {"recipient": recipient}
