# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    origin_reference = fields.Reference(
        selection="_selection_origin_reference",
        compute="_compute_origin_reference",
        string="Source Document",
    )

    def _selection_origin_reference(self):
        return [("stock.picking", "Transfer")]

    @api.model
    def _get_depends_compute_origin_reference(self):
        return ["origin"]

    @api.depends(lambda x: x._get_depends_compute_origin_reference())
    def _compute_origin_reference(self):
        for picking in self:
            origin_reference = False
            rel_picking = self.search([("name", "=", picking.origin)], limit=1)
            if rel_picking:
                origin_reference = "%s,%s" % (self._name, rel_picking.id)
            picking.origin_reference = origin_reference
