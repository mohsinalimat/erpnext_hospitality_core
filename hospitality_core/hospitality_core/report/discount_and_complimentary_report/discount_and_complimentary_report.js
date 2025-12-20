frappe.query_reports["Discount and Complimentary Report"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.now_date(), -30),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.now_date(),
            "reqd": 1
        },
        {
            "fieldname": "type",
            "label": __("Type"),
            "fieldtype": "Select",
            "options": ["", "Discount", "Complimentary"],
            "default": ""
        }
    ]
};