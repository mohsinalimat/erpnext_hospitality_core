import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Ledger Type"), "fieldname": "ledger_type", "fieldtype": "Data", "width": 200},
        {"label": _("Description"), "fieldname": "description", "fieldtype": "Data", "width": 300},
        {"label": _("Count"), "fieldname": "count", "fieldtype": "Int", "width": 100},
        {"label": _("Total Receivable"), "fieldname": "balance", "fieldtype": "Currency", "width": 150}
    ]

    data = []

    # 1. Calculate Guest Ledger (In-House Private Guests)
    # Logic: Status Open, Company is Null/Empty
    guest_stats = frappe.db.sql("""
        SELECT COUNT(name) as cnt, SUM(outstanding_balance) as bal
        FROM `tabGuest Folio`
        WHERE status = 'Open' 
        AND (company IS NULL OR company = '')
    """, as_dict=True)[0]

    data.append({
        "ledger_type": "Guest Ledger",
        "description": "Current In-House Guests (Private Pay)",
        "count": guest_stats.cnt or 0,
        "balance": guest_stats.bal or 0.0
    })

    # 2. Calculate City Ledger (Corporate/Direct Bill)
    # Logic: Status Open, Company IS set. 
    # This includes the Master Company Folios created by the new logic.
    city_stats = frappe.db.sql("""
        SELECT COUNT(name) as cnt, SUM(outstanding_balance) as bal
        FROM `tabGuest Folio`
        WHERE status = 'Open' 
        AND company IS NOT NULL 
        AND company != ''
    """, as_dict=True)[0]

    data.append({
        "ledger_type": "City Ledger",
        "description": "Corporate Accounts / Direct Bill Masters",
        "count": city_stats.cnt or 0,
        "balance": city_stats.bal or 0.0
    })

    # 3. Total
    total_bal = (guest_stats.bal or 0) + (city_stats.bal or 0)
    data.append({
        "ledger_type": "<b>TOTAL</b>",
        "description": "",
        "count": (guest_stats.cnt or 0) + (city_stats.cnt or 0),
        "balance": total_bal
    })

    chart = {
        "data": {
            "labels": ["Guest Ledger", "City Ledger"],
            "datasets": [
                {"name": "Balance", "values": [guest_stats.bal or 0, city_stats.bal or 0]}
            ]
        },
        "type": "donut",
        "colors": ["#28a745", "#007bff"]
    }

    return columns, data, None, chart