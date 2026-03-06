# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def _get_next_picking_type_color(env):
    """Choose the next available color for the operation types."""
    stock_picking_type = env["stock.picking.type"]
    picking_type = stock_picking_type.search_read(
        [("warehouse_id", "!=", False), ("color", "!=", False)],
        ["color"],
        order="color",
    )
    all_used_colors = [res["color"] for res in picking_type]
    available_colors = [color for color in range(0, 12) if color not in all_used_colors]
    return available_colors[0] if available_colors else 0


def create_picking_type(whs):
    env = whs.env
    ir_sequence_sudo = env["ir.sequence"].sudo()
    stock_picking_type = env["stock.picking.type"]
    color = _get_next_picking_type_color(env)
    stock_picking = stock_picking_type.search(
        [("sequence", "!=", False)], limit=1, order="sequence desc"
    )
    max_sequence = stock_picking.sequence or 0
    create_data = whs._get_picking_type_create_values(max_sequence)[0]
    sequence_data = whs._get_sequence_values()
    data = {}
    for picking_type, values in create_data.items():
        if picking_type in ["lot_remove_picking_type_id"] and not whs[picking_type]:
            picking_sequence = sequence_data[picking_type]
            sequence = ir_sequence_sudo.create(picking_sequence)
            values.update(
                warehouse_id=whs.id,
                color=color,
                sequence_id=sequence.id,
            )
            data[picking_type] = stock_picking_type.create(values).id
    if data:
        whs.write(data)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    warehouses = env["stock.warehouse"].search([])
    for warehouse in warehouses:
        create_picking_type(warehouse)
