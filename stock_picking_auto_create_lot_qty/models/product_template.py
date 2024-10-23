# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    batch_uom_id = fields.Many2one(
        string="Uom",
        help="The unit of measure used when creating batches.",
        comodel_name="uom.uom",
    )

    main_uom_category_id = fields.Many2one(
        string="UoM category",
        help="UoM category",
        comodel_name="uom.category",
        related="uom_id.category_id",
    )

    create_lot_every_n = fields.Integer(
        string="Create lot every",
        help="Create lot every n uom - here user can"
        " set a value and select one of the UoMs available"
        " for purchase (if value = 0, behavior stays the"
        " same as base module)",
        compute="_compute_create_lot_every_n",
        readonly=False,
        store=True,
    )

    only_multiples_allowed = fields.Boolean(
        string="Only multiples allowed",
        help="Blocks automatic creation of lots if quantity"
        " received is not a multiple of the selected value",
    )

    @api.depends("tracking")
    def _compute_create_lot_every_n(self):
        for rec in self:
            if rec.tracking != "lot":
                rec.create_lot_every_n = False
            else:
                rec.create_lot_every_n = rec.create_lot_every_n
