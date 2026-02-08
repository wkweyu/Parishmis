import frappe
from frappe.model.naming import make_autoname


def execute():
    backfill_scc_codes()
    backfill_family_codes()


def backfill_scc_codes():
    if not frappe.db.has_column("SCC", "code"):
        return
    rows = frappe.get_all("SCC", fields=["name", "code"], filters={"code": ["is", "not set"]})
    for row in rows:
        new_code = make_autoname("SCC-.#####")
        frappe.db.set_value("SCC", row.name, "code", new_code)


def backfill_family_codes():
    if not frappe.db.has_column("Family", "family_code"):
        return
    rows = frappe.get_all("Family", fields=["name", "family_code"], filters={"family_code": ["is", "not set"]})
    for row in rows:
        new_code = make_autoname("FAM-.#####")
        frappe.db.set_value("Family", row.name, "family_code", new_code)
