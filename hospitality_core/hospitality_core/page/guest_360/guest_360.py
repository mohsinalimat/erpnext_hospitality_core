import frappe
from frappe.utils import flt

@frappe.whitelist()
def get_guest_details(guest):
    if not guest:
        return {}

    # 1. Profile
    guest_doc = frappe.get_doc("Guest", guest)
    
    # 2. History (Reservations joined with Folio for balance)
    history = frappe.db.sql("""
        SELECT 
            res.name, res.status, res.arrival_date, res.departure_date, res.room, res.room_type,
            COALESCE(gf.outstanding_balance, 0) as balance
        FROM `tabHotel Reservation` res
        LEFT JOIN `tabGuest Folio` gf ON res.folio = gf.name
        WHERE res.guest = %s
        ORDER BY res.arrival_date DESC
    """, (guest,), as_dict=True)

    # 3. Stats
    total_stays = len([h for h in history if h.status == 'Checked Out'])
    
    # Total Spend from Closed Folios
    spend_data = frappe.db.sql("""
        SELECT SUM(total_charges) as total 
        FROM `tabGuest Folio` 
        WHERE guest = %s AND status = 'Closed'
    """, (guest,), as_dict=True)[0]
    total_spend = flt(spend_data.total)
    
    avg_rate = (total_spend / total_stays) if total_stays else 0
    
    last_stay = next((h for h in history if h.status == 'Checked Out'), None)
    
    return {
        "guest": guest_doc,
        "history": history,
        "stats": {
            "total_stays": total_stays,
            "total_spend": total_spend,
            "avg_rate": avg_rate,
            "last_room": last_stay.room if last_stay else None,
            "last_visit": last_stay.departure_date if last_stay else None
        }
    }