# Copyright 2026 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "stock_move_valuation_usage.access_stock_valuation_layer_usage",
        "stock_move_valuation_usage.access_stock_move_valuation_usage",
    ),
    (
        "stock_move_valuation_usage.stock_valuation_layer_usage_company_rule",
        "stock_move_valuation_usage.stock_move_valuation_usage_company_rule",
    ),
    (
        "stock_move_valuation_usage.stock_valuation_layer_usage_form",
        "stock_move_valuation_usage.stock_move_valuation_usage_form",
    ),
    (
        "stock_move_valuation_usage.stock_valuation_layer_usage_list",
        "stock_move_valuation_usage.stock_move_valuation_usage_list",
    ),
    (
        "stock_move_valuation_usage.stock_valuation_layer_usage_search",
        "stock_move_valuation_usage.stock_move_valuation_usage_search",
    ),
    (
        "stock_move_valuation_usage.stock_valuation_layer_usage_pivot",
        "stock_move_valuation_usage.stock_move_valuation_usage_pivot",
    ),
    (
        "stock_move_valuation_usage.stock_valuation_layer_usage_action",
        "stock_move_valuation_usage.stock_move_valuation_usage_action",
    ),
    (
        "stock_move_valuation_usage.stock_valuation_layer_usage_menu",
        "stock_move_valuation_usage.stock_move_valuation_usage_menu",
    ),
]


def _rename_usage_model(env):
    openupgrade.logged_query(
        env.cr, "DROP INDEX IF EXISTS stock_valuation_layer_usage_index"
    )
    openupgrade.rename_models(
        env.cr, [("stock.valuation.layer.usage", "stock.move.valuation.usage")]
    )
    openupgrade.rename_tables(
        env.cr, [("stock_valuation_layer_usage", "stock_move_valuation_usage")]
    )
    openupgrade.rename_fields(
        env,
        [
            (
                "stock.move.valuation.usage",
                "stock_move_valuation_usage",
                "stock_move_id",
                "dest_stock_move_id",
            )
        ],
    )
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)


def _fill_usage_moves(env):
    openupgrade.add_fields(
        env,
        [
            (
                "src_stock_move_id",
                "stock.move.valuation.usage",
                "stock_move_valuation_usage",
                "many2one",
                False,
                "stock_move_valuation_usage",
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_valuation_usage smvu
        SET src_stock_move_id = svl.stock_move_id
        FROM stock_valuation_layer svl
        WHERE svl.id = smvu.stock_valuation_layer_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_valuation_usage smvu
        SET dest_stock_move_id = svl.stock_move_id
        FROM stock_valuation_layer svl
        WHERE svl.id = smvu.dest_stock_valuation_layer_id
            AND smvu.dest_stock_move_id IS NULL
        """,
    )


def _fill_stock_move_usage_totals(env):
    openupgrade.add_fields(
        env,
        [
            (
                field_name,
                "stock.move",
                "stock_move",
                "float",
                "double precision",
                "stock_move_valuation_usage",
            )
            for field_name in (
                "usage_quantity",
                "usage_value",
                "incoming_usage_quantity",
                "incoming_usage_value",
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET usage_quantity = usages.quantity, usage_value = usages.value
        FROM (
            SELECT src_stock_move_id AS move_id,
                SUM(quantity) AS quantity, SUM(value) AS value
            FROM stock_move_valuation_usage
            WHERE src_stock_move_id IS NOT NULL
            GROUP BY src_stock_move_id
        ) usages
        WHERE usages.move_id = sm.id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET incoming_usage_quantity = usages.quantity,
            incoming_usage_value = usages.value
        FROM (
            SELECT dest_stock_move_id AS move_id,
                SUM(quantity) AS quantity, SUM(value) AS value
            FROM stock_move_valuation_usage
            WHERE dest_stock_move_id IS NOT NULL
            GROUP BY dest_stock_move_id
        ) usages
        WHERE usages.move_id = sm.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.table_exists(env.cr, "stock_valuation_layer_usage"):
        return
    _rename_usage_model(env)
    _fill_usage_moves(env)
    _fill_stock_move_usage_totals(env)
