# -*- coding: utf-8 -*-

from odoo import models, fields

class VendorRequirementType(models.Model):
    _name = 'vendor.requirement.type'
    _description = 'Vendor Requirement Type'
    _order = 'name'

    name = fields.Char(string='Requirement Name', required=True, translate=True)
    active = fields.Boolean(default=True, help="If unchecked, it will be hidden without removing it.")
