frappe.query_reports["Guest Ledger"] = {
    "filters": [
        {
            "fieldname": "show_corporate",
            "label": __("Include Corporate/City Ledger Guests"),
            "fieldtype": "Check",
            "default": 0,
            "description": "If checked, includes guests whose bill is paid by a Company."
        }
    ]
};