import frappe

@frappe.whitelist()
def check_availability_counts(start_date, end_date):
    # 1. Get all Room Types and their Counts
    room_types = frappe.db.sql("""
        SELECT room_type, COUNT(name) as total 
        FROM `tabHotel Room` 
        WHERE is_enabled = 1 
        GROUP BY room_type
    """, as_dict=True)

    results = []

    for rt in room_types:
        # 2. Count Bookings for this Type in Date Range
        # Logic: Overlapping reservations
        occupied = frappe.db.count("Hotel Reservation", {
            "room_type": rt.room_type,
            "status": ["in", ["Reserved", "Checked In"]],
            "arrival_date": ["<", end_date],
            "departure_date": [">", start_date]
        })
        
        results.append({
            "room_type": rt.room_type,
            "total": rt.total,
            "occupied": occupied,
            "available": rt.total - occupied
        })

    return results