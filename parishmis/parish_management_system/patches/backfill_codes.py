import frappe
from frappe.model.naming import make_autoname


def execute():
    targets = [
        ("Diocese", "code", "DIO-.#####"),
        ("Parish", "parish_code", "PAR-.#####"),
        ("Church", "code", "CH-.#####"),
        ("Parishioner", "parishioner_code", "PRN-.#####"),
        ("Association", "code", "ASC-.#####"),
    ]

    for doctype, fieldname, pattern in targets:
        if not frappe.db.has_column(doctype, fieldname):
            continue
        records = frappe.get_all(doctype, fields=["name", fieldname])
        for row in records:
            if row.get(fieldname):
                continue
            new_code = make_autoname(pattern)
            frappe.db.set_value(doctype, row.name, fieldname, new_code)
