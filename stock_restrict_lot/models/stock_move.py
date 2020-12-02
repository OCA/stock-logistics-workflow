# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, exceptions, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    restrict_lot_id = fields.Many2one("stock.production.lot", string="Restrict Lot")

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        vals["restrict_lot_id"] = self.restrict_lot_id.id
        return vals

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        vals = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if self.restrict_lot_id:
            if "lot_id" in vals and vals["lot_id"] != self.restrict_lot_id.id:
                raise exceptions.UserError(
                    _(
                        "Inconsistencies between reserved quant and lot restriction on "
                        "stock move"
                    )
                )
            vals["lot_id"] = self.restrict_lot_id.id
        return vals

    def _get_available_quantity(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        self.ensure_one()
        if not lot_id and self.restrict_lot_id:
            lot_id = self.restrict_lot_id
        return super()._get_available_quantity(
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )

    def _update_reserved_quantity(
        self,
        need,
        available_quantity,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=True,
    ):
        self.ensure_one()
        if self.restrict_lot_id:
            lot_id = self.restrict_lot_id
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
