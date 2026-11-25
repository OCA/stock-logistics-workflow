# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class StockLotStage(models.Model):
    _name = "stock.lot.stage"
    _description = "Lot Stage"
    _order = "sequence, name"
    _sql_constraints = [
        (
            "name_unique",
            "unique(name, active)",
            "Stage name must be unique!",
        ),
    ]

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    locked = fields.Boolean(
        help="If checked, lots in this stage are locked for use.",
    )
    approve_full_qty = fields.Boolean(
        help="If checked, lots in this stage are fully approved "
        "and cannot have partial quantities. "
        "Only available for unlocked stages.",
    )
    fold = fields.Boolean(
        help="If checked, this stage will be folded in kanban views.",
    )
    active = fields.Boolean(default=True)

    @api.constrains("approve_full_qty", "locked")
    def _check_approve_full_qty(self):
        """Full approval can only be set on unlocked stages."""
        for stage in self:
            if stage.approve_full_qty and stage.locked:
                raise exceptions.ValidationError(
                    _("Full approval can only be allowed on unlocked stages.")
                )
