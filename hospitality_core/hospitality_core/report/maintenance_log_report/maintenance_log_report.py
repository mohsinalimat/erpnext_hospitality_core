import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": _("Date Reported"), "fieldname": "creation", "fieldtype": "Date", "width": 100},
        {"label": _("Request ID"), "fieldname": "name", "fieldtype": "Link", "options": "Hotel Maintenance Request", "width": 140},
        {"label": _("Room"), "fieldname": "room", "fieldtype": "Link", "options": "Hotel Room", "width": 80},
        {"label": _("Issue Type"), "fieldname": "issue_type", "fieldtype": "Data", "width": 100},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 250},
        {"label": _("Reported By"), "fieldname": "reported_by_name", "fieldtype": "Data", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Resolution Notes"), "fieldname": "resolution_notes", "fieldtype": "Data", "width": 200}
    ]

    conditions = "1=1"
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions += f" AND DATE(hmr.creation) BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"

    if filters.get("status"):
        conditions += f" AND hmr.status = '{filters.get('status')}'"

    sql = f"""
        SELECT
            DATE(hmr.creation) as creation,
            hmr.name,
            hmr.room,
            hmr.issue_type,
            hmr.description,
            u.full_name as reported_by_name,
            hmr.status,
            hmr.resolution_notes
        FROM
            `tabHotel Maintenance Request` hmr
        LEFT JOIN
            `tabUser` u ON hmr.reported_by = u.name
        WHERE
            {conditions}
        ORDER BY
            hmr.creation DESC
    """
    
    data = frappe.db.sql(sql, as_dict=True)
    
    return columns, data