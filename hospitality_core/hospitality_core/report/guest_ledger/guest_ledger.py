import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": _("Room"), "fieldname": "room", "fieldtype": "Link", "options": "Hotel Room", "width": 80},
        {"label": _("Folio ID"), "fieldname": "name", "fieldtype": "Link", "options": "Guest Folio", "width": 140},
        {"label": _("Guest Name"), "fieldname": "guest_name", "fieldtype": "Data", "width": 160},
        {"label": _("Arr Date"), "fieldname": "arrival_date", "fieldtype": "Date", "width": 100},
        {"label": _("Dep Date"), "fieldname": "departure_date", "fieldtype": "Date", "width": 100},
        {"label": _("Charges"), "fieldname": "total_charges", "fieldtype": "Currency", "width": 120},
        {"label": _("Payments"), "fieldname": "total_payments", "fieldtype": "Currency", "width": 120},
        {"label": _("Balance (Guest)"), "fieldname": "outstanding_balance", "fieldtype": "Currency", "width": 120}
    ]

    # Logic:
    # 1. Fetch Open Guest Folios.
    # 2. Requirement: "Guests whose bills are billed to their company is filtered out".
    #    This implies we want the "Private Guest Ledger".
    #    We exclude folios where 'company' field is set (indicating Corporate master billing)
    #    OR we exclude folios where the balance is 0 (fully transferred).
    
    # We allow a filter to toggle this behavior if needed, but default is strict Guest Ledger.
    
    conditions = "gf.status = 'Open'"
    
    # If a guest is purely corporate, they usually have a company linked on the folio.
    # We exclude them to show only "Private" liability.
    if not filters.get("show_corporate"):
        conditions += " AND (gf.company IS NULL OR gf.company = '')"

    sql = f"""
        SELECT
            gf.room,
            gf.name,
            guest.full_name as guest_name,
            res.arrival_date,
            res.departure_date,
            gf.total_charges,
            gf.total_payments,
            gf.outstanding_balance
        FROM
            `tabGuest Folio` gf
        LEFT JOIN
            `tabGuest` guest ON gf.guest = guest.name
        LEFT JOIN
            `tabHotel Reservation` res ON gf.reservation = res.name
        WHERE
            {conditions}
            AND gf.outstanding_balance != 0
        ORDER BY
            gf.room ASC
    """

    data = frappe.db.sql(sql, as_dict=True)
    
    # Add Total Row
    if data:
        total_balance = sum(d.outstanding_balance for d in data)
        data.append({
            "guest_name": "<b>TOTAL RECEIVABLE</b>",
            "outstanding_balance": total_balance
        })

    return columns, data