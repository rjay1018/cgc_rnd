# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    validation_document_ids = fields.One2many(
        'vendor.validation.document', 'partner_id', string='Validation Documents'
    )
    validation_progress = fields.Float(
        string='Validation Progress (%)', compute='_compute_validation_progress', store=True
    )
    is_vendor_validated = fields.Boolean(
        string='Is Validated?', compute='_compute_validation_progress', store=True
    )

    @api.depends('validation_document_ids', 'validation_document_ids.status', 'validation_document_ids.requirement_type_id')
    def _compute_validation_progress(self):
        # Fetch the total number of active requirements
        total_requirements_count = self.env['vendor.requirement.type'].search_count([('active', '=', True)])
        
        for partner in self:
            if total_requirements_count == 0:
                # If there are no requirements in the system, automatically validate
                partner.validation_progress = 100.0
                partner.is_vendor_validated = True
                continue
            
            # Get unique requirement types uploaded by this vendor that are 'uploaded'
            valid_docs = partner.validation_document_ids.filtered(lambda d: d.status == 'uploaded')
            unique_reqs = valid_docs.mapped('requirement_type_id')

            # We only count requirement types that are actually active in the system
            active_unique_reqs = unique_reqs.filtered(lambda r: r.active)

            progress = (len(active_unique_reqs) / float(total_requirements_count)) * 100.0
            
            partner.validation_progress = progress
            partner.is_vendor_validated = progress >= 100.0
