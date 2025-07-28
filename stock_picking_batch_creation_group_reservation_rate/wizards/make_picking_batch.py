# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND


class MakePickingBatch(models.TransientModel):
    _inherit = "make.picking.batch"

    group_reservation_rate = fields.Boolean(
        help="Check this if you want to use reservation rate range"
    )
    group_reservation_rate_min = fields.Float(default=0.0)
    group_reservation_rate_max = fields.Float(default=100.0)

    @api.constrains("group_reservation_rate_max", "group_reservation_rate_min")
    def _check_group_reservation_rate(self):
        for batch in self:
            if batch.group_reservation_rate and (
                batch.group_reservation_rate_max < batch.group_reservation_rate_min
            ):
                raise ValidationError(
                    _(
                        "The maximum reservation rate should not be below the minimum "
                        "reservation rate!"
                    )
                )
            if (
                batch.group_reservation_rate_min < 0
                or batch.group_reservation_rate_min > 100
            ):
                raise ValidationError(
                    _("The minimum reservation rate should be between 0 and 100!")
                )
            if (
                batch.group_reservation_rate_max < 0
                or batch.group_reservation_rate_max > 100
            ):
                raise ValidationError(
                    _("The maximum reservation rate should be between 0 and 100!")
                )

    def _get_picking_domain_for_group_reservation_rate(self):
        """
        Adds the delivery carrier in criteria for pickings selection
        """
        self.ensure_one()
        return [
            ("type_group_reservation_rate", ">=", self.group_reservation_rate_min),
            ("type_group_reservation_rate", "<=", self.group_reservation_rate_max),
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
        return domain

    def _get_picking_domain_for_first(self, no_nbr_lines_limit=False):
        domain = super()._get_picking_domain_for_first(
            no_nbr_lines_limit=no_nbr_lines_limit
        )
        if self.group_reservation_rate:
            domain = AND(
                [domain, self._get_picking_domain_for_group_reservation_rate()]
            )
        return domain
