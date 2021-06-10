# Copyright 2020-2021 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


RESERVED_STATEMENT = """
SELECT SUM(product_qty) AS reserved_in_moves
 FROM stock_move_line
 WHERE location_id = %(location_id)s
   AND product_id = %(product_id)s
"""


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "reserved_quantity")
    def check_reserved_quantity(self):
        """Check the consistency of reservations.

        - reservations can only be done on physical locations;
        - the sum of reservations for a product on a location, must match the
          move lines having that location as a source location.
        """
        virtual_locations = (
            "vendor",
            "customer",
            "inventory",
            "view",
        )
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for quant in self:
            reserved_quantity = quant.reserved_quantity
            location = quant.location_id
            if reserved_quantity > 0.0 and location.usage in virtual_locations:
                raise ValidationError(
                    _(
                        "Invalid attempt to reserve product %s"
                        " for a location with usage %s."
                    )
                    % (
                        quant.product_id.display_name,
                        location.usage,
                    )
                )
            if location.usage != "internal":
                continue
            # Compare reserved quantity in quant with moves for the location.
            parameters = {
                "location_id": self.location_id.id,
                "product_id": self.product_id.id,
            }
            self.env.cr.execute(RESERVED_STATEMENT, parameters)
            reserved_in_moves = self.env.cr.fetchone()
            comparison = float_compare(
                reserved_quantity,
                reserved_in_moves,
                precision_digits=precision
            )
            if comparison == 0:
                continue
            # We detected a mismatch between moves and quants.
            raise ValidationError(
                _(
                    "Mismatch between reserved product quantity according to"
                    " quants %s and accourding to moves %s for product %s"
                    " in location %s."

                )
                % (
                    reserved_quantity,
                    reserved_in_moves,
                    quant.product_id.display_name,
                    location.complete_name,
                )
            )
