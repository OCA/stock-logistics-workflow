from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    reallocation_ids = fields.One2many(
        "stock.picking.reallocation", "picking_id", "Reallocations"
    )

    current_reallocation_id = fields.Many2one(
        "stock.picking.reallocation",
        compute="_compute_current_reallocation_id",
    )

    def reallocate(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_picking_reallocation.stock_picking_reallocation_action"
        )

        if self.current_reallocation_id:
            action["res_id"] = self.current_reallocation_id.id
        return action

    @api.depends("reallocation_ids")
    def _compute_current_reallocation_id(self):
        for picking in self:
            current_reallocation_id = picking.reallocation_ids.filtered(
                lambda r: r.state == "draft"
            )

            if len(current_reallocation_id) > 1:
                # Should not happen
                older_reallocation_ids = (
                    current_reallocation_id - current_reallocation_id[-1]
                )
                older_reallocation_ids.write({"state": "cancel"})
                current_reallocation_id = current_reallocation_id[-1]

            picking.current_reallocation_id = current_reallocation_id

    def action_confirm(self):
        super().action_confirm()
        if self.current_reallocation_id:
            self.current_reallocation_id.cancel()
