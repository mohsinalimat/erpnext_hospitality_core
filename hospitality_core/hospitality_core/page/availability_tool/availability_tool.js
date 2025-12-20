frappe.pages['availability-tool'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Room Availability Query',
        single_column: true
    });

    page.add_field({
        fieldname: 'date_range',
        label: 'Date Range',
        fieldtype: 'DateRange',
        default: [frappe.datetime.now_date(), frappe.datetime.add_days(frappe.datetime.now_date(), 1)],
        reqd: 1
    });

    page.set_primary_action('Check', function() {
        let dates = page.fields_dict.date_range.get_value();
        if(!dates) return;
        
        // DateRange field returns string "YYYY-MM-DD to YYYY-MM-DD" or array depending on version.
        // We assume Array for modern Frappe.
        let start = dates[0];
        let end = dates[1];

        frappe.call({
            method: "hospitality_core.hospitality_core.page.availability_tool.availability_tool.check_availability_counts",
            args: { start_date: start, end_date: end },
            freeze: true,
            callback: function(r) {
                render_results(wrapper, r.message);
            }
        });
    });
    
    $(wrapper).find('.layout-main-section').append('<div id="avail-results" style="margin-top:20px;"></div>');
}

function render_results(wrapper, data) {
    let html = `<table class="table table-bordered">
        <thead><tr style="background-color:#f0f4f7;"><th>Room Type</th><th>Total Rooms</th><th>Occupied/Reserved</th><th>Available</th></tr></thead>
        <tbody>`;
    
    data.forEach(row => {
        let color = row.available > 0 ? 'green' : 'red';
        html += `
            <tr>
                <td><b>${row.room_type}</b></td>
                <td>${row.total}</td>
                <td>${row.occupied}</td>
                <td style="color:${color}; font-weight:bold; font-size:1.2em;">${row.available}</td>
            </tr>
        `;
    });
    
    html += `</tbody></table>`;
    $('#avail-results').html(html);
}