import frappe
from frappe import _

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": _("Record"), "fieldname": "name", "fieldtype": "Link", "options": "Sacrament Record", "width": 140},
        {"label": _("Parishioner"), "fieldname": "parishioner", "fieldtype": "Link", "options": "Parishioner", "width": 160},
        {"label": _("Sacrament"), "fieldname": "sacrament_type", "fieldtype": "Link", "options": "Sacrament Type", "width": 140},
        {"label": _("Date"), "fieldname": "sacrament_date", "fieldtype": "Date", "width": 110},
        {"label": _("Church"), "fieldname": "church", "fieldtype": "Link", "options": "Church", "width": 140},
        {"label": _("Parish"), "fieldname": "parish", "fieldtype": "Link", "options": "Parish", "width": 140},
        {"label": _("Priest"), "fieldname": "priest", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": _("Certificate No."), "fieldname": "certificate_no", "fieldtype": "Data", "width": 140},
        {"label": _("Register Book"), "fieldname": "register_book", "fieldtype": "Data", "width": 120},
        {"label": _("Page"), "fieldname": "page_number", "fieldtype": "Data", "width": 80},
        {"label": _("Entry"), "fieldname": "entry_number", "fieldtype": "Data", "width": 80},
        {"label": _("Owner"), "fieldname": "owner", "fieldtype": "Link", "options": "User", "width": 140}
    ]

    conditions = ["docstatus = 1"]
    params = {}

    if filters.get("sacrament_type"):
        conditions.append("sacrament_type = %(sacrament_type)s")
        params["sacrament_type"] = filters["sacrament_type"]
    if filters.get("church"):
        conditions.append("church = %(church)s")
        params["church"] = filters["church"]
    if filters.get("parish"):
        conditions.append("parish = %(parish)s")
        params["parish"] = filters["parish"]
    if filters.get("from_date"):
        conditions.append("sacrament_date >= %(from_date)s")
        params["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("sacrament_date <= %(to_date)s")
        params["to_date"] = filters["to_date"]

    query = f"""
        SELECT
            name,
            parishioner,
            sacrament_type,
            sacrament_date,
            church,
            parish,
            priest,
            certificate_no,
            register_book,
            page_number,
            entry_number,
            owner
        FROM `tabSacrament Record`
        WHERE {' AND '.join(conditions)}
        ORDER BY sacrament_date DESC
    """

    data = frappe.db.sql(query, params, as_dict=True)
    return columns, data
