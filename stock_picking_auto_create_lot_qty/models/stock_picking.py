# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _set_auto_lot(self):
        """
        Allows to be called either by button or through code
        """
        pickings = self.filtered(lambda p: p.picking_type_id.auto_create_lot)
        lines = pickings.mapped("move_line_ids").filtered(
            lambda x: (
                not x.lot_id
                and not x.lot_name
                and x.product_id.tracking != "none"
                and x.product_id.auto_create_lot
            )
        )
        new_lines = pickings.mapped("move_line_ids").filtered(lambda x: x.qty_done)
        if not new_lines:
            count_by_product = dict.fromkeys(lines.mapped("product_id"), 0)
            for line in lines:
                count_by_product[line.product_id] += line.reserved_uom_qty
            for product_id, product_qty in count_by_product.items():
                current_product_qty = product_id.uom_id._compute_quantity(
                    product_qty,
                    product_id.batch_uom_id or product_id.uom_id,
                    round=False,
                )
                if product_id.create_lot_every_n:
                    every_n = product_id.product_tmpl_id.create_lot_every_n

                    count_of_lots = int(current_product_qty // every_n)
                    for _new_line_count in range(count_of_lots):
                        new_line = line.copy()
                        new_line.update(
                            {
                                "qty_done": every_n,
                                "product_uom_id": product_id.batch_uom_id
                                or product_id.uom_id,
                            }
                        )
                        new_lines += new_line
                    remainder = current_product_qty - (count_of_lots * every_n)
                    if product_id.only_multiples_allowed and remainder > 0:
                        raise UserError(
                            _(
                                "The quantity received for the product does"
                                " not allow for automatic lot creation"
                            )
                        )
                    if remainder > 0:
                        new_line = line.copy()
                        new_line.update(
                            {
                                "qty_done": remainder,
                                "product_uom_id": product_id.batch_uom_id
                                or product_id.uom_id,
                            }
                        )
                        new_lines += new_line
                else:
                    new_lines += line
            new_lines.set_lot_auto()
