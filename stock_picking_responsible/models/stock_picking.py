# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    responsible_id = fields.Many2one(
        comodel_name="res.partner",
        string="Responsible",
        default=lambda self: self.env.user.partner_id.id,
    )

    @api.multi
    def _add_follower(self):
        responsible_picking_ids = self.filtered("responsible_id")
        if responsible_picking_ids:
            discussion_subtype = self.env.ref("mail.mt_comment")
            picking_subtypes = self.env["mail.message.subtype"].search(
                [
                    ("res_model", "=", "stock.picking"),
                ]
            )
            subtypes = discussion_subtype | picking_subtypes

            for picking in responsible_picking_ids:
                picking.message_subscribe(
                    partner_ids=picking.responsible_id.ids, subtype_ids=subtypes.ids
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
