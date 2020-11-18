# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.model
    def _transfer_pickings_with_auto_move(self, auto_moves_by_pickings):
        """This function is meant to simulate what a user would normally
        transfer a picking from the user interface either partial processing
        or full processing.
        @params auto_moves_by_pickings: dict of moves grouped by pickings
        {stock.picking(id): stock.move(id1, id2, id3 ...), ...}
        """
        backorder_obj = self.env["stock.backorder.confirmation"]
        immediate_obj = self.env["stock.immediate.transfer"]
        for picking in auto_moves_by_pickings:
            # Create immediate transfer wizard so it will fill the qty_done
            # on the auto move linked operation
            immediate_wizard_dict = picking.button_validate()
            if (
                isinstance(immediate_wizard_dict, dict)
                and "res_model" in immediate_wizard_dict
                and "stock.immediate.transfer" == immediate_wizard_dict.get("res_model")
            ):
                immediate_wizard = immediate_obj.browse(
                    immediate_wizard_dict.get("res_id")
                )
                backorder_wizard_dict = immediate_wizard.process()
                if (
                    isinstance(backorder_wizard_dict, dict)
                    and "res_model" in backorder_wizard_dict
                    and "stock.backorder.confirmation"
                    == backorder_wizard_dict.get("res_model")
                ):
                    backorder_wizard = backorder_obj.browse(
                        backorder_wizard_dict.get("res_id")
                    )
                    if backorder_wizard:
                        backorder_wizard.process()

        return
