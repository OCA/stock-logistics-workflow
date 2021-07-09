# Copyright 2021 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools.sql import column_exists, rename_column


def migrate(cr, version):
    # Rename estimated_pack_weight into estimated_pack_weight_kg
    if column_exists(cr, "stock_quant_package", "estimated_pack_weight"):
        rename_column(
            cr,
            "stock_quant_package",
            "estimated_pack_weight",
            "estimated_pack_weight_kg",
        )
