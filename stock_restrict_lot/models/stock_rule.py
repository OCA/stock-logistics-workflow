from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        fields = super()._get_custom_move_fields()
        fields += ["restrict_lot_id"]
        return fields

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        values = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        values["restrict_lot_id"] = (
            move_to_copy.restrict_lot_id.id if move_to_copy.restrict_lot_id else False
        )
        return values
