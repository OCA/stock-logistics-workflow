# Copyright 2024 Binhex
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("quantity")
    def check_quantity(self):
        try:
            super().check_quantity()
        except ValidationError as ve:
            for quant in self:
                if (
                    quant.location_id.usage not in ["inventory", "supplier", "customer"]
                    and quant.lot_id
                    and quant.product_id.tracking == "serial"
                    and float_compare(
                        abs(quant.quantity),
                        1,
                        precision_rounding=quant.product_uom_id.rounding,
                    )
                    > 0
                ):
                    raise ve
