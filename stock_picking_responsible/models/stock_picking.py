# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    responsible = fields.Many2one(
        comodel_name="res.partner",
        string="Responsible",
        default=lambda self: self.env.user.partner_id.id,
    )

    @api.multi
    def _add_follower(self):
        for picking in self:
            if picking.responsible:
                types = self.env["mail.message.subtype"].search(
                    [
                        "|",
                        ("res_model", "=", "stock.picking"),
                        ("name", "=", "Discussions"),
                    ]
                )
                picking.message_subscribe(
                    partner_ids=picking.responsible.ids, subtype_ids=types.ids
                )

    @api.multi
    def write(self, values):
        res = super(StockPicking, self).write(values)
        self._add_follower()
        return res

    @api.model
    def create(self, values):
        picking = super(StockPicking, self).create(values)
        picking._add_follower()
        return picking
