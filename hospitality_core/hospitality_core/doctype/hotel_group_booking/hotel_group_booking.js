frappe.ui.form.on('Hotel Group Booking', {
    refresh: function (frm) {
        if (!frm.is_new()) {

            // Button: Create Master Folio
            if (!frm.doc.master_folio) {
                frm.add_custom_button(__('Create Master Folio'), function () {
                    frm.call({
                        method: 'hospitality_core.hospitality_core.api.group_booking.create_master_folio',
                        args: { group_booking_name: frm.doc.name },
                        freeze: true,
                        callback: function (r) {
                            if (!r.exc) frm.reload_doc();
                        }
                    });
                }).addClass("btn-primary");
            } else {
                // Link to Folio
                frm.add_custom_button(__('View Master Folio'), function () {
                    frappe.set_route('Form', 'Guest Folio', frm.doc.master_folio);
                });
            }

            // Button: Add Reservations
            frm.add_custom_button(__('Link Reservations'), function () {
                new frappe.ui.form.MultiSelectDialog({
                    doctype: "Hotel Reservation",
                    target: frm,
                    setters: {
                        status: 'Reserved',
                    },
                    get_query() {
                        return {
                            filters: {
                                'group_booking': ['is', 'not set'],
                                'status': 'Reserved'
                            }
                        };
                    },
                    action(selections) {
                        if (selections.length === 0) {
                            frappe.msgprint(__('Please select at least one reservation.'));
                            return;
                        }
                        frm.call({
                            method: 'hospitality_core.hospitality_core.api.group_booking.add_rooms_to_group',
                            args: {
                                group_booking: frm.doc.name,
                                rooms: JSON.stringify(selections)
                            },
                            freeze: true,
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.msgprint(__('Reservations linked successfully.'));
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                });
            });

            // Button: Mass Check In
            if (frm.doc.status === 'Confirmed' || frm.doc.status === 'In House') {
                frm.add_custom_button(__('Check In Group'), function () {
                    frappe.confirm('Check In all RESERVED guests in this group?', () => {
                        frm.call({
                            method: 'hospitality_core.hospitality_core.api.group_booking.mass_check_in',
                            args: { group_booking: frm.doc.name },
                            freeze: true,
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.msgprint(r.message);
                                    frm.reload_doc();
                                }
                            }
                        });
                    });
                }, 'Actions');
            }

            // Button: Mass Check Out
            if (frm.doc.status === 'In House' || frm.doc.status === 'Checked Out') {
                frm.add_custom_button(__('Check Out Group'), function () {
                    frappe.confirm('Check Out all IN-HOUSE guests in this group?', () => {
                        frm.call({
                            method: 'hospitality_core.hospitality_core.api.group_booking.mass_check_out',
                            args: { group_booking: frm.doc.name },
                            freeze: true,
                            callback: function (r) {
                                if (!r.exc) {
                                    frappe.msgprint(r.message);
                                    frm.reload_doc();
                                }
                            }
                        });
                    });
                }, 'Actions');
            }
        }
    }
});