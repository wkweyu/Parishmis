import frappe


def execute(filters=None):
    filters = filters or {}
    church = filters.get("church")
    if not church:
        return [], []

    scc_count = frappe.db.count("SCC", filters={"church": church})

    stats = frappe.db.sql(
        """
        SELECT
            COUNT(name) AS total_members,
            SUM(CASE WHEN gender = 'Male' THEN 1 ELSE 0 END) AS total_male,
            SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) AS total_female
        FROM `tabParishioner`
        WHERE church = %(church)s
        """,
        {"church": church},
        as_dict=True,
    )
    stats = stats[0] if stats else {}

    columns = [
        {"label": "Metric", "fieldname": "metric", "fieldtype": "Data", "width": 200},
        {"label": "Value", "fieldname": "value", "fieldtype": "Int", "width": 120},
    ]

    data = [
        {"metric": "Total SCCs", "value": scc_count},
        {"metric": "Total Members", "value": stats.get("total_members") or 0},
        {"metric": "Male", "value": stats.get("total_male") or 0},
        {"metric": "Female", "value": stats.get("total_female") or 0},
    ]

    return columns, data
