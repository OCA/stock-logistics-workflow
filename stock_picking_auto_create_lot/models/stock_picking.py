# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models
from odoo.osv import expression


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_auto_lot_domain(self, immediate=False):
        """Prepare the domain to search for stock.move.line records that require
        automatic lot assignment.
        The 'immediate' parameter influences the inclusion of 'qty_done' in the search criteria,
        depending on whether the transfer is immediate or planned.
        """
        domain = [
            ("picking_id", "in", self.ids),
            ("lot_id", "=", False),
            ("lot_name", "=", False),
            ("product_id.tracking", "!=", "none"),
            ("product_id.auto_create_lot", "=", True),
        ]
        if not immediate:
            domain = expression.AND([domain, [("qty_done", ">", 0)]])
        return domain

    def _set_auto_lot(self):
        """
        Allows to be called either by button or through code.
        """
        lines_to_set = self.env["stock.move.line"]
        pickings = self.filtered(lambda p: p.picking_type_id.auto_create_lot)
        if not pickings:
            return
        immediate_domain = []
        planned_domain = []
        immediate_pickings = pickings._check_immediate()
        if immediate_pickings:
            immediate_domain = immediate_pickings._prepare_auto_lot_domain(
                immediate=True
            )
        planned_pickings = pickings - immediate_pickings
        if planned_pickings:
            planned_domain = planned_pickings._prepare_auto_lot_domain()
        domain = expression.OR([immediate_domain, planned_domain])
        lines_to_set = lines_to_set.search(domain)
        for line in lines_to_set:
            line.lot_name = line._get_lot_sequence()

    def _action_done(self):
        self._set_auto_lot()
        return super()._action_done()

    def button_validate(self):
        self._set_auto_lot()
        return super().button_validate()
