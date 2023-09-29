# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

try:
    from openupgradelib import openupgrade
except Exception:
    from odoo.tools import sql as openupgrade

_logger = logging.getLogger(__name__)


def fill_layer_usage_dest_stock_valuation_layer_id(env):
    _logger.info("Filling the dest layer in layer usages")
    layer_usages = env["stock.valuation.layer.usage"].search(
        [("dest_stock_valuation_layer_id", "=", False)]
    )
    for layer_usage in layer_usages:
        # The filtered is because of dropships, otherwise there itself
        # wont be included in any case
        dest_layer = layer_usage.stock_move_id.stock_valuation_layer_ids.filtered(
            lambda l: l.id != layer_usage.stock_valuation_layer_id.id
        )
        if dest_layer:
            layer_usage.dest_stock_valuation_layer_id = dest_layer and dest_layer[0]


@openupgrade.migrate()
def migrate(env, version):
    fill_layer_usage_dest_stock_valuation_layer_id(env)
