# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    @api.depends(
        "picking_type_id.print_documents_from_batch",
        "picking_type_id.number_copies_pickings",
        "picking_type_id.number_copies_invoices",
    )
    def _compute_print_documents(self):
        res = super()._compute_print_documents()
        for record in self:
            record.print_documents = (
                record.picking_type_id.print_documents_from_batch
                in {"pickings", "invoices_and_pickings", "invoices_or_pickings"}
                and record.picking_type_id.number_copies_pickings
                and record.picking_ids
                or record.picking_type_id.print_documents_from_batch
                in {"invoices", "invoices_and_pickings", "invoices_or_pickings"}
                and record.picking_type_id.number_copies_invoices
                and record.mapped("picking_ids.sale_id.invoice_ids")
            )
        return res
