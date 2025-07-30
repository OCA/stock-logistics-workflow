# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.models import MAGIC_COLUMNS


class MakePickingBatchAbstract(models.Model):
    _name = "stock.picking.batch.creation.profile"
    _inherit = "make.picking.batch.abstract"
    _description = "Batch Creation Profile"

    name = fields.Char(required=True)
    active = fields.Boolean(
        default=True,
    )

    def _make_picking_batch_get_action(self):
        return self.env["ir.actions.act_window"]._for_xml_id(
            "stock_picking_batch_creation.make_picking_batch_act_window"
        )

    def action_launch_wizard(self):
        """
        Launch the wizard to create batches and use
        each property defined in profile
        """
        self.ensure_one()
        wizard = self._create_wizard()
        action = self._make_picking_batch_get_action()
        action.update(
            {
                "res_id": wizard.id,
            }
        )
        return action

    @api.model
    def _get_wizard_fields(self):
        """
        Returns the fields contained in the abstract
        (as there could have specific ones in real models - but not useful in this case)
        """
        for _field in self.env["make.picking.batch.abstract"]._fields.keys():
            if _field in MAGIC_COLUMNS:
                continue
            yield _field

    def _get_wizard_values(self):
        """
        Iterate on each wizard field and get value from the profile
        """
        self.ensure_one()
        wizard_fields = self.env[
            "stock.picking.batch.creation.profile"
        ]._get_wizard_fields()
        values = dict()
        for _field in wizard_fields:
            values[_field] = self[_field]
        return values

    def _create_wizard(self):
        self.ensure_one()
        Wizard = self.env["make.picking.batch"]
        values = self._get_wizard_values()
        create_values = Wizard._convert_to_write(values)
        wizard = Wizard.create(create_values)
        return wizard
