frappe.ui.form.on('Hotel Reservation', {
    refresh: function (frm) {
        // Filter Rooms based on Room Type AND Availability
        frm.set_query('room', function () {
            return {
                query: 'hospitality_core.hospitality_core.api.reservation.get_available_rooms_for_picker',
                filters: {
                    'arrival_date': frm.doc.arrival_date,
                    'departure_date': frm.doc.departure_date,
                    'room_type': frm.doc.room_type,
                    'ignore_reservation': frm.doc.name
                }
            };
        });

        // Add Workflow Buttons
        if (!frm.is_new()) {

            // CHECK IN BUTTON
            if (frm.doc.status === 'Reserved') {
                frm.add_custom_button(__('Check In'), function () {
                    frappe.confirm(
                        'Are you sure you want to Check In this guest?',
                        function () {
                            frm.call({
                                method: 'check_in_guest',
                                args: {
                                    name: frm.doc.name
                                },
                                freeze: true,
                                callback: function (r) {
                                    if (!r.exc) {
                                        frappe.msgprint('Guest Checked In Successfully');
                                        frm.reload_doc();
                                    }
                                }
                            });
                        }
                    );
                }).addClass("btn-primary");
            }

            // CHECK OUT BUTTON
            if (frm.doc.status === 'Checked In') {
                frm.add_custom_button(__('Check Out'), function () {
                    if (frm.doc.departure_date !== frappe.datetime.nowdate()) {
                        frappe.msgprint(__('Cannot Check Out. Departure date must be today.'));
                        return;
                    }
                    frappe.confirm(
                        'Are you sure you want to Check Out this guest?',
                        function () {
                            frm.call({
                                method: 'check_out_guest',
                                args: {
                                    name: frm.doc.name
                                },
                                freeze: true,
                                callback: function (r) {
                                    if (!r.exc) {
                                        frappe.msgprint('Guest Checked Out. Room marked as Dirty.');
                                        frm.reload_doc();
                                    }
                                }
                            });
                        }
                    );
                }).addClass("btn-danger");
            }

            // CANCEL RESERVATION BUTTON
            if (frm.doc.status === 'Reserved') {
                frm.add_custom_button(__('Cancel Reservation'), function () {
                    frappe.confirm(
                        'Are you sure you want to Cancel this Reservation?',
                        function () {
                            frm.call({
                                method: 'cancel_reservation',
                                args: {
                                    name: frm.doc.name
                                },
                                freeze: true,
                                callback: function (r) {
                                    if (!r.exc) {
                                        frappe.msgprint('Reservation Cancelled.');
                                        frm.reload_doc();
                                    }
                                }
                            });
                        }
                    );
                }, __('Actions'));
            }

            // Quick Access to Folio
            if (frm.doc.folio) {
                frm.add_custom_button(__('Open Folio'), function () {
                    frappe.set_route('Form', 'Guest Folio', frm.doc.folio);
                }, 'View');
            }

            // Readonly if Checked Out
            if (frm.doc.status === 'Checked Out' || frm.doc.status === 'Cancelled') {
                frm.set_read_only();
                frm.set_df_property('departure_date', 'read_only', 1);
            }
        }
        // ROOM MOVE BUTTON
        if (frm.doc.status === 'Checked In') {
            frm.add_custom_button(__('Move Room'), function () {

                var d = new frappe.ui.Dialog({
                    title: 'Move Guest to New Room',
                    fields: [
                        {
                            label: 'New Room',
                            fieldname: 'new_room',
                            fieldtype: 'Link',
                            options: 'Hotel Room',
                            get_query: function () {
                                return {
                                    filters: {
                                        'status': 'Available',
                                        'is_enabled': 1,
                                        'name': ['!=', frm.doc.room]
                                    }
                                };
                            },
                            reqd: 1
                        }
                    ],
                    primary_action_label: 'Move',
                    primary_action: function (values) {
                        frm.call({
                            method: 'hospitality_core.hospitality_core.api.room_move.process_room_move',
                            args: {
                                reservation_name: frm.doc.name,
                                new_room: values.new_room
                            },
                            freeze: true,
                            callback: function (r) {
                                if (!r.exc) {
                                    d.hide();
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                });
                d.show();

            }, 'Actions');
        }
    },

    room_type: function (frm) {
        // Clear room if type changes
        frm.set_value('room', '');
    },

    arrival_date: function (frm) {
        calculate_nights(frm);
        validate_room_availability(frm);
    },

    departure_date: function (frm) {
        calculate_nights(frm);
        validate_room_availability(frm);
    }
});

function calculate_nights(frm) {
    if (frm.doc.arrival_date && frm.doc.departure_date) {
        var diff = frappe.datetime.get_diff(frm.doc.departure_date, frm.doc.arrival_date);
        if (diff < 1) {
            frappe.msgprint("Departure must be after Arrival");
        }
    }
}

function validate_room_availability(frm) {
    if (frm.doc.room && frm.doc.arrival_date && frm.doc.departure_date) {
        frappe.call({
            method: "hospitality_core.hospitality_core.api.reservation.check_availability",
            args: {
                room: frm.doc.room,
                arrival_date: frm.doc.arrival_date,
                departure_date: frm.doc.departure_date,
                ignore_reservation: frm.doc.name
            },
            callback: function (r) {
                if (r.exc) {
                    frm.set_value('room', '');
                }
            }
        });
    }
}