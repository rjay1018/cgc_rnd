# PRD: Internal Vendor Validation Management

## Core Understanding
- **Problem Statement**: We need an internal vendor validation system to ensure that unverified vendors cannot be utilized for purchasing. Vendors must submit required documentation before being eligible for purchase orders or product sourcing.
- **Success Criteria**: 
  1. A clear progress bar updates visually as vendor documents are uploaded.
  2. Vendors reach 100% progress to become automatically validated.
  3. Only vendors marked as validated are visible/selectable when creating a Purchase Order or adding a Product Supplier.
- **Target Users**: Procurement team / Purchaser.

## Technical Architectures Considered

### Option 1 (Minimal): Manual Boolean + Attachment Box
- **Description**: Add an `is_vendor_validated` boolean field and a single attachment widget to `res.partner`.
- **Pros**: Extremely fast to build.
- **Cons**: Does not track specific requirements. No calculated progress. Heavily reliant on manual manager checking.
- **Decision**: Rejected (Violates the requirement for calculated progress tracking).

### Option 2 (Medium - Preferred MVP): Requirement Types + Submissions
- **Description**: Create configuration model `vendor.requirement.type`. Add a One2Many in `res.partner` linking to `ir.attachment` directly.
- **Pros**: Fast, no enterprise dependencies.
- **Cons**: Fragmented document viewing.
- **Decision**: Rejected per user request to utilize the Documents feature.

### Option 3 (Comprehensive): Validation Workflows / Approval App Integration
- **Description**: Fully integrate with Odoo's Documents App where each document upload is stored centrally. The custom `vendor.requirement.type` links to a specific workspace in the Documents app (e.g. "Vendor Compliance"). Progress = `(Uploaded Types / Total Active Types) * 100`.
- **Pros**: Centralized view for compliance officer. Easy bulk-checking, tagging, and OCR integration in the Enterprise app. Dynamic progress calculation.
- **Cons**: Requires enterprise licensing dependency on Documents App.
- **Decision**: **Selected**. This provides the best enterprise experience by combining the progress tracking with robust centralized document management.

## Proposed Data Models 

### 1. `vendor.requirement.type`
Handles global configuration for what documents are required.
- `name`: Char (e.g., Tax ID)
- `active`: Boolean (Default True)

### 2. `vendor.validation.document`
Handles the specific submission by a vendor.
- `partner_id`: Many2one (`res.partner`)
- `requirement_type_id`: Many2one (`vendor.requirement.type`)
- `document_id`: Many2one (`documents.document`) - *Integrates with Documents App*
- `state`: Selection (Uploaded/Expired - for future scaling)

### 4. `documents.folder`
Create a dedicated Workspace/Folder during module installation logic:
- `name`: "Vendor Compliance"

### 3. `res.partner` (Extensions)
- `validation_document_ids`: One2many (`vendor.validation.document`)
- `validation_progress`: Float (Compute: number of distinct requirement types submitted / total active requirement types)
- `is_vendor_validated`: Boolean (Compute: True if validation_progress >= 100)

## UI modifications & View Inheritances
- **Partner View**: Add a new notebook page "Vendor Validation" inside the partner form containing the `validation_document_ids` One2many and a widget for `validation_progress` (progressbar).
- **Purchase Order View**: Inherit `purchase.order.form`, xpath the `partner_id` field to append `[('is_vendor_validated', '=', True)]` to its domain.
- **Supplier Info View**: Inherit `product.supplierinfo.form`, xpath the `partner_id` field to enforce the same domain.

## Constraints & Considerations
- Security: Standard purchase access rights.
- Edge Case: If a `vendor.requirement.type` is deleted/archived, the validation percentage should dynamically recalculate gracefully. (E.g., if there were 3 requirements and now only 2, the progress adjusts).
- Existing Data: Previously created active vendors will instantly become non-valid for new POs since their progress is 0%. A conversation point is raised in the Implementation Plan to consider grandfathering existing active vendors.
