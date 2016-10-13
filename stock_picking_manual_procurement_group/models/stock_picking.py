# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    create_procurement_group = fields.Boolean(
        string="Create Procurement Group",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
                ],
            }
        )

    @api.multi
    def action_confirm(self):
        for res in self:
            if res.create_procurement_group:
                data = {
                    "name": res.name,
                    "move_type": res.move_type,
                    }
                group = self.env[
                    "procurement.group"].create(data)
                res.write({
                    "group_id": group.id})
        return super(StockPicking, self).action_confirm()
