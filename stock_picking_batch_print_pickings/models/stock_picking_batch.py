# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    print_documents = fields.Boolean(
        help="Print Pickings from Batch",
        compute="_compute_print_documents",
    )

    @api.depends(
        "picking_type_id.print_documents_from_batch",
        "picking_type_id.number_copies_pickings",
    )
    def _compute_print_documents(self):
        for record in self:
            record.print_documents = (
                record.picking_type_id.print_documents_from_batch
                and record.picking_type_id.number_copies_pickings
                and record.picking_ids
            )

    def action_print_pickings(self):
        for record in self:
            if not record.print_documents:
                raise UserError(
                    _(
                        "Picking Type %(type)s is not configured to print from batch.",
                        type=record.picking_type_id.display_name,
                    )
                )
        return self.env.ref(
            "stock_picking_batch_print_pickings.action_report_picking_batch_print_pickings"
        ).report_action(self)
