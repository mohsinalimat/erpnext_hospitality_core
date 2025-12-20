frappe.ui.form.on('Guest Folio', {
    refresh: function (frm) {
        frm.set_read_only();

        // Button: Record Payment
        if (frm.doc.status === 'Open' || frm.doc.status === 'Closed') {
            frm.add_custom_button(__('Record Payment'), function () {
                make_payment_entry(frm);
            }, 'Actions');
        }

        // Button: Create Invoice
        if (frm.doc.status !== 'Provisional') {
            frm.add_custom_button(__('Create Invoice'), function () {
                frappe.confirm(
                    'Create Sales Invoice for all unbilled items?',
                    function () {
                        frm.call({
                            method: 'hospitality_core.hospitality_core.api.invoicing.create_invoice_from_folio',
                            args: {
                                folio_name: frm.doc.name
                            },
                            freeze: true,
                            callback: function (r) {
                                if (!r.exc && r.message) {
                                    frappe.msgprint('Invoice Created: ' + r.message);
                                    frappe.set_route('Form', 'Sales Invoice', r.message);
                                    frm.reload_doc();
                                }
                            }
                        });
                    }
                );
            }, 'Actions');
        }

        // Button: Move Transactions (Move Bill)
        if (frm.doc.status === 'Open') {
            frm.add_custom_button(__('Move Transactions'), function () {
                move_transactions_dialog(frm);
            }, 'Actions');
        }

        // Button: Void Transaction
        if (frm.doc.status === 'Open') {
            frm.add_custom_button(__('Void Transaction'), function () {
                void_transaction_dialog(frm);
            }, 'Actions');
        }

        // Highlight Balance
        if (frm.doc.outstanding_balance > 0) {
            frm.set_df_property('outstanding_balance', 'read_only', 1);
            $(frm.fields_dict['outstanding_balance'].wrapper).find('input').css('color', 'red').css('font-weight', 'bold');
        }
    }
});

frappe.ui.form.on('Folio Transaction', {
    item: function (frm, cdt, cdn) {
        // Automatically fetch price when Item is selected
        var row = locals[cdt][cdn];
        if (row.item) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Item Price",
                    filters: { item_code: row.item, price_list: "Standard Selling" }, // Adjust Price List as needed
                    fieldname: "price_list_rate"
                },
                callback: function (r) {
                    let rate = 0;
                    if (r.message && r.message.price_list_rate) {
                        rate = r.message.price_list_rate;
                    } else {
                        // Fallback: Get Standard Rate from Item
                        frappe.db.get_value("Item", row.item, "standard_rate", (val) => {
                            if (val && val.standard_rate) {
                                frappe.model.set_value(cdt, cdn, "amount", val.standard_rate * row.qty);
                            }
                        });
                        return;
                    }
                    frappe.model.set_value(cdt, cdn, "amount", rate * row.qty);
                }
            });

            // Default Description
            frappe.db.get_value("Item", row.item, "item_name", (r) => {
                if (r && r.item_name) frappe.model.set_value(cdt, cdn, "description", r.item_name);
            });
        }
    },

    qty: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        // Recalculate amount if rate known, or simple logic
        // This is a basic implementation. Ideally store rate separately.
    }
});

function move_transactions_dialog(frm) {
    // Filter valid transactions (not void, not invoiced)
    let valid_txns = frm.doc.transactions.filter(t => !t.is_void && !t.is_invoiced).map(t => {
        return { label: `${t.posting_date}: ${t.description} (${t.amount})`, value: t.name }
    });

    if (valid_txns.length === 0) {
        frappe.msgprint("No movable transactions found.");
        return;
    }

    var d = new frappe.ui.Dialog({
        title: 'Move Transactions to Another Folio',
        fields: [
            {
                label: 'Select Transactions',
                fieldname: 'transactions',
                fieldtype: 'MultiSelect', // Or Table MultiSelect depending on version
                options: valid_txns,
                reqd: 1,
                description: 'Ctrl+Click to select multiple'
            },
            {
                label: 'Target Folio',
                fieldname: 'target_folio',
                fieldtype: 'Link',
                options: 'Guest Folio',
                get_query: function () {
                    return {
                        filters: {
                            'status': 'Open',
                            'name': ['!=', frm.doc.name]
                        }
                    };
                },
                reqd: 1
            }
        ],
        primary_action_label: 'Move',
        primary_action: function (values) {
            // MultiSelect returns array of values or comma separated string
            let txn_list = values.transactions;
            if (typeof txn_list === 'string') {
                txn_list = txn_list.split(',').map(s => s.trim());
            }

            frappe.call({
                method: 'hospitality_core.hospitality_core.api.folio.move_transactions',
                args: {
                    transaction_names: txn_list,
                    target_folio: values.target_folio
                },
                freeze: true,
                callback: function (r) {
                    if (!r.exc) {
                        frappe.msgprint(__("Transactions moved successfully"));
                        d.hide();
                        frm.reload_doc();
                    }
                }
            });
        }
    });
    d.show();
}

function void_transaction_dialog(frm) {
    let valid_txns = frm.doc.transactions.filter(t => !t.is_void && !t.is_invoiced).map(t => {
        return { label: `${t.posting_date} - ${t.description} (${t.amount})`, value: t.name }
    });

    if (valid_txns.length === 0) {
        frappe.msgprint("No voidable transactions found.");
        return;
    }

    var d = new frappe.ui.Dialog({
        title: 'Void Transaction',
        fields: [
            {
                label: 'Select Transaction',
                fieldname: 'transaction',
                fieldtype: 'Select',
                options: valid_txns,
                reqd: 1
            },
            {
                label: 'Reason Code',
                fieldname: 'reason',
                fieldtype: 'Link',
                options: 'Allowance Reason Code',
                reqd: 1
            }
        ],
        primary_action_label: 'Void',
        primary_action: function (values) {
            frappe.call({
                method: 'hospitality_core.hospitality_core.api.financial_control.void_transaction',
                args: {
                    folio_transaction_name: values.transaction,
                    reason_code: values.reason
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
}

function make_payment_entry(frm) {
    frappe.db.get_value('Guest', frm.doc.guest, 'customer').then(r => {
        let customer = frm.doc.company || r.message.customer;

        if (!customer) {
            frappe.msgprint('Please link the Guest to a Customer record first to record payments via ERPNext.');
            return;
        }

        frappe.model.with_doctype('Payment Entry', function () {
            var pe = frappe.model.get_new_doc('Payment Entry');
            pe.payment_type = 'Receive';
            pe.party_type = 'Customer';
            pe.party = customer;
            pe.paid_amount = frm.doc.outstanding_balance;
            pe.received_amount = frm.doc.outstanding_balance;
            pe.reference_no = frm.doc.name;
            pe.reference_date = frappe.datetime.now_date();
            frappe.set_route('Form', 'Payment Entry', pe.name);
        });
    });
}