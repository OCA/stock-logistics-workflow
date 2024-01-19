# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    @api.depends(
        "picking_type_id.batch_print_pickings",
        "picking_type_id.number_copies_pickings",
        "picking_type_id.batch_print_invoices",
        "picking_type_id.number_copies_invoices",
    )
    def _compute_print_pickings(self):
        res = super()._compute_print_pickings()
        for record in self:
            if record.print_pickings or (
                record.picking_type_id.batch_print_invoices
                and record.picking_type_id.number_copies_invoices
                and record.picking_ids.sale_id.mapped("invoice_ids")
            ):
                record.print_pickings = True
            else:
                record.print_pickings = False
        return res
