frappe.query_reports["Folio Balance Summary"] = {
    "filters": [
        // This report is primarily a snapshot of the current state.
        // Optional: Add Company filter if multiple hotels exist in one system.
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company")
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname === "balance" && data && data.balance > 0) {
            value = `<span style="color:red; font-weight:bold;">${value}</span>`;
        }
        return value;
    },
    "onload": function(report) {
        // Add a button to jump to detailed ledgers
        report.page.add_inner_button(__("View Guest Ledger"), function() {
            frappe.set_route("query-report", "Guest Ledger");
        });
        report.page.add_inner_button(__("View City Ledger"), function() {
            frappe.set_route("query-report", "City Ledger");
        });
    }
};