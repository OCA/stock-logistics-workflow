# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_show_line_note_picking_report = fields.Boolean(
        "Display line notes in picking operations report",
        implied_group="sale_purchase_stock_line_note.group_show_line_note_picking_report",
        default=False,
    )
