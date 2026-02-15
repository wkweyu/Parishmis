import json

import frappe


def execute():
    path = frappe.get_app_path(
        "parishmis",
        "parish_management_system",
        "workspace",
        "parish_management_system",
        "parish_management_system.json",
    )

    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    workspace_name = payload.get("name") or "Parish Management System"
    if not frappe.db.exists("Workspace", workspace_name):
        return

    workspace = frappe.get_doc("Workspace", workspace_name)
    if payload.get("content"):
        workspace.content = payload.get("content")
    workspace.set("charts", payload.get("charts", []))
    workspace.set("shortcuts", payload.get("shortcuts", []))
    workspace.set("links", payload.get("links", []))
    workspace.save(ignore_permissions=True)
