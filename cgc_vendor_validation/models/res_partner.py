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
    validation_status = fields.Selection([
        ('not_valid', 'Not Valid'),
        ('in_progress', 'In-Progress'),
        ('validated', 'Validated'),
    ], string='Validation Status', compute='_compute_validation_status',
       search='_search_validation_status', store=False, compute_sudo=True)

    @api.depends('validation_progress')
    def _compute_validation_status(self):
        for partner in self:
            if partner.validation_progress >= 100.0:
                partner.validation_status = 'validated'
            elif partner.validation_progress > 0:
                partner.validation_status = 'in_progress'
            else:
                partner.validation_status = 'not_valid'

    def _search_validation_status(self, operator, value):
        total_reqs = self.env['vendor.requirement.type'].search_count([('active', '=', True)])

        if total_reqs == 0:
            # If no requirements exist, everyone is 'validated'
            if operator == '=' and value == 'validated':
                return []  # match all
            return [('id', '=', -1)]  # match none

        # Get all partners with at least one upload
        self.env.cr.execute("""
            SELECT partner_id, count(DISTINCT requirement_type_id) as uploaded_count
            FROM vendor_validation_document
            WHERE status = 'uploaded'
            GROUP BY partner_id
        """)
        rows = self.env.cr.fetchall()
        uploaded_map = {r[0]: r[1] for r in rows}

        validated_ids = [pid for pid, cnt in uploaded_map.items() if cnt >= total_reqs]
        in_progress_ids = [pid for pid, cnt in uploaded_map.items() if cnt < total_reqs]

        def match(val):
            if val == 'validated':
                return [('id', 'in', validated_ids)] if validated_ids else [('id', '=', -1)]
            elif val == 'in_progress':
                return [('id', 'in', in_progress_ids)] if in_progress_ids else [('id', '=', -1)]
            else:  # not_valid — partners with zero uploads
                all_with_uploads = list(uploaded_map.keys())
                return [('id', 'not in', all_with_uploads)] if all_with_uploads else []

        if operator == '=':
            return match(value)
        elif operator == '!=':
            # negate: return partners NOT in the matched set
            matched = match(value)
            if matched == []:
                return [('id', '=', -1)]
            if matched == [('id', '=', -1)]:
                return []
            # swap in/not in
            domain = matched[0]
            if domain[1] == 'in':
                return [('id', 'not in', domain[2])]
            return [('id', 'in', domain[2])]
        elif operator == 'in' and isinstance(value, list):
            import functools
            from odoo.osv import expression
            domains = [match(v) for v in value]
            return expression.OR(domains)
        return []

    # A non-stored field purely used to trigger side-effects when the form view loads
    trigger_auto_load_requirements = fields.Boolean(
        compute='_compute_auto_load_requirements', store=False, compute_sudo=True
    )

    @api.depends('name')
    def _compute_auto_load_requirements(self):
        for partner in self:
            partner.trigger_auto_load_requirements = True
            if isinstance(partner.id, int):
                active_reqs = self.env['vendor.requirement.type'].search([('active', '=', True)])
                existing_req_ids = partner.validation_document_ids.mapped('requirement_type_id.id')
                missing_reqs = active_reqs.filtered(lambda r: r.id not in existing_req_ids)
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
                continue

            valid_docs = partner.validation_document_ids.filtered(lambda d: d.status == 'uploaded')
            unique_reqs = valid_docs.mapped('requirement_type_id')
            active_unique_reqs = unique_reqs.filtered(lambda r: r.active)

            progress = (len(active_unique_reqs) / float(total_requirements_count)) * 100.0
            partner.validation_progress = progress
