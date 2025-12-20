import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class HotelGroupBooking(Document):
    def validate(self):
        self.validate_dates()
        self.validate_status()

    def validate_dates(self):
        if self.arrival_date and self.departure_date:
            if getdate(self.arrival_date) >= getdate(self.departure_date):
                frappe.throw(_("Departure Date must be after Arrival Date."))

    def validate_status(self):
        # Prevent checking in a group without a financial master folio
        if self.status in ["In House", "Checked Out"] and not self.master_folio:
            frappe.throw(
                _("Cannot change status to '{0}' until a Master Folio is created. Please click 'Create Master Folio'.").format(self.status)
            )

        # If Status is Confirmed, Master Payer is mandatory
        if self.status == "Confirmed" and not self.master_payer:
            frappe.throw(_("Please select a Master Payer (Customer) to confirm this group booking."))