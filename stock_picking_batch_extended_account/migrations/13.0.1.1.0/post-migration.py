# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    batch_picking_auto_invoice_field = env.ref(
        "stock_picking_batch_extended_account.field_res_partner__batch_picking_auto_invoice"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_property
        SET value_text = CASE WHEN value_integer = 1 THEN 'yes' ELSE 'no' END,
        type='char', value_integer=NULL
        WHERE name='batch_picking_auto_invoice' AND fields_id = %s
        """
        % (batch_picking_auto_invoice_field.id,),
    )
