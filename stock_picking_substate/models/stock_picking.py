# Copyright 2022 ArcheTI (https://archeti.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(selection_add=[("stock.picking", "Transfer")])


class StockPicking(models.Model):
    _inherit = ["stock.picking", "base.substate.mixin"]
    _name = "stock.picking"
    _state_field = "state"

    @api.constrains("substate_id", "state")
    def check_substate_id_value(self):
        picking_states = dict(self._fields["state"].selection)
        pickings_to_update = self.env["stock.picking"]
        for picking in self:
            if not self.env.context.get("check_picking_substate", False):
                pickings_to_update += picking
                continue

            target_state = picking.substate_id.target_state_value_id.target_state_value
            if picking.substate_id and picking.state != target_state:
                raise ValidationError(
                    _(
                        'The substate "%s" is not defined for the state'
                        ' "%s" but for "%s" '
                    )
                    % (
                        picking.substate_id.name,
                        _(picking_states[picking.state]),
                        _(picking_states[target_state]),
                    )
                )
        if pickings_to_update:
            pickings_to_update._update_substate()

    def _update_substate(self):
        """
        state is a computed field, we need this because the function
        _update_before_write_create in base.substate.mixin does not work as
        expected
        :return:
        """
        for picking in self:
            picking.write(
                {"substate_id": picking._get_default_substate_id(picking.state)}
            )

    def write(self, values):
        if "substate_id" in values:
            return super(
                StockPicking, self.with_context(check_picking_substate=True)
            ).write(values)
        return super(StockPicking, self).write(values)

    @api.model
    def create(self, values):
        if "substate_id" in values:
            return super(
                StockPicking, self.with_context(check_picking_substate=True)
            ).create(values)
        return super(StockPicking, self).create(values)
