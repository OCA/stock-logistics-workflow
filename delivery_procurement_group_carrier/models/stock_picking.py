# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _align_group_carrier(self):
        for picking in self:
            picking_carrier = picking.carrier_id
            picking_group = picking.group_id
            if picking_group and picking_carrier != picking_group.carrier_id:
                picking_group.carrier_id = picking_carrier
                need_align_pickings = self.search(
                    [
                        ("group_id", "=", picking_group.id),
                        (
                            "state",
                            "not in",
                            (
                                "done",
                                "cancel",
                            ),
                        ),
                        ("carrier_id", "!=", picking_carrier.id),
                        ("carrier_id", "!=", False),
                    ]
                )
                need_align_pickings.carrier_id = picking_carrier

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
        updated_pickings._align_group_carrier()
        return res
