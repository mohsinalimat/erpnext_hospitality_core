import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Type"), "fieldname": "type", "fieldtype": "Data", "width": 120},
        {"label": _("Room"), "fieldname": "room", "fieldtype": "Link", "options": "Hotel Room", "width": 80},
        {"label": _("Guest"), "fieldname": "guest_name", "fieldtype": "Data", "width": 150},
        {"label": _("Item Code"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 200},
        {"label": _("Amount (Credit)"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Folio"), "fieldname": "parent", "fieldtype": "Link", "options": "Guest Folio", "width": 140},
        {"label": _("Posted By"), "fieldname": "owner", "fieldtype": "Data", "width": 120}
    ]

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    # Logic:
    # Find transactions where amount < 0 (Credits)
    # Exclude Payments (Cash, Card, Transfer)
    # Include Items named 'DISCOUNT', 'COMPLIMENTARY' or Descriptions containing 'Discount'
    
    sql = """
        SELECT
            ft.posting_date,
            CASE 
                WHEN ft.item = 'COMPLIMENTARY' OR ft.description LIKE '%%Complimentary%%' THEN 'Complimentary'
                ELSE 'Discount'
            END as type,
            gf.room,
            g.full_name as guest_name,
            ft.item,
            ft.description,
            ABS(ft.amount) as amount, -- Show as positive value for report legibility
            ft.parent,
            ft.owner
        FROM `tabFolio Transaction` ft
        JOIN `tabGuest Folio` gf ON ft.parent = gf.name
        LEFT JOIN `tabGuest` g ON gf.guest = g.name
        WHERE ft.posting_date BETWEEN %s AND %s
        AND ft.is_void = 0
        AND ft.amount < 0
        AND ft.item NOT IN ('PAYMENT', 'PAYMENT-CASH', 'PAYMENT-CARD') -- Adjust based on your payment item codes
        AND ft.item IN ('DISCOUNT', 'COMPLIMENTARY') 
        OR (ft.amount < 0 AND ft.description LIKE '%%Discount%%' AND ft.item NOT IN ('PAYMENT'))
        ORDER BY ft.posting_date DESC
    """
    
    data = frappe.db.sql(sql, (from_date, to_date), as_dict=True)

    # Chart Data
    comp_total = sum([d['amount'] for d in data if d['type'] == 'Complimentary'])
    disc_total = sum([d['amount'] for d in data if d['type'] == 'Discount'])

    chart = {
        "data": {
            "labels": ["Complimentary", "Discounts"],
            "datasets": [{"name": "Value Given", "values": [comp_total, disc_total]}]
        },
        "type": "bar",
        "colors": ["#e74c3c", "#f39c12"]
    }
    
    if data:
        data.append({
            "description": "<b>TOTAL GIVEN</b>",
            "amount": sum([d['amount'] for d in data])
        })

    return columns, data, None, chart