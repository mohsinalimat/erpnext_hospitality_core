import frappe
from frappe import _
from frappe.utils import add_days, date_diff, getdate, flt

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 110},
        {"label": _("Total Rooms"), "fieldname": "total_rooms", "fieldtype": "Int", "width": 100},
        {"label": _("Occupied"), "fieldname": "occupied_rooms", "fieldtype": "Int", "width": 100},
        {"label": _("Occupancy %"), "fieldname": "occupancy_pct", "fieldtype": "Percent", "width": 110},
        {"label": _("Room Revenue"), "fieldname": "revenue", "fieldtype": "Currency", "width": 130},
        {"label": _("ADR"), "fieldname": "adr", "fieldtype": "Currency", "width": 120, "description": "Average Daily Rate"},
        {"label": _("RevPAR"), "fieldname": "revpar", "fieldtype": "Currency", "width": 120, "description": "Revenue Per Available Room"}
    ]

    data = []
    
    start_date = getdate(filters.get("from_date"))
    end_date = getdate(filters.get("to_date"))
    
    # 1. Total Inventory (Count of enabled rooms)
    total_rooms_count = frappe.db.count("Hotel Room", filters={"is_enabled": 1})

    # 2. Fetch all Room Revenue Transactions in range
    # Grouped by Date
    revenue_map = {}
    rev_sql = """
        SELECT posting_date, SUM(amount) as total
        FROM `tabFolio Transaction`
        WHERE posting_date BETWEEN %s AND %s
        AND is_void = 0
        AND item IN (SELECT name FROM `tabItem` WHERE item_code='ROOM-RENT' OR item_group='Accommodation')
        GROUP BY posting_date
    """
    rev_data = frappe.db.sql(rev_sql, (start_date, end_date), as_dict=True)
    for r in rev_data:
        revenue_map[str(r.posting_date)] = flt(r.total)

    # 3. Loop through dates
    curr_date = start_date
    while curr_date <= end_date:
        str_date = curr_date.strftime("%Y-%m-%d")
        
        # Calculate Occupied
        # Count reservations where Date is within [Arrival, Departure)
        # We explicitly exclude Checked Out if they left BEFORE this date, 
        # but the date range check handles that.
        # Status must be Checked In (for live) or Checked Out (for history).
        occupied_count = frappe.db.count("Hotel Reservation", {
            "arrival_date": ["<=", str_date],
            "departure_date": [">", str_date], 
            "status": ["in", ["Checked In", "Checked Out"]] 
        })

        revenue = revenue_map.get(str_date, 0.0)
        
        # Calculations
        occupancy = (occupied_count / total_rooms_count * 100) if total_rooms_count else 0.0
        adr = (revenue / occupied_count) if occupied_count else 0.0
        revpar = (revenue / total_rooms_count) if total_rooms_count else 0.0

        data.append({
            "date": str_date,
            "total_rooms": total_rooms_count,
            "occupied_rooms": occupied_count,
            "occupancy_pct": flt(occupancy, 2),
            "revenue": revenue,
            "adr": flt(adr, 2),
            "revpar": flt(revpar, 2)
        })

        curr_date = add_days(curr_date, 1)

    # Chart Configuration
    chart = {
        "data": {
            "labels": [d["date"] for d in data],
            "datasets": [
                {"name": "Occupancy %", "values": [d["occupancy_pct"] for d in data]},
                {"name": "RevPAR", "values": [d["revpar"] for d in data]}
            ]
        },
        "type": "line",
        "colors": ["#7cd6fd", "#743ee2"]
    }

    return columns, data, None, chart