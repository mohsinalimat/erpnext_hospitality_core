frappe.query_reports["Maintenance Log Report"] = {
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
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ["", "Reported", "In Progress", "Completed", "Cancelled"],
            "default": ""
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname === "status") {
            if (data.status === "Reported") {
                value = `<span style="color:red; font-weight:bold;">${value}</span>`;
            } else if (data.status === "In Progress") {
                value = `<span style="color:orange;">${value}</span>`;
            } else if (data.status === "Completed") {
                value = `<span style="color:green;">${value}</span>`;
            }
        }
        return value;
    }
};