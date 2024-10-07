# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_calendar_id = fields.Many2one(
        "resource.calendar",
        string="Supplier Calendar",
        help="This calendar will be used to manage the availability of the supplier",
    )
