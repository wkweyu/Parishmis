import frappe
from frappe import _

no_cache = 1


def _sanitize_redirect(target):
    if not target or not isinstance(target, str) or not target.startswith("/"):
        return "/portal"
    return target


def _redirect(location):
    frappe.local.flags.redirect_location = location
    raise frappe.Redirect


def get_context(context):
    if frappe.session.user != "Guest":
        if "Portal User" in frappe.get_roles():
            _redirect("/portal")
        _redirect("/app")

    context.no_header = True
    context.full_width = True
    context.no_cache = 1
    context.show_sidebar = False
    context.show_search = False
    context.page_title = _("ParishMIS Portal Login")
    context.redirect_to = _sanitize_redirect(frappe.form_dict.get("redirect-to"))
    return context