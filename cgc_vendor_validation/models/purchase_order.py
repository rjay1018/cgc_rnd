from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('partner_id')
    def _check_vendor_validated(self):
        for order in self:
            if order.partner_id and order.partner_id.validation_status != 'validated':
                raise ValidationError(_(
                    "Partner '%s' is not a validated vendor. Please select a validated vendor for purchase orders."
                ) % order.partner_id.name)