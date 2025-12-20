import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": _("Room"), "fieldname": "room", "fieldtype": "Data", "width": 80},
        {"label": _("Guest"), "fieldname": "guest_name", "fieldtype": "Data", "width": 150},
        {"label": _("Department / Item Group"), "fieldname": "item_group", "fieldtype": "Data", "width": 150},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 200},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120}
    ]

    # Filters
    date_from = filters.get("from_date")
    date_to = filters.get("to_date")

    # SQL Logic:
    # 1. We query `Folio Transaction`
    # 2. We join `Item` to get the Item Group (Department)
    # 3. We exclude Voided transactions and Payments (Amount < 0)
    #    *Payments are Cash Flow, not Sales Revenue.
    
    sql = """
        SELECT
            ft.posting_date,
            gf.room,
            guest.full_name as guest_name,
            item.item_group,
            ft.description,
            ft.amount
        FROM
            `tabFolio Transaction` ft
        INNER JOIN
            `tabGuest Folio` gf ON ft.parent = gf.name
        LEFT JOIN
            `tabGuest` guest ON gf.guest = guest.name
        LEFT JOIN
            `tabItem` item ON ft.item = item.name
        WHERE
            ft.posting_date BETWEEN %(from_date)s AND %(to_date)s
            AND ft.is_void = 0
            AND ft.amount > 0 
        ORDER BY
            ft.posting_date, item.item_group
    """
    
    data = frappe.db.sql(sql, {"from_date": date_from, "to_date": date_to}, as_dict=True)
    
    # Add Summary Row
    total_sales = sum([d.amount for d in data])
    if data:
        data.append({
            "posting_date": "",
            "room": "",
            "guest_name": "<b>TOTAL</b>",
            "item_group": "",
            "description": "",
            "amount": total_sales
        })

    return columns, data