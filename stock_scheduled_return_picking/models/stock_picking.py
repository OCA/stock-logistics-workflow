# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    has_return_date = fields.Boolean(related="picking_type_id.has_return_date")
    return_picking_date = fields.Datetime(string="Return date")
    linked_to = fields.Many2one(
        comodel_name="stock.picking", string="Linked to", copy=False
    )

    def button_validate(self):
        """Create the return stock picking for specific picking type."""
        result = super().button_validate()
        wiz_model = self.env["stock.return.picking"]
        for picking in self:
            if picking.has_return_date and picking.state == "done":
                wiz = wiz_model.create(
                    {
                        "picking_id": picking.id,
                        "location_id": picking.location_id.id,
                    }
                )
                wiz._onchange_picking_id()
                action = wiz.create_returns()
                return_picking = self.browse(action["res_id"])
                return_picking.scheduled_date = picking.return_picking_date
                return_picking.move_lines.write({"date": picking.return_picking_date})
                picking.linked_to = return_picking
                # Regenerate the move lines to assign original production lots
                for move in return_picking.move_lines:
                    previous_lines = move.move_line_ids
                    for rline in move.origin_returned_move_id.move_line_ids:
                        rline.copy(
                            {
                                "picking_id": move.picking_id.id,
                                "move_id": move.id,
                                "date": fields.Datetime.now(),
                                "location_id": rline.location_dest_id.id,
                                "location_dest_id": rline.location_id.id,
                                "product_uom_qty": rline.qty_done,
                            }
                        )
                    # By removing previous stock.move.lines AFTER generating
                    # the new ones, we prevent the stock move to reset its
                    # state to 'confirmed' (the state is reset when there is
                    # no reservation line on the move)
                    previous_lines.unlink()
        return result
