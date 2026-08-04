# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # Drop the partner form view that displayed ``backorder_policy``
    cr.execute(
        """
        DELETE FROM ir_ui_view
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'stock_picking_backorder_policy'
                AND model = 'ir.ui.view'
                AND name = 'view_partner_form'
        )
        """
    )
    cr.execute(
        """
        DELETE FROM ir_model_data
        WHERE module = 'stock_picking_backorder_policy'
            AND model = 'ir.ui.view'
            AND name = 'view_partner_form'
        """
    )
