import frappe
from frappe import _
from frappe.utils import nowdate, date_diff

def execute(filters=None):
    if not filters:
        filters = {}

    columns = [
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Customer", "width": 160},
        {"label": _("Master Folio"), "fieldname": "name", "fieldtype": "Link", "options": "Guest Folio", "width": 140},
        {"label": _("Open Since"), "fieldname": "open_date", "fieldtype": "Date", "width": 100},
        {"label": _("Age (Days)"), "fieldname": "age", "fieldtype": "Int", "width": 80},
        {"label": _("Guest Ref"), "fieldname": "guest_name", "fieldtype": "Data", "width": 150},
        {"label": _("Total Charges"), "fieldname": "total_charges", "fieldtype": "Currency", "width": 120},
        {"label": _("Payments/Credits"), "fieldname": "total_payments", "fieldtype": "Currency", "width": 120},
        {"label": _("Outstanding Balance"), "fieldname": "outstanding_balance", "fieldtype": "Currency", "width": 140}
    ]

    # Logic: 
    # City Ledger now strictly contains Master Folios (is_company_master = 1).
    # Individual guest folios (even if corporate) are part of Guest Ledger until checked out 
    # and transferred to the City Ledger (Master Folio).
    
    conditions = "gf.status = 'Open' AND gf.is_company_master = 1"
    
    if filters.get("company"):
        conditions += f" AND gf.company = '{filters.get('company')}'"

    sql = f"""
        SELECT
            gf.company,
            gf.name,
            gf.open_date,
            DATEDIFF(CURDATE(), gf.open_date) as age,
            guest.full_name as guest_name,
            gf.total_charges,
            gf.total_payments,
            gf.outstanding_balance
        FROM
            `tabGuest Folio` gf
        LEFT JOIN
            `tabGuest` guest ON gf.guest = guest.name
        WHERE
            {conditions}
            AND gf.outstanding_balance != 0
        ORDER BY
            gf.company, gf.open_date
    """

    data = frappe.db.sql(sql, as_dict=True)
    
    # Add Total Row
    if data:
        total = sum(d.outstanding_balance for d in data)
        data.append({
            "company": "<b>TOTAL CITY LEDGER</b>",
            "outstanding_balance": total
        })
    
    return columns, data