# -*- coding: utf-8 -*-
{
    'name': 'Internal Vendor Validation Management',
    'version': '19.0.2.0.4',
    'category': 'Purchases',
    'summary': 'Manage and track vendor compliance documentation',
    'description': """
        This module enforces vendor validation by requiring vendors to submit specific documents
        before they can be used in purchase orders.

        Features:
        - Configurable Requirement Types
        - Progress tracking for Vendor Document Submissions
        - Integration with Documents app for centralized compliance management
        - Constraints on Purchase Orders for unvalidated vendors
    """,
    'author': 'Rjay Lopez',
    'depends': ['base', 'purchase', 'documents'],
    'data': [
        'security/ir.model.access.csv',
        'data/document_workspace_data.xml',
        'views/vendor_requirement_views.xml',
        'views/res_partner_views.xml',
        'views/purchase_order_views.xml',
        'views/product_supplierinfo_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
