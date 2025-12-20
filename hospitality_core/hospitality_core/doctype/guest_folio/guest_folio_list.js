frappe.listview_settings['Guest Folio'] = {
    add_fields: ["status"],
    get_indicator: function (doc) {
        var colors = {
            "Provisional": "orange",
            "Open": "green",
            "Closed": "gray",
            "Cancelled": "red"
        };
        return [__(doc.status), colors[doc.status] || "grey", "status,=," + doc.status];
    }
};
