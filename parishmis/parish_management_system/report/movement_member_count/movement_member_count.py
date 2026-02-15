import frappe

def execute(filters=None):
    filters = filters or {}
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Movement", "fieldname": "movement", "fieldtype": "Link", "options": "Movement", "width": 200},
        {"label": "Total Members", "fieldname": "total_members", "fieldtype": "Int", "width": 120},
        {"label": "Male", "fieldname": "male", "fieldtype": "Int", "width": 100},
        {"label": "Female", "fieldname": "female", "fieldtype": "Int", "width": 100},
    ]

def get_data(filters):
    conditions = ""
    params = {}
    if filters.get("parish"):
        conditions = " AND m.parish = %(parish)s"
        params["parish"] = filters.get("parish")

    return frappe.db.sql(
        f"""
        SELECT
            mm.movement,
            COUNT(p.name) as total_members,
            SUM(CASE WHEN p.gender = 'Male' THEN 1 ELSE 0 END) as male,
            SUM(CASE WHEN p.gender = 'Female' THEN 1 ELSE 0 END) as female
        FROM `tabMovement Member` mm
        INNER JOIN `tabParishioner` p ON p.name = mm.parent
        INNER JOIN `tabMovement` m ON m.name = mm.movement
        WHERE mm.status = 'Active' {conditions}
        GROUP BY mm.movement
        ORDER BY total_members DESC
        """,
        params,
        as_dict=True
    )
