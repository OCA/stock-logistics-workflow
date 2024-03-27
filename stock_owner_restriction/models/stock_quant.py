# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# Copyright 2023 Quartile Limited
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
        restricted_owner = self.env.context.get("force_restricted_owner_id", None)
        if owner_id is None or restricted_owner is None:
            return records
        return records.filtered(
            lambda q: q.owner_id == (restricted_owner or self.env["res.partner"])
        )

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        owner_in_domain = any(t[0] == "owner_id" for t in domain)
        if not owner_in_domain:
            restricted_owner = self.env.context.get("force_restricted_owner_id", None)
            if restricted_owner is not None:
                domain = expression.AND(
                    [
                        domain,
                        [
                            (
                                "owner_id",
                                "=",
                                restricted_owner and restricted_owner.id or False,
                            )
                        ],
                    ]
                )
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
        restricted_owner = self.env.context.get("force_restricted_owner_id", None)
        if not owner_id and restricted_owner is not None:
            owner_id = restricted_owner
        return super()._get_available_quantity(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            allow_negative=allow_negative,
        )

    @api.model
    def _update_available_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        in_date=None,
    ):
        restricted_owner = self.env.context.get("force_restricted_owner_id", None)
        if not owner_id and restricted_owner is not None:
            owner_id = restricted_owner
        return super()._update_available_quantity(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            in_date=in_date,
        )

    @api.model
    def _update_reserved_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        restricted_owner = self.env.context.get("force_restricted_owner_id", None)
        if not owner_id and restricted_owner is not None:
            owner_id = restricted_owner
        return super()._update_reserved_quantity(
            product_id,
            location_id,
            quantity,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
