# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api
from odoo.tools import sql

_logger = logging.getLogger(__name__)


def _create_lock_route(env, picking_type):
    # Before 16.0.2.0.0, any quant could be locked with the picking type,
    # Migrate to a dedicated route with a pull rule to lock the quant
    # from its exact location.
    location_src = (
        picking_type.warehouse_id.view_location_id
        or picking_type.default_location_src_id
    )
    location_dest = (
        picking_type.default_location_dest_id or picking_type.default_location_src_id
    )
    if not location_src or not location_dest:
        _logger.warning(
            "No quant lock route created for operation type %s: "
            "no default location defined.",
            picking_type.display_name,
        )
        return
    name = "Quant Lock: %s" % picking_type.display_name
    env["stock.route"].create(
        {
            "name": name,
            "allow_quant_lock": True,
            "product_selectable": False,
            "company_id": picking_type.company_id.id,
            "rule_ids": [
                (
                    0,
                    0,
                    {
                        "name": name,
                        "action": "pull",
                        "procure_method": "make_to_stock",
                        "location_src_id": location_src.id,
                        "location_dest_id": location_dest.id,
                        "picking_type_id": picking_type.id,
                        "warehouse_id": picking_type.warehouse_id.id,
                        "company_id": picking_type.company_id.id,
                    },
                )
            ],
        }
    )
    _logger.info("Quant lock route created for %s", picking_type.display_name)


def _migrate_lock_picking_types(env):
    if not sql.column_exists(env.cr, "stock_picking_type", "allow_quant_lock"):
        return
    env.cr.execute("SELECT id FROM stock_picking_type WHERE allow_quant_lock")
    picking_type_ids = [row[0] for row in env.cr.fetchall()]
    picking_types = env["stock.picking.type"].with_context(active_test=False)
    for picking_type in picking_types.browse(picking_type_ids):
        _create_lock_route(env, picking_type)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _migrate_lock_picking_types(env)
    # Only create the missing records: nothing existing is modified
    env["stock.warehouse"].search([])._create_quality_check_lock()
