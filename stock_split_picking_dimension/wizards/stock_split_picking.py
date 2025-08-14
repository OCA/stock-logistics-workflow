# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare

from ..exceptions import DimensionMustBePositiveError, DimensionRequiredError


class StockSplitPicking(models.TransientModel):
    _inherit = "stock.split.picking"

    mode = fields.Selection(
        selection_add=[
            ("dimensions", "By dimensions"),
        ],
        ondelete={"dimensions": "cascade"},
    )

    max_nbr_lines = fields.Integer(
        string="Max number of lines",
        default=0,
    )
    max_volume = fields.Float(
        default=0.0,
        help="Volume in default system volume unit of measure",
    )
    max_weight = fields.Float(
        default=0.0,
        help="Weight in default system weight unit of measure",
    )
    user_max_volume = fields.Float(
        string="Maximum total net volume",
        compute="_compute_user_max_volume",
        inverse="_inverse_user_max_volume",
        readonly=False,
    )
    user_max_weight = fields.Float(
        string="Maximum total net weight",
        compute="_compute_user_max_weight",
        inverse="_inverse_user_max_weight",
        readonly=False,
    )
    user_weight_uom_id = fields.Many2one(
        # Same as product.packing
        "uom.uom",
        string="Weight Units of Measure",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_kgm").id)
        ],
        help="Weight Unit of Measure",
        compute=False,
        default=lambda self: self._get_system_weight_uom(),
    )
    user_weight_uom_name = fields.Char(
        # Same as product.packing
        string="Weight unit of measure label",
        related="user_weight_uom_id.display_name",
        readonly=True,
    )
    user_volume_uom_id = fields.Many2one(
        # Same as product.packing
        "uom.uom",
        string="Volume Units of Measure",
        domain=lambda self: [
            ("category_id", "=", self.env.ref("uom.product_uom_categ_vol").id)
        ],
        help="Packaging volume unit of measure",
        default=lambda self: self._get_system_volume_uom(),
        required=True,
    )

    user_volume_uom_name = fields.Char(
        # Same as product.packing
        string="Volume Unit of Measure label",
        related="user_volume_uom_id.display_name",
        readonly=True,
        required=True,
    )

    @api.constrains("max_nbr_lines", "max_volume", "max_weight", "mode")
    def _check_dimensions(self):
        volume_uom = self._get_system_volume_uom()
        weight_uom = self._get_system_weight_uom()
        for rec in self:
            if not rec.mode == "dimensions":
                continue

            if (
                float_compare(
                    rec.max_volume, 0.0, precision_rounding=volume_uom.rounding
                )
                < 0
            ):
                raise DimensionMustBePositiveError(self.env, self._fields["max_volume"])

            if (
                float_compare(
                    rec.max_weight, 0.0, precision_rounding=weight_uom.rounding
                )
                < 0
            ):
                raise DimensionMustBePositiveError(self.env, self._fields["max_weight"])

            if rec.max_nbr_lines < 0:
                raise DimensionMustBePositiveError(
                    self.env, self._fields["max_nbr_lines"]
                )

            if (
                not rec.max_nbr_lines > 0
                and not float_compare(
                    rec.max_volume, 0.0, precision_rounding=volume_uom.rounding
                )
                > 0
                and not float_compare(
                    rec.max_weight, 0.0, precision_rounding=weight_uom.rounding
                )
                > 0
            ):
                raise DimensionRequiredError(self.env)

    @api.depends("max_volume", "user_volume_uom_id")
    def _compute_user_max_volume(self):
        volume_uom = self._get_system_volume_uom()
        for rec in self:
            rec.user_max_volume = volume_uom._compute_quantity(
                rec.max_volume, to_unit=rec.user_volume_uom_id
            )

    def _inverse_user_max_volume(self):
        volume_uom = self._get_system_volume_uom()
        for rec in self:
            rec.max_volume = rec.user_volume_uom_id._compute_quantity(
                rec.user_max_volume, to_unit=volume_uom
            )

    @api.depends("max_weight", "user_weight_uom_id")
    def _compute_user_max_weight(self):
        weight_uom = self._get_system_weight_uom()
        for rec in self:
            rec.user_max_weight = weight_uom._compute_quantity(
                rec.max_weight, to_unit=rec.user_weight_uom_id
            )

    def _inverse_user_max_weight(self):
        weight_uom = self._get_system_weight_uom()
        for rec in self:
            rec.max_weight = rec.user_weight_uom_id._compute_quantity(
                rec.user_max_weight, to_unit=weight_uom
            )

    @api.model
    def _get_system_volume_uom(self):
        return self.env[
            "product.template"
        ]._get_volume_uom_id_from_ir_config_parameter()

    @api.model
    def _get_system_weight_uom(self):
        return self.env[
            "product.template"
        ]._get_weight_uom_id_from_ir_config_parameter()

    def _apply_dimensions(self):
        """Apply mode `mode`: By dimensions

        Spit off moves lines if they fit in the user-defined dimensions.
        Keep the rest in the original picking.
        """
        volume_uom = self._get_system_volume_uom()
        weight_uom = self._get_system_weight_uom()
        new_pickings = self.env["stock.picking"]
        for picking in self.picking_ids:
            taken_nbr_lines = 0
            taken_volume = 0.0
            taken_weight = 0.0
            moves_to_split_off = self.env["stock.move"]
            for move in picking.move_ids:
                # Stop if we've reached the maximum number of lines, volume, or weight
                if (
                    (self.max_nbr_lines and taken_nbr_lines >= self.max_nbr_lines)
                    or (self.max_volume and taken_volume >= self.max_volume)
                    or (self.max_weight and taken_weight >= self.max_weight)
                ):
                    break
                # Do not split moves that are done or cancelled
                if move.state in ("done", "cancel"):
                    continue
                # If the move fits in the available dimensions, split it off
                move_weight = move.product_qty * move.product_id.weight
                move_volume = move.volume
                if (
                    not self.max_volume
                    or float_compare(
                        move_volume,
                        self.max_volume - taken_volume,
                        precision_rounding=volume_uom.rounding,
                    )
                    <= 0
                ) and (
                    not self.max_weight
                    or float_compare(
                        move_weight,
                        self.max_weight - taken_weight,
                        precision_rounding=weight_uom.rounding,
                    )
                    <= 0
                ):
                    moves_to_split_off += move
                    taken_nbr_lines += 1
                    taken_volume += move_volume
                    taken_weight += move_weight
                    continue
            # If all the picking moves are the ones to be split, then it means
            # we haven't created any backorder move. We keep the picking as-is.
            if picking.move_ids == moves_to_split_off or not moves_to_split_off:
                continue  # pragma: no cover
            # Create the split orders for the extracted moves, and split them off
            new_pickings += picking._split_off_moves(moves_to_split_off)
        return new_pickings
