# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.osv.expression import AND


class MakePickingBatch(models.TransientModel):
    _inherit = "make.picking.batch"

    def _get_picking_domain_for_group_reservation_rate(self):
        """
        Adds the delivery carrier in criteria for pickings selection
        """
        self.ensure_one()
        return [
            ("type_group_reservation_rate", ">=", self.group_reservation_rate_min),
            ("type_group_reservation_rate", "<=", self.group_reservation_rate_max),
        ]

    def _get_picking_domain_for_group_additional_reservation_rate(self):
        """
        Adds the delivery carrier in criteria for pickings selection
        """
        self.ensure_one()
        return [
            (
                "additional_type_group_reservation_rate",
                ">=",
                self.additional_group_reservation_rate_min,
            ),
            (
                "additional_type_group_reservation_rate",
                "<=",
                self.additional_group_reservation_rate_max,
            ),
        ]

    def _get_picking_domain_for_additional(self):
        domain = super()._get_picking_domain_for_additional()
        if self.group_reservation_rate:
            domain = AND(
                [
                    domain,
                    self._get_picking_domain_for_group_reservation_rate(),
                ]
            )
        if self.additional_group_reservation_rate:
            domain = AND(
                [
                    domain,
                    self._get_picking_domain_for_group_reservation_rate(),
                ]
            )
        return domain

    def _get_picking_domain_for_first(self, no_nbr_lines_limit=False):
        domain = super()._get_picking_domain_for_first(
            no_nbr_lines_limit=no_nbr_lines_limit
        )
        if self.group_reservation_rate:
            domain = AND(
                [domain, self._get_picking_domain_for_group_reservation_rate()]
            )
        if self.additional_group_reservation_rate:
            domain = AND(
                [
                    domain,
                    self._get_picking_domain_for_group_additional_reservation_rate(),
                ]
            )
        return domain
