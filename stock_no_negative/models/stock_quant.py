# Copyright 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools import config, float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "quantity")
    def check_negative_qty(self):
        # To provide an option to skip the check when necessary.
        if self.env.context.get("skip_negative_qty_check"):
            return

        p = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        check_negative_qty = (
            config["test_enable"] and self.env.context.get("test_stock_no_negative")
        ) or not config["test_enable"]
        if not check_negative_qty:
            return

        # Test the cheap condition first so the product, category and location
        # are only loaded for the (rare) negative quants.
        negative_quants = self.filtered(
            lambda q: float_compare(q.quantity, 0, precision_digits=p) == -1
        )
        for quant in negative_quants:
            product = quant.product_id
            location = quant.location_id
            if (
                product.is_storable
                and location.usage in ["internal", "transit"]
                and not product.allow_negative_stock
                and not product.categ_id.allow_negative_stock
                and not location.allow_negative_stock
            ):
                msg_add = ""
                if quant.lot_id:
                    msg_add = self.env._(
                        " lot %(name)s", name=quant.lot_id.display_name
                    )

                raise ValidationError(
                    self.env._(
                        "You cannot validate this stock operation because the "
                        "stock level of the product '%(name)s' %(name_lot)s would "
                        "become negative (%(q_quantity)s) on the stock location "
                        "'%(complete_name)s' and negative stock is not allowed "
                        "for this product and/or location.",
                        name=quant.product_id.display_name,
                        name_lot=msg_add,
                        q_quantity=quant.quantity,
                        complete_name=quant.location_id.complete_name,
                    )
                )
