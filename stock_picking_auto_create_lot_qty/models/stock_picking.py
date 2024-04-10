# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _split_stock_move_lines(self, pickings):
        """
        Split stock move lines into existing and new lines.
        This method separates stock move lines into existing and new lines based on
        specific criteria and optionally creates automatic lot numbers.
        Args:
            pickings (recordset): Recordset of stock pickings for which to retrieve
                                  stock move lines
        Returns:
            tuple (existing_lines, new_lines): A tuple containing two recordsets:
                 - existing_lines: Existing stock move lines associated with the pickings.
                 - new_lines: New stock move lines that need to be created.
        """
        existing_lines = self.env["stock.move.line"].browse()
        new_lines = self.env["stock.move.line"].browse()
        for line in pickings.mapped("move_line_ids"):
            if (
                not line.lot_id
                and not line.lot_name
                and line.product_id.tracking != "none"
                and line.product_id.auto_create_lot
            ):
                existing_lines |= line
            if line.qty_done:
                new_lines |= line
        return existing_lines, new_lines

    @api.model
    def _create_multiple_stock_move_lines_for_lots(
        self, count_of_lots, line, product, every_n
    ):
        """
        Create multiple stock move lines for generating lots.
        Args:
            count_of_lots (int): Number of lots to generate.
            line (stock.move.line): Stock move line to use as a template.
            product (product.product): Product for which lots are generated.
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
                    "product_uom_id": product.batch_uom_id.id or product.uom_id.id,
                    "product_id": product.id,
                }
            )
            new_lines |= new_line
        return new_lines

    @api.model
    def _prepare_stock_move_lines_for_lots(self, product, line, current_product_qty):
        """
        Prepare stock move lines representing generated lots for a product.
        This method is responsible for preparing stock move lines that
        represent the lots generated for a specific product based on
        the product's configuration and the provided quantity.
        Args:
            product (product.product): Product for which lots are generated.
            line (stock.move.line): Stock move line to use as a template.
            current_product_qty (int): Quantity of the product to generate lots for.
        Returns:
            lines (recordset): A set of new stock move lines representing the
                                   generated lots.
        """
        every_n = product.product_tmpl_id.create_lot_every_n
        if every_n == 0 or current_product_qty == 0:
            raise ValidationError(
                _("The qty create lot every n and product qty must be greater than 0")
            )
        lines = self.env["stock.move.line"].browse()
        count_of_lots = int(current_product_qty // every_n)
        lines |= self._create_multiple_stock_move_lines_for_lots(
            count_of_lots, line, product, every_n
        )
        remainder = current_product_qty - (count_of_lots * every_n)
        if product.only_multiples_allowed and remainder > 0:
            raise UserError(
                _(
                    "The quantity received for the product does"
                    " not allow for automatic lot creation"
                )
            )
        if remainder > 0:
            lines |= self._create_multiple_stock_move_lines_for_lots(
                1, line, product, remainder
            )
        return lines

    def _set_auto_lot(self):
        """
        Create new lots for stock move lines based on product settings.
        """
        pickings = self.filtered(lambda p: p.picking_type_id.auto_create_lot)
        immediate_pickings = self.filtered(lambda p: p.immediate_transfer)
        lines, new_lines = self._split_stock_move_lines(pickings)
        if immediate_pickings and lines:
            return self._create_lots_for_immediate_pickings(lines)
        if new_lines or not lines:
            return
        for line in lines:
            product_id = line.product_id

            if product_id.create_lot_every_n:
                product_qty = line.reserved_uom_qty
                current_product_qty = product_id.uom_id._compute_quantity(
                    product_qty,
                    product_id.batch_uom_id or product_id.uom_id,
                    round=False,
                )
                new_lines |= self._prepare_stock_move_lines_for_lots(
                    product_id, line, current_product_qty
                )
            else:
                new_lines |= line

        self._set_lotname(new_lines)

    @api.model
    def _create_lots_for_immediate_pickings(self, lines):
        """
        Create stock move lines for immediate pickings,
        handling products that require lot creation.

        Args:
            lines (stock.move.line): A recordset of stock move lines to process.
        """
        new_lines = self.env["stock.move.line"].browse()
        old_lines = self.env["stock.move.line"].browse()
        for line in lines:
            product_id = line.product_id

            if product_id.create_lot_every_n:
                product_qty = line.reserved_uom_qty
                current_product_qty = product_id.uom_id._compute_quantity(
                    product_qty,
                    product_id.batch_uom_id or product_id.uom_id,
                    round=False,
                )
                old_lines |= line
                new_lines |= self._prepare_stock_move_lines_for_lots(
                    product_id, line, current_product_qty
                )
            else:
                new_lines |= line
        old_lines.update({"qty_done": 0})
        self._set_lotname(new_lines)

    @api.model
    def _set_lotname(self, lines):
        """
        Set the lot name for each stock move line in the provided recordset.

        Args:
            lines (stock.move.line): A recordset of stock move lines to update with lot names.
        """
        for line in lines:
            line.lot_name = line._get_lot_sequence()
