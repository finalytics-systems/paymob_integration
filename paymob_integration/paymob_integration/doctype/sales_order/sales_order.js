// Sales Order Custom Script for Paymob Integration

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        // Add Paymob buttons only if document is submitted
        if (frm.doc.docstatus === 1) {
            add_paymob_buttons(frm);
        }
    },
    
    onload: function(frm) {
        // Initialize Paymob integration
        initialize_paymob_integration();
    }
});

function add_paymob_buttons(frm) {
    // Add Create Payment Link button
    if (!frm.doc.paymob_payment_link) {
        frm.add_custom_button(__('Create Payment Link'), function() {
            create_payment_link(frm);
        }, __('Paymob'));
    }
    
    // Add View Payment Link button
    if (frm.doc.paymob_payment_link) {
        frm.add_custom_button(__('View Payment Link'), function() {
            view_payment_link(frm);
        }, __('Paymob'));
        
        frm.add_custom_button(__('Copy Payment Link'), function() {
            copy_payment_link(frm);
        }, __('Paymob'));
    }
    
    // Add Send Payment Email button
    if (frm.doc.paymob_payment_link && frm.doc.paymob_payment_status !== 'Paid') {
        frm.add_custom_button(__('Send Payment Email'), function() {
            send_payment_email(frm);
        }, __('Paymob'));
    }
    
    // Add Check Payment Status button
    frm.add_custom_button(__('Check Payment Status'), function() {
        check_payment_status(frm);
    }, __('Paymob'));
    
    // Add Test Connection button (for admin users)
    if (frappe.user.has_role('System Manager')) {
        frm.add_custom_button(__('Test Paymob Connection'), function() {
            test_paymob_connection(frm);
        }, __('Paymob'));
    }
}

function create_payment_link(frm) {
    frappe.confirm(
        __('Are you sure you want to create a payment link for this Sales Order?'),
        function() {
            frappe.call({
                method: 'paymob_integration.paymob_integration.api.create_payment_link',
                args: {
                    sales_order_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message.status === 'success') {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Payment link created and sent to customer successfully!'),
                            indicator: 'green'
                        });
                        frm.reload_doc();
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            message: r.message.message,
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}

function view_payment_link(frm) {
    if (frm.doc.paymob_payment_link) {
        frappe.msgprint({
            title: __('Payment Link'),
            message: `<a href="${frm.doc.paymob_payment_link}" target="_blank">${frm.doc.paymob_payment_link}</a>`,
            indicator: 'blue'
        });
    }
}

function copy_payment_link(frm) {
    if (frm.doc.paymob_payment_link) {
        navigator.clipboard.writeText(frm.doc.paymob_payment_link).then(function() {
            frappe.msgprint({
                title: __('Success'),
                message: __('Payment link copied to clipboard'),
                indicator: 'green'
            });
        }).catch(function(err) {
            frappe.msgprint({
                title: __('Error'),
                message: __('Failed to copy payment link'),
                indicator: 'red'
            });
        });
    }
}

function send_payment_email(frm) {
    frappe.confirm(
        __('Are you sure you want to send the payment email to the customer?'),
        function() {
            frappe.call({
                method: 'paymob_integration.paymob_integration.api.send_payment_email',
                args: {
                    sales_order_name: frm.doc.name
                },
                callback: function(r) {
                    if (r.message.status === 'success') {
                        frappe.msgprint({
                            title: __('Success'),
                            message: __('Payment email sent to customer successfully!'),
                            indicator: 'green'
                        });
                    } else {
                        frappe.msgprint({
                            title: __('Error'),
                            message: r.message.message,
                            indicator: 'red'
                        });
                    }
                }
            });
        }
    );
}

function check_payment_status(frm) {
    frappe.call({
        method: 'paymob_integration.paymob_integration.api.get_payment_status',
        args: {
            sales_order_name: frm.doc.name
        },
        callback: function(r) {
            if (r.message.status === 'error') {
                frappe.msgprint({
                    title: __('Error'),
                    message: r.message.message,
                    indicator: 'red'
                });
            } else {
                let status_message = `
                    <div style="padding: 10px;">
                        <p><strong>Paymob Order ID:</strong> ${r.message.paymob_order_id || 'N/A'}</p>
                        <p><strong>Transaction ID:</strong> ${r.message.paymob_transaction_id || 'N/A'}</p>
                        <p><strong>Payment Status:</strong> ${r.message.paymob_payment_status || 'Pending'}</p>
                        <p><strong>Payment Entry:</strong> ${r.message.paymob_payment_entry || 'N/A'}</p>
                    </div>
                `;
                
                frappe.msgprint({
                    title: __('Payment Status'),
                    message: status_message,
                    indicator: 'blue'
                });
                
                frm.reload_doc();
            }
        }
    });
}

function test_paymob_connection(frm) {
    frappe.call({
        method: 'paymob_integration.paymob_integration.api.test_paymob_connection',
        callback: function(r) {
            if (r.message.status === 'success') {
                frappe.msgprint({
                    title: __('Connection Test Successful'),
                    message: r.message.message,
                    indicator: 'green'
                });
            } else {
                frappe.msgprint({
                    title: __('Connection Test Failed'),
                    message: r.message.message,
                    indicator: 'red'
                });
            }
        }
    });
}

function initialize_paymob_integration() {
    // This function can be called to initialize any Paymob-related setup
    console.log('Paymob integration initialized for Sales Order');
}
