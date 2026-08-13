# Copyright 2018 Tecnativa - Sergio Teruel
# Copyright 2026 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute("""
        UPDATE product_template
        SET auto_create_lot_option = 'odoo_sequence'
        WHERE auto_create_lot IS TRUE
    """)
