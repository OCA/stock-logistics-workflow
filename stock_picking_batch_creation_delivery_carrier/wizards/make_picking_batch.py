# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.osv.expression import AND


class MakePickingBatch(models.TransientModel):
    _inherit = "make.picking.batch"

    delivery_carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        help="Fill in this if you want to filter the "
        "selected pickings with a delivery carrier",
    )

    def _get_picking_domain_for_delivery_carrier(self, delivery_carrier=None):
        """
        Adds the delivery carrier in criteria for pickings selection
        """
        self.ensure_one()
        return [
            (
                "carrier_id",
                "=",
                delivery_carrier.id
                if delivery_carrier
                else self.delivery_carrier_id.id,
            )
        ]

    def _get_picking_domain_for_additional(self):
        domain = super()._get_picking_domain_for_additional()
        if self._first_picking.carrier_id:
            domain = AND(
                [
                    domain,
                    self._get_picking_domain_for_delivery_carrier(
                        delivery_carrier=self._first_picking.carrier_id
                    ),
                ]
            )
        return domain

    def _get_picking_domain_for_first(self, no_nbr_lines_limit=False):
        domain = super()._get_picking_domain_for_first()
        if self.delivery_carrier_id:
            domain = AND([domain, self._get_picking_domain_for_delivery_carrier()])
        return domain

    def _create_batch_values(self):
        self.ensure_one()
        values = super()._create_batch_values()
        if self.delivery_carrier_id:
            values.update(
                {
                    "delivery_carrier_id": self.delivery_carrier_id.id,
                }
            )
        return values
