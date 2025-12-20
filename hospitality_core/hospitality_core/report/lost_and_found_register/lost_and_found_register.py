import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": _("ID"), "fieldname": "name", "fieldtype": "Link", "options": "Lost and Found Item", "width": 120},
        {"label": _("Date Found"), "fieldname": "found_date", "fieldtype": "Date", "width": 100},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {"label": _("Found In"), "fieldname": "found_location", "fieldtype": "Data", "width": 120, "description": "Room or Area"},
        {"label": _("Found By"), "fieldname": "finder_name", "fieldtype": "Data", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80},
        {"label": _("Claimed By"), "fieldname": "claimant_info", "fieldtype": "Data", "width": 180},
        {"label": _("Date Claimed"), "fieldname": "claimed_date", "fieldtype": "Date", "width": 100}
    ]

    conditions = "1=1"
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions += f" AND lnf.found_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'"

    if filters.get("status"):
        conditions += f" AND lnf.status = '{filters.get('status')}'"

    sql = f"""
        SELECT
            lnf.name,
            lnf.found_date,
            lnf.item_name,
            lnf.found_location,
            emp.employee_name as finder_name,
            lnf.status,
            lnf.claimant_info,
            lnf.claimed_date
        FROM
            `tabLost and Found Item` lnf
        LEFT JOIN
            `tabEmployee` emp ON lnf.finder = emp.name
        WHERE
            {conditions}
        ORDER BY
            lnf.found_date DESC
    """
    
    data = frappe.db.sql(sql, as_dict=True)
    
    return columns, data