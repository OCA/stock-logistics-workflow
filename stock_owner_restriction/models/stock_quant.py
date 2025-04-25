# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.osv import expression


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _get_restriction_owner_id(self, location_id, owner_id):
        """Hook to allow modify the owner of quants to gather.
        By default prevent a negative quant from being created with owner instead of
        reducing the original quant when a return is made by assigning owner.
        """
        return owner_id if location_id.usage != "customer" else self.env["res.partner"]

    def _gather(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        qty=0,
    ):
        owner_for_super = self._get_restriction_owner_id(location_id, owner_id)

        gather_args = {
            "product_id": product_id,
            "location_id": location_id,
            "lot_id": lot_id,
            "package_id": package_id,
            "owner_id": owner_for_super,
            "strict": strict,
        }
        if "qty" in super()._gather.__code__.co_varnames:
            gather_args["qty"] = qty
        records = super()._gather(**gather_args)

        restricted_owner_id_ctx = self.env.context.get(
            "force_restricted_owner_id", None
        )
        if restricted_owner_id_ctx is not None:
            if isinstance(restricted_owner_id_ctx, int):
                records = records.filtered(
                    lambda q: q.owner_id.id == restricted_owner_id_ctx
                )
            elif restricted_owner_id_ctx is False:
                records = records.filtered(lambda q: not q.owner_id)

        return records

    @api.model
    def _read_group(
        self,
        domain,
        groupby=(),
        aggregates=(),
        having=(),
        offset=0,
        limit=None,
        order=None,
    ):
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if restricted_owner_id is not None:
            domain = expression.AND([domain, [("owner_id", "=", restricted_owner_id)]])
        return super()._read_group(
            domain,
            groupby=groupby,
            aggregates=aggregates,
            having=having,
            offset=offset,
            limit=limit,
            order=order,
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
        restricted_owner_id_ctx = self.env.context.get(
            "force_restricted_owner_id", None
        )
        owner_arg_for_super = owner_id

        if owner_arg_for_super is None and restricted_owner_id_ctx is not None:
            if isinstance(restricted_owner_id_ctx, int):
                owner_recordset = self.env["res.partner"].browse(
                    restricted_owner_id_ctx
                )
                owner_arg_for_super = (
                    owner_recordset if owner_recordset.exists() else False
                )
            elif restricted_owner_id_ctx is False:
                owner_arg_for_super = False

        return super()._get_available_quantity(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_arg_for_super,
            strict=strict,
            allow_negative=allow_negative,
        )
