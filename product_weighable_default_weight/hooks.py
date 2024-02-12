import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _logger.info(
            "[default UoM] Fast initializing weight fields for products"
            ", if not set"
        )
        env.cr.execute("""
            SELECT value
            FROM ir_config_parameter
            WHERE key='product.weight_in_lbs';""")
        res = env.cr.fetchone()
        if res and res[0] == 1:
            # LBs is the global default UoM
            default_uom = env.ref("uom.product_uom_lb")
        else:
            # Kg is the global default UoM
            default_uom = env.ref("uom.product_uom_kgm")
        if default_uom:
            env.cr.execute("""
                UPDATE product_template
                SET weight = 1.0
                WHERE uom_id = %s
                AND (weight = 0.0 or weight is null);""", (default_uom.id,))
            env.cr.execute("""
                UPDATE product_product pp
                SET weight = 1.0
                FROM product_template pt
                WHERE pt.id = pp.product_tmpl_id
                AND pt.uom_id = %s
                AND (
                    pp.weight = 0.0 or pp.weight is null);""", (default_uom.id,))

        _logger.info(
            "[Other UoM] Initializing weight fields for weighable products,"
            " if not set, via ORM"
        )
        groups = env["product.product"].read_group(
            [
                ("uom_id.measure_type", "=", "weight"),
                '|', ("weight", "=", 0.0), ('weight', '=', False)
            ],
            fields=["weight", "uom_id"],
            groupby="uom_id")

        for group in groups:
            products = env["product.product"].search(group["__domain"])
            new_weight = env["product.template"]._get_weight_from_uom_id(
                group["uom_id"][0]
            )
            _logger.info(
                f"Writing new weight {new_weight} for {len(products)} products."
            )
            products.write({"weight": new_weight})
