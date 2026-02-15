import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Parishioner Code", "fieldname": "parishioner_code", "fieldtype": "Data", "width": 120},
        {"label": "Full Name", "fieldname": "full_name", "fieldtype": "Data", "width": 200},
        {"label": "Church", "fieldname": "church", "fieldtype": "Link", "options": "Church", "width": 150},
        {"label": "SCC", "fieldname": "scc", "fieldtype": "Link", "options": "SCC", "width": 150},
    ]

def get_data(filters):
    conditions = ""
    params = {}
    if filters.get("church"):
        conditions = " AND church = %(church)s"
        params["church"] = filters.get("church")

    return frappe.db.sql(
        f"""
        SELECT
            parishioner_code,
            full_name,
            church,
            scc
        FROM `tabParishioner`
        WHERE name NOT IN (
            SELECT parent FROM `tabMovement Member` WHERE status = 'Active'
        ) {conditions}
        ORDER BY full_name ASC
        """,
        params,
        as_dict=True
    )
