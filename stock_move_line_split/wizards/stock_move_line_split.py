# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class StockMoveLineSplit(models.TransientModel):
    _name = "stock.move.line.split"
    _description = "Split Stock Move Lines"

    move_line_ids = fields.Many2many(
        "stock.move.line",
        string="Move Lines to Split",
    )
    strategy = fields.Selection(
        [
            ("fixed", "Fixed quantity per line"),
            ("weight", "Maximum weight per line"),
        ],
        string="Split Strategy",
        required=True,
        default="fixed",
    )
    fixed_qty = fields.Float(
        string="Qty per Line",
        digits="Product Unit of Measure",
        default=1.0,
    )
    weight_source = fields.Selection(
        [
            ("custom", "Custom weight"),
            ("package_type", "Package type"),
        ],
        string="Max Weight From",
        required=True,
        default="custom",
    )
    package_type_id = fields.Many2one(
        "stock.package.type",
        string="Package Type",
    )
    package_type_available_weight = fields.Float(
        string="Available Weight",
        compute="_compute_package_type_available_weight",
    )
    max_weight = fields.Float(string="Max Weight per Line")
    weight_uom_name = fields.Char(compute="_compute_weight_uom_name")

    @api.depends("package_type_id.max_weight", "package_type_id.base_weight")
    def _compute_package_type_available_weight(self):
        for wizard in self:
            package_type = wizard.package_type_id
            av_weight = 0.0
            if package_type:
                av_weight = package_type.max_weight - package_type.base_weight
            wizard.package_type_available_weight = max(0.0, av_weight)

    def _compute_weight_uom_name(self):
        name = self.env[
            "product.template"
        ]._get_weight_uom_name_from_ir_config_parameter()
        for wizard in self:
            wizard.weight_uom_name = name

    def _get_max_weight(self):
        self.ensure_one()
        weight_uom = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()
        rounding = weight_uom.rounding
        if self.weight_source == "package_type":
            p_type = self.package_type_id
            if not p_type:
                raise UserError(self.env._("Please select a package type."))
            max_weight = p_type.max_weight - p_type.base_weight
            if float_compare(max_weight, 0, precision_rounding=rounding) <= 0:
                raise UserError(
                    self.env._(
                        "The available weight of package type %(package_type)s "
                        "(max weight - base weight) must be greater than zero.",
                        package_type=p_type.display_name,
                    )
                )
            return max_weight
        if float_compare(self.max_weight, 0, precision_rounding=rounding) <= 0:
            raise UserError(
                self.env._("Please set a maximum weight greater than zero.")
            )
        return self.max_weight

    def _get_split_size(self, move_line):
        self.ensure_one()
        method = getattr(self, f"_get_split_size_{self.strategy}", None)
        if method is None:
            raise UserError(
                self.env._(
                    "No split-size method defined for strategy %(strategy)s.",
                    strategy=self.strategy,
                )
            )
        return method(move_line)

    def _get_split_size_fixed(self, move_line):
        self.ensure_one()
        rounding = move_line.product_uom_id.rounding
        if float_compare(self.fixed_qty, 0, precision_rounding=rounding) <= 0:
            raise UserError(self.env._("The split quantity must be greater than zero."))
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        round_fixed_qty = float_round(self.fixed_qty, precision_rounding=rounding)
        if (
            float_compare(
                self.fixed_qty,
                round_fixed_qty,
                precision_digits=precision,
            )
            != 0
        ):
            raise UserError(
                self.env._(
                    "The split quantity %(qty)s does not respect the "
                    "rounding of unit of measure %(uom)s.",
                    qty=self.fixed_qty,
                    uom=move_line.product_uom_id.display_name,
                )
            )
        return self.fixed_qty

    def _get_split_size_weight(self, move_line):
        self.ensure_one()
        product = move_line.product_id
        weight_uom = self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()
        max_weight = self._get_max_weight()
        if float_is_zero(product.weight, precision_rounding=weight_uom.rounding):
            raise UserError(
                self.env._(
                    "Product %(product)s has no weight defined, so it cannot be "
                    "split by weight.",
                    product=product.display_name,
                )
            )
        decimal_units = max_weight / product.weight
        units = float_round(
            decimal_units, precision_rounding=1.0, rounding_method="DOWN"
        )
        if units < 1:
            raise UserError(
                self.env._(
                    "A single unit of %(product)s exceeds the maximum weight, "
                    "so it cannot be split by weight.",
                    product=product.display_name,
                )
            )
        return product.uom_id._compute_quantity(units, move_line.product_uom_id)

    def _get_chunk_sizes(self, move_line):
        self.ensure_one()
        rounding = move_line.product_uom_id.rounding
        total = move_line.quantity
        size = self._get_split_size(move_line)
        if float_compare(size, 0, precision_rounding=rounding) <= 0:
            raise UserError(self.env._("The split quantity must be greater than zero."))
        chunks = []
        remaining = total
        while float_compare(remaining, 0, precision_rounding=rounding) > 0:
            chunk = min(size, remaining)
            chunks.append(chunk)
            remaining = max(
                0, float_round(remaining - chunk, precision_rounding=rounding)
            )
        return chunks

    def action_apply(self):
        self.ensure_one()
        if not self.move_line_ids:
            raise UserError(self.env._("There are no move lines to split."))
        for move_line in self.move_line_ids:
            move_line._check_can_split()
        for move_line in self.move_line_ids:
            move_line._split_quantity(self._get_chunk_sizes(move_line))
        return {"type": "ir.actions.act_window_close"}
