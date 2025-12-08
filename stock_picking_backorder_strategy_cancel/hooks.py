from odoo.tools.sql import column_exists


def pre_init_hook(env):
    if not column_exists(env.cr, "stock_picking_type", "backorder_strategy"):
        return

    env.cr.execute(
        """SELECT id FROM stock_picking_type WHERE backorder_strategy = 'cancel'"""
    )
    result = env.cr.fetchall()

    if not result:
        return

    picking_ids = [res[0] for res in result]

    update_query = """
        UPDATE stock_picking_type
        SET create_backorder = 'cancel'
        WHERE id IN %s
    """
    env.cr.execute(update_query, (tuple(picking_ids),))
