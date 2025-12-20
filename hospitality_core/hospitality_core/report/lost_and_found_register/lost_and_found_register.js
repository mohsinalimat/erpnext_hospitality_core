frappe.query_reports["Lost and Found Register"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("Found From"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.now_date(), -90),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("Found To"),
            "fieldtype": "Date",
            "default": frappe.datetime.now_date(),
            "reqd": 1
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ["", "Found", "Claimed", "Disposed"],
            "default": ""
        }
    ]
};