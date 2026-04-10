from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('partner_id')
    def _check_vendor_validated(self):
        for order in self:
            if order.partner_id and not order.partner_id.is_vendor_validated:
                raise ValidationError(
                    f"Partner '{order.partner_id.name}' is not a validated vendor. "
                    "Please select a validated vendor for purchase orders."
                )