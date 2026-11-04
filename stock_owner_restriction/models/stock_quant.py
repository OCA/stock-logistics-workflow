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
        records = super()._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=self._get_restriction_owner_id(location_id, owner_id),
            strict=strict,
            qty=qty,
        )
        restricted_owner_id = self.env.context.get("force_restricted_owner_id", None)
        if restricted_owner_id is None:
            # Don't gate on `owner_id`: some core callers (e.g.
            # _set_quantity_done) reach here with a plain None without ever
            # going through _action_assign.
            return records
        return records.filtered(
            lambda q: q.owner_id == (restricted_owner_id or self.env["res.partner"])
        )

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
            # The context value can be a res.partner recordset (set by
            # stock.move._action_assign) or an id; domains do not accept
            # recordset values.
            if isinstance(restricted_owner_id, models.BaseModel):
                restricted_owner_id = restricted_owner_id.id
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
