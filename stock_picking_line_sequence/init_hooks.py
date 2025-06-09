# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    """
    Fetches all the pickings and resets the sequence of the move lines
    """
    stock = env["stock.picking"].search([])
    stock.with_context(skip_update_line_ids=True)._reset_sequence()
