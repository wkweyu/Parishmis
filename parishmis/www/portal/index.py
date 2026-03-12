import frappe
from frappe import _

no_cache = 1


def _redirect(location):
    frappe.local.flags.redirect_location = location
    raise frappe.Redirect


def get_context(context):
    if frappe.session.user == "Guest":
        _redirect("/portal/login?redirect-to=/portal")

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
