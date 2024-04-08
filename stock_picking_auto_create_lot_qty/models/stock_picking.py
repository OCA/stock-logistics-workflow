# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_stock_move_lines(self, pickings):
        """Get stock move lines for the given pickings, and the new ones

        Args:
            pickings (recordset): Recordset of stock pickings for which to retrieve
                                  stock move lines

        Returns:
            tuple (lines, new_lines): A tuple containing two recordsets - lines and new_lines.
                 - lines: Existing stock move lines associated with the pickings.
                 - new_lines: New stock move lines that need to be created.

        """
        lines = new_lines = self.env["stock.move.line"].browse()
        for line in pickings.mapped("move_line_ids"):
            if (
                not line.lot_id
                and not line.lot_name
                and line.product_id.tracking != "none"
                and line.product_id.auto_create_lot
            ):
                lines |= line
            if line.qty_done:
                new_lines |= line
        return lines, new_lines

    @api.model
    def _generate_lots_stock_move_line(self, count_of_lots, line, product_id, every_n):
        """
        Generate new stock move lines for lots based on the given parameters.

        Args:
            count_of_lots (int): Number of lots to generate.
            line (stock.move.line): Stock move line to use as a template.
            product_id (product.product): Product for which lots are generated.
            every_n (int): Number of units of measure to generate a lot for.

        Returns:
            new_lines (recordset): List of new stock move lines generated.
        """
        new_lines = self.env["stock.move.line"].browse()
        for _count in range(count_of_lots):
            new_line = line.copy()
            new_line.update(
                {
                    "qty_done": every_n,
                    "product_uom_id": product_id.batch_uom_id or product_id.uom_id,
                }
            )
            new_lines |= new_line
        return new_lines

    @api.model
    def _compute_count_by_product(self, lines):
        """
        Compute the number of lots to generate for each product.

        Args:
            lines (recordset): List of stock move lines.

        Returns:
            count_by_product (dict): Dictionary with product IDs as keys and number of lots
                                    to generate as values.
        """
        count_by_product = dict.fromkeys(lines.mapped("product_id"), 0)
        for line in lines:
            count_by_product[line.product_id] += line.product_uom_qty
        return count_by_product

    @api.model
    def _generate_lot_every_n(self, product_id, line, current_product_qty):
        """
        Generate lots for a product every n units based on the product's configuration.

        Args:
            product_id (product.product): Product for which lots are generated.
            line (stock.move.line): Stock move line to use as a template.
            current_product_qty (int): Quantity of the product to generate lots for.

        Returns:
            lines (recordset): A set of new stock move lines representing the
                                   generated lots.
        """
        lines = self.env["stock.move.line"].browse()
        every_n = product_id.product_tmpl_id.create_lot_every_n
        count_of_lots = int(current_product_qty // every_n)
        lines |= self._generate_lots_stock_move_line(
            count_of_lots, line, product_id, every_n
        )
        remainder = current_product_qty - (count_of_lots * every_n)
        if product_id.only_multiples_allowed and remainder > 0:
            raise UserError(
                _(
                    "The quantity received for the product does"
                    " not allow for automatic lot creation"
                )
            )
        if remainder > 0:
            lines |= self._generate_lots_stock_move_line(1, line, product_id, remainder)
        return lines

    def _set_auto_lot(self):
        """
        Allows to be called either by button or through code
        """
        pickings = self.filtered(lambda p: p.picking_type_id.auto_create_lot)
        lines, new_lines = self._get_stock_move_lines(pickings)
        if new_lines:
            return
        count_by_product = self._compute_count_by_product(lines)
        line = lines[0] if lines else None
        for product_id, product_qty in count_by_product.items():
            current_product_qty = product_id.uom_id._compute_quantity(
                product_qty,
                product_id.batch_uom_id or product_id.uom_id,
                round=False,
            )
            if product_id.create_lot_every_n:
                new_lines |= self._generate_lot_every_n(
                    product_id, line, current_product_qty
                )
            else:
                new_lines |= line
        new_lines.set_lot_auto()
