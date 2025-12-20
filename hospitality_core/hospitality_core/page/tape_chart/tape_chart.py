import frappe
from frappe.utils import getdate

@frappe.whitelist()
def get_chart_data(start_date, end_date):
    # 1. Get all Enabled Rooms
    rooms = frappe.get_all("Hotel Room", 
        filters={"is_enabled": 1}, 
        fields=["name", "room_number", "room_type"],
        order_by="room_number asc"
    )

    # 2. Get Reservations in range
    # Logic: Arrival < End AND Departure > Start
    bookings = frappe.db.sql("""
        SELECT name, guest, room, arrival_date, departure_date, status
        FROM `tabHotel Reservation`
        WHERE status IN ('Reserved', 'Checked In')
        AND arrival_date < %(end)s AND departure_date > %(start)s
    """, {"start": start_date, "end": end_date}, as_dict=True)

    return {
        "rooms": rooms,
        "bookings": bookings
    }