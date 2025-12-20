import frappe
from frappe import _

@frappe.whitelist()
def create_master_folio(group_booking_name):
    doc = frappe.get_doc("Hotel Group Booking", group_booking_name)
    
    if doc.master_folio:
        frappe.throw(_("Master Folio already exists: {0}").format(doc.master_folio))

    if not doc.master_payer:
        frappe.throw(_("Please select a Master Payer (Customer) before creating a Folio."))

    # Create a "Dummy" Guest record for the Group if needed, or link to a generic placeholder.
    # Ideally, we create a Guest record representing the Event Organizer.
    # For this implementation, we assume a Guest record exists or we create one on the fly.
    
    organizer_guest = frappe.db.get_value("Guest", {"customer": doc.master_payer}, "name")
    if not organizer_guest:
        # Create a proxy guest for the company
        g = frappe.new_doc("Guest")
        g.full_name = doc.group_name
        g.customer = doc.master_payer
        g.insert(ignore_permissions=True)
        organizer_guest = g.name

    # Create the Master Folio
    folio = frappe.new_doc("Guest Folio")
    folio.guest = organizer_guest
    folio.company = doc.master_payer
    # We don't link a specific room or reservation, but we flag it as a Group Master
    folio.status = "Open"
    folio.save(ignore_permissions=True)
    
    # Link back
    doc.db_set("master_folio", folio.name)
    
    return folio.name

@frappe.whitelist()
def add_rooms_to_group(group_booking, rooms):
    """
    rooms: JSON string list of room names or reservations
    Logic to mass-update reservations to link them to this group.
    """
    import json
    room_list = json.loads(rooms)
    
    # room_list might be strings (IDs) or objects depending on client input
    for res_data in room_list:
        res_name = res_data if isinstance(res_data, str) else res_data.get('name') or res_data.get('hotel_reservation')
        if res_name:
            frappe.db.set_value("Hotel Reservation", res_name, {
                "group_booking": group_booking,
                "is_group_guest": 1 # Auto-flag as group guest
            })
        
    return True

@frappe.whitelist()
def mass_check_in(group_booking):
    """
    Finds all 'Reserved' bookings linked to this group and checks them in.
    """
    reservations = frappe.get_all("Hotel Reservation", 
        filters={"group_booking": group_booking, "status": "Reserved"},
        fields=["name"]
    )
    
    if not reservations:
        return {"message": _("No reserved bookings found for this group.")}
        
    count = 0
    for r in reservations:
        try:
            doc = frappe.get_doc("Hotel Reservation", r.name)
            doc.process_check_in()
            count += 1
        except Exception as e:
            frappe.log_error(message=str(e), title=f"Group Checkin Error: {r.name}")
            
    return {"message": _("Successfully Checked In {0} guests.").format(count)}

@frappe.whitelist()
def mass_check_out(group_booking):
    """
    Finds all 'Checked In' bookings linked to this group and checks them out.
    """
    reservations = frappe.get_all("Hotel Reservation", 
        filters={"group_booking": group_booking, "status": "Checked In"},
        fields=["name"]
    )
    
    if not reservations:
        return {"message": _("No in-house guests found for this group to check out.")}
        
    count = 0
    for r in reservations:
        try:
            doc = frappe.get_doc("Hotel Reservation", r.name)
            doc.process_check_out()
            count += 1
        except Exception as e:
            frappe.log_error(message=str(e), title=f"Group Checkout Error: {r.name}")
            
    return {"message": _("Successfully Checked Out {0} guests.").format(count)}