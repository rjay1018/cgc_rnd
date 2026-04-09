# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class VendorValidationDocument(models.Model):
    _name = 'vendor.validation.document'
    _description = 'Vendor Validation Document'

    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, ondelete='cascade')
    requirement_type_id = fields.Many2one('vendor.requirement.type', string='Requirement Type', required=True)
    document_id = fields.Many2one('documents.document', string='Linked Document File', ondelete='restrict')
    
    file_name = fields.Char(string='File Name')
    file_upload = fields.Binary(string='Upload File')

    status = fields.Selection([
        ('missing', 'Missing'),
        ('uploaded', 'Uploaded'),
        ('expired', 'Expired'),
    ], string='Status', default='missing', required=True)
    upload_date = fields.Date(string='Upload Date')

    _sql_constraints = [
        ('unique_active_requirement_per_vendor', 'unique(partner_id, requirement_type_id)', 
         'This vendor already has an active document for this requirement type.')
    ]

    def _process_file_upload(self, record, binary_data, file_name):
        workspace = self.env.ref('cgc_vendor_validation.document_folder_vendor_compliance', raise_if_not_found=False)
        if not workspace:
            return None

        # Check or Create Subfolder for Supplier
        subfolder = self.env['documents.document'].search([
            ('type', '=', 'folder'),
            ('folder_id', '=', workspace.id),
            ('name', '=', record.partner_id.name)
        ], limit=1)

        if not subfolder:
            subfolder = self.env['documents.document'].create({
                'name': record.partner_id.name,
                'type': 'folder',
                'folder_id': workspace.id
            })

        # Name formatting
        doc_name = file_name if file_name else f"{record.partner_id.name} - {record.requirement_type_id.name}"
        
        # Create Document
        new_doc = self.env['documents.document'].create({
            'name': doc_name,
            'folder_id': subfolder.id,
            'datas': binary_data,
            'type': 'binary',
        })
        return new_doc

    @api.model_create_multi
    def create(self, vals_list):
        records = super(VendorValidationDocument, self).create(vals_list)
        for record in records:
            if record.file_upload:
                new_doc = self._process_file_upload(record, record.file_upload, record.file_name)
                if new_doc:
                    record.write({
                        'document_id': new_doc.id,
                        'status': 'uploaded',
                        'upload_date': fields.Date.context_today(record),
                        'file_upload': False
                    })
        return records

    def write(self, vals):
        res = super(VendorValidationDocument, self).write(vals)
        if 'file_upload' in vals and vals['file_upload']:
            for record in self:
                new_doc = self._process_file_upload(record, vals['file_upload'], vals.get('file_name') or record.file_name)
                if new_doc:
                    # Update without triggering infinite loops
                    super(VendorValidationDocument, record).write({
                        'document_id': new_doc.id,
                        'status': 'uploaded',
                        'upload_date': fields.Date.context_today(record),
                        'file_upload': False
                    })
        return res
