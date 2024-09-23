# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Operating Hours Calendar",
    )
