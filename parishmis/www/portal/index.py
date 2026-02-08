import frappe
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please log in to open the parishioner portal."), frappe.PermissionError)

    if "Portal User" not in frappe.get_roles():
        frappe.throw(
            _("Your account is missing the Portal User role. Contact the parish office for access."),
            frappe.PermissionError,
        )

    context.show_sidebar = False
    context.show_search = False
    context.no_cache = 1
    context.csrf_token = frappe.local.session.data.csrf_token
    context.portal_user = frappe.session.user
    context.page_title = _("ParishMIS Portal")
    return context
