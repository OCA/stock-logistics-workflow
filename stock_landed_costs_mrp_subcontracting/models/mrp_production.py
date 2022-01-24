# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _generate_backorder_productions(self, close_mo=True):
        backorders = super(MrpProduction, self)._generate_backorder_productions(
            close_mo=close_mo
        )
        for backorder in backorders:
            for finished_move in backorder.move_finished_ids:
                for move_dest in finished_move.move_dest_ids:
                    # We have to make sure that the move that is a
                    # subcontracted receipt only has as origin the
                    # subcontracting manufacturing order finished move id.
                    # Otherwise the landed cost application will propose
                    # incorrect moves, not linked to the actual picking that
                    # is being proposed.
                    if move_dest.is_subcontract:
                        move_dest.write({"move_orig_ids": [(6, 0, finished_move.ids)]})
        return backorders
