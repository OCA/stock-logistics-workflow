from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        """Inherit to set the backorder strategy to restrict."""
        restrict_bo_pickings = self.filtered(
            lambda m: m.picking_type_id.create_backorder == "restrict"
        ).mapped("picking_id")
        if restrict_bo_pickings:
            restrict_bo_pickings._check_backorder()
        return super()._action_done(cancel_backorder=cancel_backorder)
