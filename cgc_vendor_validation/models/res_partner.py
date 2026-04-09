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
    
    # A non-stored field purely used to trigger side-effects when the form view loads
    trigger_auto_load_requirements = fields.Boolean(
        compute='_compute_auto_load_requirements', store=False
    )

    @api.depends('name')  # triggers when viewed due to XML inclusion
    def _compute_auto_load_requirements(self):
        for partner in self:
            partner.trigger_auto_load_requirements = True
            # Only auto-load if evaluating a real record, not a new unsaved form
            if not isinstance(partner.id, models.NewId) and partner.id:
                # Fetch all active global requirements
                active_reqs = self.env['vendor.requirement.type'].search([('active', '=', True)])
                # Find requirements we already have lines for (any status)
                existing_req_ids = partner.validation_document_ids.mapped('requirement_type_id.id')
                
                # Check for missing
                missing_reqs = active_reqs.filtered(lambda r: r.id not in existing_req_ids)
                
                # Create shell rows to allow inline file uploads
                if missing_reqs:
                    self.env['vendor.validation.document'].sudo().create([
                        {
                            'partner_id': partner.id,
                            'requirement_type_id': req.id,
                            'status': 'missing'
                        } for req in missing_reqs
                    ])

    @api.depends('validation_document_ids', 'validation_document_ids.status', 'validation_document_ids.requirement_type_id')
    def _compute_validation_progress(self):
        total_requirements_count = self.env['vendor.requirement.type'].search_count([('active', '=', True)])
        
        for partner in self:
            if total_requirements_count == 0:
                partner.validation_progress = 100.0
                partner.is_vendor_validated = True
                continue
            
            valid_docs = partner.validation_document_ids.filtered(lambda d: d.status == 'uploaded')
            unique_reqs = valid_docs.mapped('requirement_type_id')
            active_unique_reqs = unique_reqs.filtered(lambda r: r.active)

            progress = (len(active_unique_reqs) / float(total_requirements_count)) * 100.0
            
            partner.validation_progress = progress
            partner.is_vendor_validated = progress >= 100.0
