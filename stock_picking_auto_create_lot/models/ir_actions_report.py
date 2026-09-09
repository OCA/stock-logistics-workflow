# Copyright 2025 Moduon Team
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class IrActionReport(models.Model):
    _inherit = "ir.actions.report"

    def report_action(self, docids, data=None, config=True):
        # Catch a context to force lot creation on print so it can be used in different
        # scenarios without the need of defining glue modules.
        if self.env.context.get("force_auto_lot") and self.model == "stock.move.line":
            move_lines = (
                self.env["stock.move.line"]
                .browse(docids)
                .filtered(
                    lambda x: (
                        not x.lot_id
                        and not x.lot_name
                        and x.product_id.tracking != "none"
                        and (
                            x.product_id.auto_create_lot
                            or x.product_id.categ_id.auto_create_lot
                        )
                    )
                )
            )
            if move_lines:
                for line in move_lines:
                    line.lot_name = line._get_lot_sequence()
                move_lines.with_context(
                    bypass_reservation_update=True
                )._create_and_assign_production_lot()
        return super().report_action(docids, data, config)
