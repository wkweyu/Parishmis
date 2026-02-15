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
    workspace.module = "Parish Management System"

    valid_shortcuts = []
    for shortcut in payload.get("shortcuts", []):
        link_type = shortcut.get("type") or shortcut.get("link_type")
        link_to = shortcut.get("link_to")
        if link_type == "DocType" and link_to and not frappe.db.exists("DocType", link_to):
            continue
        if link_type == "Report" and link_to and not frappe.db.exists("Report", link_to):
            continue
        valid_shortcuts.append(shortcut)

    valid_links = []
    for link in payload.get("links", []):
        link_type = link.get("link_type") or link.get("type")
        link_to = link.get("link_to")
        if link_type == "DocType" and link_to and not frappe.db.exists("DocType", link_to):
            continue
        if link_type == "Report" and link_to and not frappe.db.exists("Report", link_to):
            continue
        valid_links.append(link)

    content_raw = payload.get("content") or "[]"
    try:
        blocks = json.loads(content_raw)
    except Exception:
        blocks = []

    valid_labels = {s.get("label") for s in valid_shortcuts if s.get("label")}
    filtered_blocks = []
    for block in blocks:
        if block.get("type") != "shortcut":
            filtered_blocks.append(block)
            continue

        data = block.get("data") or {}
        label = data.get("label") or data.get("shortcut_name")
        if label in valid_labels:
            filtered_blocks.append(block)

    workspace.content = json.dumps(filtered_blocks, ensure_ascii=True)
    workspace.set("charts", payload.get("charts", []))
    workspace.set("shortcuts", valid_shortcuts)
    workspace.set("links", valid_links)
    workspace.save(ignore_permissions=True)
