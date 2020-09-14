# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    groups = env["procurement.group"].search([])
    for group in groups:
        pickings = group.picking_ids
        all_sales = pickings.move_lines.sale_line_id.order_id
        # approximation, only new orders will have the correct
        # links
        group.sale_ids |= all_sales
