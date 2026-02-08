import frappe
from parishmis.api import portal


def _resolve_user(user=None):
    if user:
        return user
    return frappe.db.get_value(
        "Parishioner",
        {"user_account": ("!=", "")},
        "user_account",
    )


def sample_bootstrap(user=None):
    """Utility to snapshot portal bootstrap payload for a given user."""
    original_user = frappe.session.user
    try:
        target_user = _resolve_user(user)
        if not target_user:
            frappe.throw("No parishioners linked to user accounts. Link at least one to test the portal API.")
        frappe.set_user(target_user)
        payload = portal.get_portal_bootstrap()
        return {
            "acting_user": target_user,
            "profile_name": payload.get("profile", {}).get("parishioner", {}).get("full_name"),
            "stats": {
                "family_members": len(payload.get("family", {}).get("members", [])),
                "sacrament_records": len(payload.get("sacraments", {}).get("records", [])),
                "contributions": len(payload.get("contributions", {}).get("entries", [])),
                "announcements": len(payload.get("announcements", [])),
                "activities": len(payload.get("activities", [])),
            },
            "peek": payload,
        }
    finally:
        frappe.set_user(original_user)


def collection_types_snapshot(user=None):
    """Utility to preview portal collection type payload."""
    original_user = frappe.session.user
    try:
        target_user = _resolve_user(user)
        if not target_user:
            frappe.throw("No portal-linked users available.")
        frappe.set_user(target_user)
        return portal.get_collection_types()
    finally:
        frappe.set_user(original_user)
