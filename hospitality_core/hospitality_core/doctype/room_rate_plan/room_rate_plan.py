import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class RoomRatePlan(Document):
    def validate(self):
        self.validate_dates()
        if self.active:
            self.validate_overlap()

    def validate_dates(self):
        if getdate(self.valid_from) > getdate(self.valid_to):
            frappe.throw(_("Valid From date cannot be after Valid To date."))

    def validate_overlap(self):
        """
        Ensure no other Active rate plan exists for this Room Type 
        within the same date range.
        """
        overlapping = frappe.db.sql("""
            SELECT name FROM `tabRoom Rate Plan`
            WHERE room_type = %s
            AND name != %s
            AND active = 1
            AND (
                (valid_from BETWEEN %s AND %s) OR
                (valid_to BETWEEN %s AND %s) OR
                (%s BETWEEN valid_from AND valid_to)
            )
        """, (
            self.room_type, 
            self.name or "New Rate Plan", 
            self.valid_from, self.valid_to, 
            self.valid_from, self.valid_to, 
            self.valid_from
        ))

        if overlapping:
            frappe.throw(
                _("Rate Plan overlaps with existing active plan: {0} for Room Type {1}").format(
                    overlapping[0][0], self.room_type
                )
            )