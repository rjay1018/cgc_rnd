from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('partner_id')
    def _check_vendor_validated(self):
        for order in self:
            if order.partner_id and order.partner_id.validation_progress < 100.0:
                raise ValidationError(_(
                    "Partner '%s' is not a validated vendor (progress: %d%%). Please select a fully validated vendor for purchase orders."
                ) % (order.partner_id.name, int(order.partner_id.validation_progress)))