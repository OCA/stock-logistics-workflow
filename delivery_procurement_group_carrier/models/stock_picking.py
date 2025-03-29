# Copyright 2025 Camptocamp SA
# Copyright 2025 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.tools import groupby


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _align_group_carrier(self):
        for group, pickings in groupby(self, lambda pick: pick.group_id):
            if not group:
                continue
            pickings = self.browse().union(*pickings)
            carrier = pickings.carrier_id
            carrier.ensure_one()
            need_align_pickings = self.search(
                [
                    ("group_id", "=", group.id),
                    (
                        "state",
                        "not in",
                        (
                            "done",
                            "cancel",
                        ),
                    ),
                    ("carrier_id", "!=", carrier.id),
                    ("carrier_id", "!=", False),
                ]
            )
            group.carrier_id = carrier
            if need_align_pickings:
                need_align_pickings.carrier_id = carrier

    def write(self, values):
        if "carrier_id" not in values or self.env.context.get(
            "skip_align_group_carrier"
        ):
            # We only track when carrier changes. Avoid useless computation when
            # carrier_id isn't in values
            return super().write(values)
        carrier_mapping = {record.id: record.carrier_id for record in self}
        res = super().write(values)
        # Align group on pickings where carrier was updated
        updated_pickings = self.filtered(
            lambda p: p.carrier_id != carrier_mapping.get(p.id)
        )
        if updated_pickings:
            updated_pickings._align_group_carrier()
        return res
