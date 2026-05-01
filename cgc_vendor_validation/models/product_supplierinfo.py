# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    partner_id = fields.Many2one(
        'res.partner',
        domain="[('supplier_rank', '>', 0), ('validation_status', '=', 'validated')]"
    )
