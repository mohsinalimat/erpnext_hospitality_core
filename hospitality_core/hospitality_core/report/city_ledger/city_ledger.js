frappe.query_reports["City Ledger"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Customer (Company)"),
            "fieldtype": "Link",
            "options": "Customer",
            "reqd": 0
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Highlight old debts (> 30 days)
        if (column.fieldname === "age" && data && data.age > 30) {
            value = `<span style="color:red; font-weight:bold;">${value}</span>`;
        }
        
        // Highlight negative balances (Credits) in green
        if (column.fieldname === "outstanding_balance" && data && data.outstanding_balance < 0) {
            value = `<span style="color:green;">${value}</span>`;
        }

        return value;
    }
};