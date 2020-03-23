from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    group_shippings = fields.Boolean(
        "Group shippings",
        related="out_type_id.group_pickings",
        readonly=False,
        help="Group shippings for the same partner and carrier. "
        "Shippings with shipping policy set to "
        "'When all products are ready' are never grouped.",
    )
