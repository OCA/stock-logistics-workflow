# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class WeighingWizard(models.TransientModel):
    _inherit = "weighing.wizard"

    measure_device_id = fields.Many2one(
        comodel_name="remote.measure.device",
        default=lambda self: self.env.user.remote_measure_device_id,
        readonly=True,
    )
    uom_id = fields.Many2one(comodel_name="uom.uom", related="measure_device_id.uom_id")
