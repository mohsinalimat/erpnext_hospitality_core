import frappe
from frappe import _
from frappe.utils import getdate, nowdate

def execute(filters=None):
    if not filters:
        filters = {}
        
    target_date = filters.get("date") or nowdate()
    
    columns = [
        {"label": _("Room"), "fieldname": "room", "fieldtype": "Link", "options": "Hotel Room", "width": 80},
        {"label": _("Guest Name"), "fieldname": "guest_name", "fieldtype": "Data", "width": 150},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Arrival"), "fieldname": "arrival_date", "fieldtype": "Date", "width": 100},
        {"label": _("Departure"), "fieldname": "departure_date", "fieldtype": "Date", "width": 100},
        {"label": _("Rate Plan"), "fieldname": "rate_plan", "fieldtype": "Data", "width": 120},
        {"label": _("Pax"), "fieldname": "pax", "fieldtype": "Data", "width": 60, "default": "1"}, # Adults/Children
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Customer", "width": 150},
        {"label": _("Balance"), "fieldname": "balance", "fieldtype": "Currency", "width": 120}
    ]

    # Logic: 
    # House List = Rooms Occupied on Target Date.
    # Logic: Reservation Arrival <= Target AND Reservation Departure > Target
    # We filter for Status = Checked In (if today) or was active (deduced).
    
    # Note: If looking at the past, strictly relying on current 'Checked In' status is wrong.
    # We must rely on dates.
    # However, 'Checked Out' reservations are also valid for the House List of *yesterday*.
    
    sql = """
        SELECT 
            res.room,
            guest.full_name as guest_name,
            res.status,
            res.arrival_date,
            res.departure_date,
            res.rate_plan,
            res.company,
            folio.outstanding_balance as balance
        FROM
            `tabHotel Reservation` res
        LEFT JOIN
            `tabGuest` guest ON res.guest = guest.name
        LEFT JOIN
            `tabGuest Folio` folio ON res.folio = folio.name
        WHERE
            res.arrival_date <= %(date)s
            AND res.departure_date > %(date)s
            AND res.status IN ('Checked In', 'Checked Out') 
    """
    
    # Note: We include 'Checked Out' because if I run the report for Yesterday, 
    # a guest who checked out Today was "In House" Yesterday.
    # If I run it for Today, 'Checked Out' guests are gone (Departure > Today would be false), 
    # so they are correctly excluded.
    
    data = frappe.db.sql(sql, {"date": target_date}, as_dict=True)
    
    # Add Total Rooms Occupied count
    report_summary = []
    if data:
        report_summary = [
            {"value": len(data), "label": "Total Occupied Rooms", "datatype": "Int"},
        ]

    return columns, data, None, None, report_summary