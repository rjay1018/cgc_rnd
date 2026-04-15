# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    partner_id = fields.Many2one(
        'res.partner',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('validation_progress', '=', 100)]"
    )
