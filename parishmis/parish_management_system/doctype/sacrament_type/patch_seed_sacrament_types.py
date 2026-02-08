import frappe


def execute():
    seed = [
        {"sacrament_type": "Baptism", "description": "Baptism", "repeatable": 0, "min_age_years": 0, "require_priest": 1, "requires_training": 1},
        {"sacrament_type": "Eucharist", "description": "Eucharist", "repeatable": 1, "min_age_years": 7, "require_priest": 1, "requires_training": 1},
        {"sacrament_type": "Confirmation", "description": "Confirmation", "repeatable": 0, "min_age_years": 12, "require_priest": 1, "requires_training": 1},
        {"sacrament_type": "Reconciliation", "description": "Reconciliation", "repeatable": 1, "min_age_years": 7, "require_priest": 1, "requires_training": 1},
        {"sacrament_type": "Anointing of the Sick", "description": "Anointing of the Sick", "repeatable": 1, "min_age_years": 0, "require_priest": 1, "requires_training": 0},
        {"sacrament_type": "Marriage", "description": "Marriage", "repeatable": 0, "min_age_years": 18, "require_priest": 1, "requires_training": 1},
        {"sacrament_type": "Holy Orders", "description": "Holy Orders", "repeatable": 0, "min_age_years": 21, "require_priest": 1, "requires_training": 1},
    ]

    for row in seed:
        if not frappe.db.exists("Sacrament Type", {"sacrament_type": row["sacrament_type"]}):
            doc = frappe.new_doc("Sacrament Type")
            for k, v in row.items():
                doc.set(k, v)
            doc.insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Sacrament Type", row["sacrament_type"], row)
