from odoo import SUPERUSER_ID, api
from odoo.tools import sql


def pre_init_hook(cr):
    if not sql.column_exists(cr, "stock_quant", "is_locked_by_picking"):
        cr.execute(
            "ALTER TABLE stock_quant ADD COLUMN is_locked_by_picking boolean DEFAULT False"
        )


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["stock.warehouse"].search([])._create_quality_check_lock()
