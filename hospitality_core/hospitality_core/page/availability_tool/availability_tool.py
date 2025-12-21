import frappe

@frappe.whitelist()
def check_availability_counts(start_date, end_date):
    # 1. Get all Enabled Rooms
    rooms = frappe.get_all("Hotel Room", 
        fields=["name", "room_type", "status as current_status"],
        filters={"is_enabled": 1},
        order_by="room_number"
    )

    # 2. Get all Overlapping Reservations
    reservations = frappe.db.sql("""
        SELECT room, status, name, guest
        FROM `tabHotel Reservation`
        WHERE status IN ('Reserved', 'Checked In')
        AND arrival_date < %s
        AND departure_date > %s
    """, (end_date, start_date), as_dict=True)

    reservation_map = {r.room: r for r in reservations}

    room_details = []
    summary_map = {}

    for room in rooms:
        res = reservation_map.get(room.name)
        status = "Available"
        details = ""

        if room.current_status == "Out of Order":
            status = "Out of Order"
            details = "Maintenance"
        elif res:
            if res.status == "Checked In":
                status = "Occupied"
            else:
                status = "Reserved"
            details = f"{res.name} ({res.guest})"
        
        room_details.append({
            "room": room.name,
            "room_type": room.room_type,
            "status": status,
            "details": details
        })

        # Summary Logic
        if room.room_type not in summary_map:
            summary_map[room.room_type] = {"room_type": room.room_type, "total": 0, "occupied": 0, "available": 0}
        
        summary_map[room.room_type]["total"] += 1
        if status in ["Occupied", "Reserved", "Out of Order"]:
            summary_map[room.room_type]["occupied"] += 1
        else:
            summary_map[room.room_type]["available"] += 1

    return {
        "summary": list(summary_map.values()),
        "room_details": room_details
    }