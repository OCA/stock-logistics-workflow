# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    quant_lock_quant_id = fields.Many2one(
        comodel_name="stock.quant",
        string="Locked quant",
        copy=False,
        index=True,
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        fields = super()._prepare_merge_moves_distinct_fields()
        # Never merge moves with different locked quants.
        fields.append("quant_lock_quant_id")
        return fields

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
        if self.quant_lock_quant_id:
            # Force the reservation to be done on the locked quant and not any other
            # available quant with the same characteristics.
            quant = self.quant_lock_quant_id
            lot_id = quant.lot_id
            package_id = quant.package_id
            owner_id = quant.owner_id
            strict = True
            available_quantity = quant.available_quantity
            return super(
                StockMove,
                self.with_context(force_quant_lock_quant_id=quant.id),
            )._update_reserved_quantity(
                need,
                available_quantity,
                location_id,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
