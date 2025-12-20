frappe.pages['guest-360'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Guest 360 View',
        single_column: true
    });

    // 1. Search Field
    page.add_field({
        fieldname: 'guest',
        label: 'Search Guest',
        fieldtype: 'Link',
        options: 'Guest',
        change: function() {
            let guest = page.fields_dict.guest.get_value();
            if(guest) render_guest_profile(wrapper, guest);
        }
    });

    // CSS
    $(`<style>
        .g360-card { background: #fff; border: 1px solid #d1d8dd; border-radius: 8px; padding: 20px; margin-bottom: 20px; height: 100%; }
        .g360-header { font-size: 18px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        .g360-stat-val { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .g360-stat-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }
        .g360-tag { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 5px;}
        .tag-vip { background: #ffd700; color: #000; }
        .tag-reg { background: #e0e0e0; color: #333; }
        .tag-corp { background: #3498db; color: #fff; }
    </style>`).appendTo(wrapper);

    $(wrapper).find('.layout-main-section').append('<div id="g360-content" style="margin-top: 20px;"></div>');
    
    $('#g360-content').html('<div class="text-center text-muted p-5">Please select a guest to view details.</div>');
}

function render_guest_profile(wrapper, guest_name) {
    frappe.call({
        method: "hospitality_core.hospitality_core.page.guest_360.guest_360.get_guest_details",
        args: { guest: guest_name },
        freeze: true,
        callback: function(r) {
            if(r.message) {
                let d = r.message;
                let html = `
                <div class="row">
                    <!-- Profile Card -->
                    <div class="col-md-4">
                        <div class="g360-card">
                            <div class="g360-header">Profile</div>
                            <div class="text-center mb-3">
                                <div class="avatar avatar-xl" style="width: 80px; height: 80px; margin: 0 auto; background: #f0f0f0; border-radius: 50%; line-height: 80px; font-size: 32px;">
                                    ${d.guest.full_name.charAt(0)}
                                </div>
                                <h4 class="mt-2">${d.guest.full_name}</h4>
                                <span class="g360-tag ${d.guest.guest_type === 'VIP' ? 'tag-vip' : (d.guest.guest_type === 'Corporate' ? 'tag-corp' : 'tag-reg')}">
                                    ${d.guest.guest_type}
                                </span>
                            </div>
                            <table class="table table-borderless table-sm">
                                <tr><td class="text-muted">Email:</td><td>${d.guest.email_id || '-'}</td></tr>
                                <tr><td class="text-muted">Mobile:</td><td>${d.guest.mobile_no || '-'}</td></tr>
                                <tr><td class="text-muted">Customer:</td><td>${d.guest.customer || '-'}</td></tr>
                                <tr><td class="text-muted">Address:</td><td>${d.guest.address || '-'}</td></tr>
                            </table>
                            <button class="btn btn-default btn-sm btn-block mt-3" onclick="frappe.set_route('Form', 'Guest', '${d.guest.name}')">Edit Profile</button>
                        </div>
                    </div>

                    <!-- Stats Card -->
                    <div class="col-md-8">
                        <div class="g360-card">
                            <div class="g360-header">Performance Stats</div>
                            <div class="row text-center">
                                <div class="col-sm-4">
                                    <div class="g360-stat-val">${d.stats.total_stays}</div>
                                    <div class="g360-stat-label">Total Visits</div>
                                </div>
                                <div class="col-sm-4">
                                    <div class="g360-stat-val">${format_currency(d.stats.total_spend)}</div>
                                    <div class="g360-stat-label">Lifetime Spend</div>
                                </div>
                                <div class="col-sm-4">
                                    <div class="g360-stat-val">${format_currency(d.stats.avg_rate)}</div>
                                    <div class="g360-stat-label">Avg Nightly Rate</div>
                                </div>
                            </div>
                            <hr>
                            <div class="row text-center mt-3">
                                <div class="col-sm-4">
                                    <div class="g360-stat-val" style="font-size: 18px;">${d.stats.last_room || '-'}</div>
                                    <div class="g360-stat-label">Last Room</div>
                                </div>
                                <div class="col-sm-4">
                                    <div class="g360-stat-val" style="font-size: 18px;">${d.stats.last_visit ? frappe.datetime.str_to_user(d.stats.last_visit) : '-'}</div>
                                    <div class="g360-stat-label">Last Checked Out</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- History Table -->
                <div class="row">
                    <div class="col-md-12">
                        <div class="g360-card">
                            <div class="g360-header">Stay History</div>
                            <table class="table table-bordered table-hover">
                                <thead style="background-color: #f8f9fa;">
                                    <tr>
                                        <th>Reservation</th>
                                        <th>Status</th>
                                        <th>Arrival</th>
                                        <th>Departure</th>
                                        <th>Room</th>
                                        <th>Folio Balance</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${d.history.map(row => `
                                    <tr style="cursor: pointer;" onclick="frappe.set_route('Form', 'Hotel Reservation', '${row.name}')">
                                        <td>${row.name}</td>
                                        <td>${row.status}</td>
                                        <td>${frappe.datetime.str_to_user(row.arrival_date)}</td>
                                        <td>${frappe.datetime.str_to_user(row.departure_date)}</td>
                                        <td>${row.room} - ${row.room_type}</td>
                                        <td class="text-right">${format_currency(row.balance)}</td>
                                    </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                            ${d.history.length === 0 ? '<p class="text-center text-muted">No history found.</p>' : ''}
                        </div>
                    </div>
                </div>
                `;
                $('#g360-content').html(html);
            }
        }
    });
}