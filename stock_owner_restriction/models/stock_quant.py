# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.osv import expression


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _gather(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        records = super()._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if owner_id is None or restricted_owner_id is None:
            return records
        return records.filtered(
            lambda q: q.owner_id == (restricted_owner_id or self.env["res.partner"])
        )

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if restricted_owner_id is not None:
            domain = expression.AND([domain, [("owner_id", "=", restricted_owner_id)]])
        return super(StockQuant, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )

    @api.model
    def _get_available_quantity(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        allow_negative=False,
    ):
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if not owner_id and restricted_owner_id is not None:
            owner_id = restricted_owner_id
        return super()._get_available_quantity(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )
