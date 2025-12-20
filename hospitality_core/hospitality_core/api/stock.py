import frappe
from frappe import _

def deduct_inventory(doc, method=None):
    """
    Hook: Guest Folio (on_update) or Folio Transaction (after_insert).
    Logic: If a new transaction is added for a Stock Item, create a Stock Entry (Material Issue).
    """
    
    if doc.doctype != "Folio Transaction":
        return

    if doc.is_void or doc.amount <= 0:
        return

    # 1. Check if Item is a Stock Item
    item_details = frappe.db.get_value("Item", doc.item, ["is_stock_item", "default_warehouse"], as_dict=True)
    if not item_details or not item_details.is_stock_item:
        return

    # 2. Get Room Warehouse
    folio = frappe.get_doc("Guest Folio", doc.parent)
    room_warehouse = frappe.db.get_value("Hotel Room", folio.room, "warehouse")
    
    # Use Company from Folio if available, otherwise User Default
    # Note: Guest Folio doesn't strictly have a 'Company' field for the Hotel Entity, 
    # it has 'company' linking to Customer. 
    # We should rely on System Defaults or the User's Company for the Hotel's side.
    hotel_company = frappe.defaults.get_user_default("Company")
    
    if not room_warehouse:
        # Fallback to Item default or System default
        room_warehouse = item_details.default_warehouse or frappe.db.get_value("Stock Settings", None, "default_warehouse")
        
    if not room_warehouse:
        frappe.log_error(f"Skipping Stock Deduction for {doc.item}. No Warehouse found for Room {folio.room}", "Hotel Stock Error")
        return
        
    # Validate Warehouse belongs to Company
    wh_company = frappe.db.get_value("Warehouse", room_warehouse, "company")
    if wh_company != hotel_company:
        frappe.log_error(f"Warehouse {room_warehouse} belongs to {wh_company}, expected {hotel_company}", "Hotel Stock Error")
        return

    # 3. Create Stock Entry (Material Issue)
    se = frappe.new_doc("Stock Entry")
    se.stock_entry_type = "Material Issue"
    se.purpose = "Material Issue"
    se.posting_date = doc.posting_date
    se.company = hotel_company
    
    # Add Item
    se.append("items", {
        "item_code": doc.item,
        "qty": doc.qty,
        "uom": frappe.db.get_value("Item", doc.item, "stock_uom"),
        "s_warehouse": room_warehouse,
        "cost_center": frappe.get_cached_value('Company', se.company, 'cost_center')
    })
    
    try:
        se.insert(ignore_permissions=True)
        se.submit()
        frappe.msgprint(_("Consumed {0} from Warehouse {1}").format(doc.item, room_warehouse), alert=True)
        
        # Link Stock Entry to Transaction for reference
        frappe.db.set_value("Folio Transaction", doc.name, {
            "reference_doctype": "Stock Entry",
            "reference_name": se.name
        })
        
    except Exception as e:
        frappe.log_error(f"Failed to deduct stock for {doc.item}: {str(e)}", "Hotel Stock Error")