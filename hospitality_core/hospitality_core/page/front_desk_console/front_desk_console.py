import frappe
from frappe.utils import nowdate, flt, getdate

@frappe.whitelist()
def get_console_data(target_date=None):
    if not target_date:
        target_date = nowdate()
    
    # 1. Fetch Arrivals for specific date
    # Include 'Checked Out' in arrivals list if they arrived AND left on the target date (Day Use)
    arrivals = frappe.db.sql("""
        SELECT res.name, g.full_name as guest_name, res.status, res.room, res.room_type, res.arrival_date
        FROM `tabHotel Reservation` res
        LEFT JOIN `tabGuest` g ON res.guest = g.name
        WHERE res.arrival_date = %s 
        AND res.status IN ('Reserved', 'Checked In', 'Checked Out')
        ORDER BY res.status DESC, g.full_name ASC
    """, (target_date,), as_dict=True)

    # 2. Fetch Departures for specific date
    departures = frappe.db.sql("""
        SELECT res.name, g.full_name as guest_name, res.status, res.room, res.room_type, res.departure_date
        FROM `tabHotel Reservation` res
        LEFT JOIN `tabGuest` g ON res.guest = g.name
        WHERE res.departure_date = %s 
        AND res.status IN ('Checked In', 'Checked Out')
        ORDER BY res.status ASC, res.room ASC
    """, (target_date,), as_dict=True)

    # 3. Stats Calculation (Date Sensitive)
    total_rooms = frappe.db.count("Hotel Room", {"is_enabled": 1})
    
    # Calculate In-House (Night Occupancy)
    # Logic: Arrived <= Today AND Departing > Today.
    # This captures:
    #   - Old Check-ins (Stayovers)
    #   - New Check-ins (Arrivals)
    # It Excludes:
    #   - Due Outs (Departing Today) -> These rooms are considered available for tonight once vacated.
    in_house_count = frappe.db.count("Hotel Reservation", {
        "arrival_date": ["<=", target_date],
        "departure_date": [">", target_date],
        "status": "Checked In" 
    })

    # Arrivals Pending (Reserved for this date)
    # These represent potential In-House guests for tonight who haven't arrived yet.
    arrivals_pending = len([a for a in arrivals if a.status == 'Reserved'])
    
    # Departures Pending (Checked In with departure on this date)
    # These are guests physically present right now but expected to leave.
    departures_pending = len([d for d in departures if d.status == 'Checked In'])
    
    available_today_departures = len([d for d in departures if d.status == 'Checked Out'])
    
    # Available Rooms Calculation
    # Logic: Total - (Currently In House for Night + Reserved Arrivals) - OOO
    # Note: A room that checks out today is available for a new arrival tonight.
    ooo_rooms = frappe.db.count("Hotel Room", {"status": "Out of Order", "is_enabled": 1})
    
    # Committed Rooms = People staying tonight + People arriving tonight
    committed_rooms = in_house_count + arrivals_pending
    
    available = total_rooms - committed_rooms - ooo_rooms
    if available < 0: available = 0

    occupancy_pct = 0
    if total_rooms > 0:
        occupancy_pct = flt((in_house_count / total_rooms) * 100, 1)

    return {
        "arrivals": arrivals,
        "departures": departures,
        "stats": {
            "total_rooms": total_rooms,
            "in_house": in_house_count,
            "occupancy_pct": occupancy_pct,
            "arrivals_pending": arrivals_pending,
            "departures_pending": departures_pending,
            "available": available
        }
    }