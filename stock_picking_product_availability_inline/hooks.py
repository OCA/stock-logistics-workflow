# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Precompute all the dates at once"""
    cr.execute(
        "ALTER TABLE stock_move_line ADD COLUMN "
        "IF NOT EXISTS picking_type_warehouse_id INTEGER"
    )
    cr.execute(
        """
        UPDATE stock_move_line sml0
        SET picking_type_warehouse_id = spt.warehouse_id
        FROM stock_move_line sml
        LEFT JOIN stock_picking sp ON sml.picking_id = sp.id
        LEFT JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
        WHERE
            sml0.id=sml.id
            AND sml.picking_type_warehouse_id IS NULL
            AND sml.state NOT IN ('cancel', 'done')
    """
    )
