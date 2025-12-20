import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class GuestFolio(Document):
    def autoname(self):
        # Different Naming for Company Master Folios
        if self.is_company_master:
            # e.g., MASTER-GOOGLE
            # We sanitize the company name
            company_key = self.company.replace(" ", "")[:10].upper()
            self.name = make_autoname(f"MASTER-{company_key}-.#####")
        else:
            # Standard Guest Folio: FOLIO-RES-GUEST
            if self.reservation:
                self.name = make_autoname("FOLIO-.#####")
            else:
                self.name = make_autoname("FOLIO-.#####")

    def validate(self):
        self.validate_status_change()
        self.validate_master_folio()

    def validate_master_folio(self):
        if self.is_company_master and not self.company:
            frappe.throw(_("Company is mandatory for a Company Master Folio."))
        
        if not self.is_company_master and not self.reservation:
            # Regular guest folios usually need a reservation
            pass

    def validate_status_change(self):
        if self.status == "Closed":
            # Check if this folio belongs to a Company Guest
            is_company_guest = False
            if self.reservation:
                is_company_guest = frappe.db.get_value("Hotel Reservation", self.reservation, "is_company_guest")
            
            # If it is NOT a company guest, strict balance enforcement applies.
            # If it IS a company guest, we assume the balance is liable to the company and allow closure.
            if not is_company_guest:
                # For Floating Point comparison
                if self.outstanding_balance > 0.01 or self.outstanding_balance < -0.01:
                    frappe.throw(
                        _("Cannot Close Folio. Outstanding Balance is {0}. Please settle payments or post allowances.").format(self.outstanding_balance)
                    )

    def on_trash(self):
        if self.transactions:
            frappe.throw(_("Cannot delete a Folio that has transactions. Cancel it instead."))