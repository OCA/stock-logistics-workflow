# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api
from odoo.models import Model
from odoo.osv import expression


class StockPicking(Model):
    _inherit = "stock.picking"

    @api.model
    def check_assign_all(self, domain=None, batch_size=False, company=None):
        """Try to assign confirmed pickings"""
        if not batch_size:
            batch_size = 1000
        move_assign_domain = self.env["procurement.group"]._get_moves_to_assign_domain(
            company
        )
        if domain:
            move_assign_domain = expression.AND([domain, move_assign_domain])

        moves_to_assign = self.env["stock.move"].search(
            move_assign_domain,
            limit=None,
            order="reservation_date, priority desc, date asc, id asc",
        )
        total_items = len(moves_to_assign)
        for i in range(0, total_items, batch_size):
            batch = moves_to_assign[i : i + batch_size]
            self.env["stock.move"].browse(batch.ids).sudo()._action_assign()

    def action_immediate_transfer_wizard(self):
        view = self.env.ref("stock.view_immediate_transfer")
        wiz = self.env["stock.immediate.transfer"].create(
            {
                "pick_ids": [(4, p.id) for p in self],
                "immediate_transfer_line_ids": [
                    (0, 0, {"to_immediate": True, "picking_id": p.id}) for p in self
                ],
            }
        )
        return {
            "name": _("Immediate Transfer?"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.immediate.transfer",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": wiz.id,
            "context": self.env.context,
        }
