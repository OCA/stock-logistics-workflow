#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import psycopg2
from psycopg2 import sql

from odoo import api, models
from odoo.tools import flatten, mute_logger

_logger = logging.getLogger(__name__)


class SaleOrderLine (models.Model):
    _inherit = 'sale.order.line'

    def _prepare_kit_component_line_values(
        self, component_bom_line, component_bom_line_dict,
    ):
        """Default values for the Component line that override `self`'s values."""
        self.ensure_one()
        component = component_bom_line.product_id
        quantity = component_bom_line_dict['qty']
        component_line_default_values = {
            'product_id': component.id,
            'product_uom_qty': quantity,
            # Needs to be explicit because required
            # and its copy is disabled
            'order_id': self.order_id.id,
        }
        return component_line_default_values

    def _create_kit_component_lines(self):
        """Create sale order lines for components for each line containing a kit.

        :return: Mapping from the sale order lines of the kit
        to the sale order lines of its components.
        """
        kit_lines_to_component_lines = dict()
        for line in self:
            product = line.product_id
            product_bom = self.env['mrp.bom']._bom_find(
                product=product,
            )
            if product_bom:
                is_kit = product_bom.type == 'phantom'
                if is_kit:
                    kit_lines_to_component_lines[line] = self.browse()
                    boms_done, lines_done = product_bom.explode(
                        product,
                        line.product_uom_qty,
                    )
                    for component_bom_line, component_bom_line_dict in lines_done:
                        component_line_default_values = \
                            line._prepare_kit_component_line_values(
                                component_bom_line, component_bom_line_dict,
                            )
                        component_line = line.copy(
                            default=component_line_default_values,
                        )
                        kit_lines_to_component_lines[line] |= component_line
        return kit_lines_to_component_lines

    def _restore_kit_component_foreign_keys(
        self, kit_line, kit_component_lines,
    ):
        """Redirect foreign keys linked to component lines to the kit line."""
        foreign_keys = self.env['base.partner.merge.automatic.wizard'] \
            ._get_fk_on(self._table)
        for table, column in foreign_keys:
            try:
                with mute_logger('odoo.sql_db'), self._cr.savepoint():
                    query = \
                        sql.SQL(
                            'UPDATE {table} '
                            'SET {column} = %(kit_id)s '
                            'WHERE {column} = ANY(%(component_ids)s)'
                        ).format(
                            table=sql.Identifier(table),
                            column=sql.Identifier(column),
                        )
                    self._cr.execute(
                        query,
                        params={
                            'kit_id': kit_line.id,
                            'component_ids': kit_component_lines.ids,
                        },
                    )
            except psycopg2.Error:
                _logger.debug(
                    "Cannot restore link to kit lines, "
                    "most likely due to violated unique constraint",
                    exc_info=True,
                )
        return True

    def _restore_kit_component_reference_fields(
        self, kit_line, kit_component_lines,
    ):
        """Redirect fields linked to component lines to the kit line."""
        reference_fields_records = self.env['ir.model.fields'].search(
            [
                ('ttype', '=', 'reference'),
            ],
        )
        for reference_field_record in reference_fields_records:
            model_name = reference_field_record.model
            field_name = reference_field_record.name
            try:
                records_model = self.env[model_name]
                reference_field = records_model._fields[field_name]
            except KeyError:
                # unknown model or field => skip
                continue

            if reference_field.compute is not None:
                continue

            component_reference_values = [
                reference_field.convert_to_read(
                    kit_component_line,
                    records_model.browse(),
                )
                for kit_component_line in kit_component_lines
            ]
            to_update_records = records_model.sudo().search(
                [
                    (field_name, 'in', component_reference_values),
                ],
            )
            to_update_records.update({
                field_name: reference_field.convert_to_read(
                    kit_line,
                    records_model.browse(),
                ),
            })
        return True

    def _unlink_kit_component_lines(self, kit_lines_to_component_lines):
        """Remove the created component lines.

        Redirect any reference to the component lines to the kit line.
        """
        for kit_line, kit_component_lines in kit_lines_to_component_lines.items():
            self._restore_kit_component_foreign_keys(kit_line, kit_component_lines)
            self._restore_kit_component_reference_fields(kit_line, kit_component_lines)

            order = kit_component_lines.mapped('order_id')
            # Cannot unlink lines of confirmed orders
            old_state = order.state
            order.state = 'draft'
            kit_component_lines.unlink()
            order.state = old_state
        return True

    @api.multi
    def _action_launch_stock_rule(self):
        kit_lines_to_component_lines = self._create_kit_component_lines()

        kit_lines_ids = \
            [line.id for line in kit_lines_to_component_lines.keys()]
        kit_lines = self.browse(kit_lines_ids)

        component_lines_ids = \
            [line.ids for line in kit_lines_to_component_lines.values()]
        component_lines = self.browse(flatten(component_lines_ids))

        # Launch stock rules of the components
        # instead of the stock rules of the kit lines
        to_launch_lines = self - kit_lines + component_lines
        result = super(SaleOrderLine, to_launch_lines)._action_launch_stock_rule()

        self._unlink_kit_component_lines(kit_lines_to_component_lines)
        return result
