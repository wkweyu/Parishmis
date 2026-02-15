import frappe

def execute():
    """
    Force-updates the report type for the SCC and Parishioner reporting module.
    This fixes the 'Must specify a Query to run' error on Frappe Cloud.
    """
    reports_to_fix = [
        "SCC Member Count",
        "Parishioners per Church",
        "Parishioners per Group",
        "Parishioner Statistics Dashboard",
        "Church Drilldown",
        "Detailed Parishioner List"
    ]

    for report_name in reports_to_fix:
        if frappe.db.exists("Report", report_name):
            # Force update the report type to Script Report
            # and clear any stale query field that triggers the error
            frappe.db.set_value("Report", report_name, {
                "report_type": "Script Report",
                "query": "",
                "is_standard": "Yes"
            })
            
            # Reload from the latest file content
            try:
                frappe.reload_doc("parish_management_system", "report", report_name, force=True)
            except Exception:
                pass

    frappe.clear_cache()
