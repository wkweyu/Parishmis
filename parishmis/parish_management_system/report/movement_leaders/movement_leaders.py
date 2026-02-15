import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Movement", "fieldname": "movement", "fieldtype": "Link", "options": "Movement", "width": 180},
        {"label": "Role", "fieldname": "role", "fieldtype": "Data", "width": 120},
        {"label": "Parishioner", "fieldname": "parishioner_name", "fieldtype": "Link", "options": "Parishioner", "width": 200},
        {"label": "Phone", "fieldname": "phone", "fieldtype": "Data", "width": 120},
    ]

def get_data(filters):
    conditions = " AND mm.role IN ('Chair', 'Secretary', 'Treasurer')"
    params = {}
    if filters.get("movement"):
        conditions += " AND mm.movement = %(movement)s"
        params["movement"] = filters.get("movement")

    return frappe.db.sql(
        f"""
        SELECT
            mm.movement,
            mm.role,
            p.full_name as parishioner_name,
            p.phone_number as phone
        FROM `tabMovement Member` mm
        INNER JOIN `tabParishioner` p ON p.name = mm.parent
        WHERE mm.status = 'Active' {conditions}
        ORDER BY mm.movement, mm.role
        """,
        params,
        as_dict=True
    )
