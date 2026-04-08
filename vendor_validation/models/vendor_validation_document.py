# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class VendorValidationDocument(models.Model):
    _name = 'vendor.validation.document'
    _description = 'Vendor Validation Document'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, ondelete='cascade')
    requirement_type_id = fields.Many2one('vendor.requirement.type', string='Requirement Type', required=True)
    document_id = fields.Many2one('documents.document', string='Document File', required=True, ondelete='restrict')
    status = fields.Selection([
        ('uploaded', 'Uploaded'),
        ('expired', 'Expired'),
    ], string='Status', default='uploaded', required=True)
    upload_date = fields.Date(string='Upload Date', default=fields.Date.context_today)

    _sql_constraints = [
        ('unique_active_requirement_per_vendor', 'unique(partner_id, requirement_type_id, status)', 
         'This vendor already has an active document for this requirement type.')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        # Auto-tag or assign folder if needed based on the Documents app workspace
        # We will retrieve the xml_id for our vendor compliance folder
        folder = self.env.ref('vendor_validation.document_folder_vendor_compliance', raise_if_not_found=False)
        for vals in vals_list:
            if 'document_id' in vals and folder:
                doc = self.env['documents.document'].browse(vals['document_id'])
                if doc.exists():
                    doc.folder_id = folder.id
                    # Optional: rename document to format: [Vendor] - [Requirement Type]
                    partner = self.env['res.partner'].browse(vals.get('partner_id'))
                    req_type = self.env['vendor.requirement.type'].browse(vals.get('requirement_type_id'))
                    if partner and req_type:
                        doc.name = f"{partner.name} - {req_type.name}"
        return super(VendorValidationDocument, self).create(vals_list)
