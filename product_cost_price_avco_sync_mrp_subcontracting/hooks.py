# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    """Method for changing the stock.move associated with the valuation layer. With the
    installation of this module, it is desired to associate the stock.move related to
    subcontracting production instead of linking the movement related to production
    input. This is how it is done in versions 14.0+. So this code is not needed in that
    versions
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    svls = env["stock.valuation.layer"].search(
        [("stock_move_id.is_subcontract", "=", True)], order="stock_move_id, id asc"
    )
    ant_move = False
    for svl in svls:
        if svl.stock_move_id != ant_move:
            index = 0
            ant_move = svl.stock_move_id
            orig_moves = ant_move.move_orig_ids.sorted("id")
        svl.stock_move_id = orig_moves[index]
        index += 1
