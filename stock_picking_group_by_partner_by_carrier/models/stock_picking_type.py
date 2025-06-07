from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    group_pickings = fields.Boolean(
        "Group pickings",
        help="Group pickings for the same partner and carrier. "
        "Pickings with shipping policy set to "
        "'When all products are ready' are never grouped.",
    )

    show_group_pickings = fields.Boolean(compute="_compute_show_group_pickings")

    @api.depends("code", "warehouse_id.delivery_pull")
    def _compute_show_group_pickings(self):
        for record in self:
            if record.warehouse_id.delivery_pull:
                record.show_group_pickings = record.code == "outgoing"
                continue
            record.show_group_pickings = True
