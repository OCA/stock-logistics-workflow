# Copyright (C) 2026 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    lock_location_id = fields.Boolean(
        string="Lock Source Location",
        help="Check the box if you want to enable the Lock Source Location "
        "field on operations types",
    )
    lock_location_dest_id = fields.Boolean(
        string="Lock Destination Location",
        help="Check the box if you want to enable the Lock Destination Location "
        "field on operations types",
    )
