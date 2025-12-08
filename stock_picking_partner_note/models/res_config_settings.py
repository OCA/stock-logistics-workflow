# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    check_note_already_in_use = fields.Boolean(
        related="company_id.check_note_already_in_use",
        readonly=False,
        help="Prevent the update or deletion of a note that is already in use by "
        "more than one contact.",
    )
