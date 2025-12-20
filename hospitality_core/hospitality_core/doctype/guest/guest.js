frappe.ui.form.on('Guest', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            render_guest_dashboard(frm);
            
            // Add button to jump to history
            frm.add_custom_button(__('View Past Stays'), function() {
                frappe.set_route('List', 'Hotel Reservation', {guest: frm.doc.name});
            }, 'History');
        }
    }
});

function render_guest_dashboard(frm) {
    // 1. Fetch Data
    frappe.call({
        method: 'hospitality_core.hospitality_core.doctype.guest.guest.get_guest_stats',
        args: { guest: frm.doc.name },
        callback: function(r) {
            if (r.message) {
                let stats = r.message;
                
                // 2. Inject HTML
                let html = `
                <div class="row" style="margin-bottom: 20px;">
                    <div class="col-sm-3">
                        <div class="dashboard-stat-box" style="background:#f8f9fa; padding:15px; border-radius:5px; text-align:center;">
                            <h4 style="color:#6c757d;">Total Stays</h4>
                            <h2>${stats.total_stays}</h2>
                        </div>
                    </div>
                    <div class="col-sm-3">
                        <div class="dashboard-stat-box" style="background:#e8f5e9; padding:15px; border-radius:5px; text-align:center;">
                            <h4 style="color:#2e7d32;">Total Spend</h4>
                            <h2>${format_currency(stats.total_spend)}</h2>
                        </div>
                    </div>
                    <div class="col-sm-3">
                        <div class="dashboard-stat-box" style="background:#e3f2fd; padding:15px; border-radius:5px; text-align:center;">
                            <h4 style="color:#1565c0;">Last Room</h4>
                            <h2>${stats.last_room || '-'}</h2>
                        </div>
                    </div>
                    <div class="col-sm-3">
                        <div class="dashboard-stat-box" style="background:#fff3e0; padding:15px; border-radius:5px; text-align:center;">
                            <h4 style="color:#ef6c00;">Avg. Rate</h4>
                            <h2>${format_currency(stats.avg_rate)}</h2>
                        </div>
                    </div>
                </div>
                `;
                
                // Inject before the first section
                if(frm.fields_dict['full_name']) {
                    $(frm.fields_dict['full_name'].wrapper).closest('.form-section').before(html);
                }
            }
        }
    });
}