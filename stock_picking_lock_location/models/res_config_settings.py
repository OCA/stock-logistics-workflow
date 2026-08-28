# Copyright (C) 2026 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    lock_location_id = fields.Boolean(
        related="company_id.lock_location_id",
        string="Lock Source Location",
        readonly=False,
        help="Check the box if you want to enable the lock_location_id "
        "field on operations types",
    )
    lock_location_dest_id = fields.Boolean(
        related="company_id.lock_location_dest_id",
        string="Lock Destination Location",
        readonly=False,
        help="Check the box if you want to enable the lock_location_dest_id "
        "field on operations types",
    )
