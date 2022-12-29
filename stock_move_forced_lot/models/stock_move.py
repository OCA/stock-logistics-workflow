# Copyright 2022 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    forced_lot_id = fields.Many2one("stock.production.lot")

    def _get_available_quantity(
        self,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        if not lot_id and self.forced_lot_id and self.location_id.usage == "internal":
            lot_id = self.forced_lot_id
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
        if not lot_id and self.forced_lot_id and self.location_id.usage == "internal":
            lot_id = self.forced_lot_id
        return super()._update_reserved_quantity(
            need,
            available_quantity,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        res = super()._prepare_merge_moves_distinct_fields()
        return res + ["forced_lot_id"]
