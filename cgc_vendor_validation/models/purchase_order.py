# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.constrains('state', 'partner_id')
    def _check_vendor_validation(self):
        for order in self:
            if order.state in ['purchase', 'done'] and order.partner_id:
                if not order.partner_id.is_vendor_validated:
                    progress = order.partner_id.validation_progress
                    raise UserError(_(
                        'Cannot confirm Purchase Order: The vendor "%s" has not completed their required compliance validation '
                        '(Current Progress: %d%%). Please ensure all required documents are uploaded.'
                    ) % (order.partner_id.name, int(progress)))
