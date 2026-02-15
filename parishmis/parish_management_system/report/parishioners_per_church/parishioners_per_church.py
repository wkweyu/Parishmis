import frappe


def execute(filters=None):
    data = frappe.db.sql(
        """
        SELECT
            p.church AS church,
            COUNT(p.name) AS total_members
        FROM `tabParishioner` p
        GROUP BY p.church
        ORDER BY p.church
        """,
        as_dict=True,
    )

    columns = [
        {"label": "Church", "fieldname": "church", "fieldtype": "Link", "options": "Church", "width": 200},
        {"label": "Total Members", "fieldname": "total_members", "fieldtype": "Int", "width": 140},
    ]
    return columns, data
