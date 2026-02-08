from datetime import timedelta

import frappe
from frappe.utils import add_days, now_datetime


def preview_collection_types():
    return frappe.get_all(
        "Collection Type",
        fields=["name", "collection_type", "category", "description"],
        order_by="collection_type asc",
    )


def enrich_collection_type_descriptions():
    templates = {
        "Tithes": "Monthly tithe contributions supporting parish operations.",
        "Offering": "General weekly mass offering recorded per family.",
        "Building Fund": "Capital and building projects envelope.",
        "Sacrament Fee": "Fees collected during sacrament preparation and administration.",
        "Donation": "One-time gifts earmarked by the donor.",
        "Dues": "Association dues and mandated contributions.",
        "Other": "Miscellaneous collections captured during parish drives.",
    }

    updated = []
    for doc in preview_collection_types():
        base = templates.get(doc.category, templates.get(doc.collection_type))
        if not base:
            base = f"{doc.collection_type} contributions tracked in ParishMIS."
        frappe.db.set_value("Collection Type", doc.name, "description", base, update_modified=False)
        updated.append({"name": doc.name, "collection_type": doc.collection_type, "description": base})

    frappe.db.commit()
    return updated


def seed_church_activities(church: str, parish: str):
    schedule = [
        {
            "title": "Family Life Workshop",
            "category": "Formation",
            "start_days": 3,
            "duration_hours": 2,
            "location": "Parish Hall",
            "audience_scope": "Church",
        },
        {
            "title": "Youth Praise Vigil",
            "category": "Community",
            "start_days": 7,
            "duration_hours": 3,
            "location": "Main Sanctuary",
            "audience_scope": "Church",
        },
        {
            "title": "Charity Medical Camp",
            "category": "Other",
            "start_days": 14,
            "duration_hours": 6,
            "location": "Parish Grounds",
            "audience_scope": "Parish",
        },
    ]

    created = []
    for item in schedule:
        start = add_days(now_datetime(), item["start_days"])
        end = start + timedelta(hours=item["duration_hours"])
        doc = frappe.get_doc(
            {
                "doctype": "Church Activity",
                "title": item["title"],
                "category": item["category"],
                "audience_scope": item["audience_scope"],
                "status": "Scheduled",
                "parish": parish,
                "church": church,
                "start_datetime": start,
                "end_datetime": end,
                "location": item["location"],
                "description": f"{item['title']} hosted at {item['location']}.",
                "is_published": 1,
            }
        )
        doc.insert(ignore_permissions=True)
        created.append(doc.name)

    return created
