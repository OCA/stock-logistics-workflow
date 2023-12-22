# Copyright (C) 2023 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models


class StockPickingKitWizard(models.TransientModel):
    _name = "stock.picking.kit.wizard"
    _description = "Kit Picking Wizard"

    def _default_picking_id(self):
        "Default to the current form's selected Picking"
        return self.env["stock.picking"].browse([self.env.context.get("active_id", 0)])

    @api.constrains("product_id")
    def _check_product_id_is_serial(self):
        for wizard in self:
            product = wizard.product_id
            if not (product.is_kits or product.tracking == "serial"):
                raise exceptions.ValidationError(
                    _("Product %s must but a Kit or be Serial Number controlled.")
                    % wizard.product_id.display_name
                )

    @api.depends("picking_id")
    def _compute_product_selectable_ids(self):
        for wizard in self:
            boms = wizard.picking_id.move_ids.bom_line_id.bom_id.filtered(
                lambda x: x.type == "phantom"
            )
            products = boms.product_id | boms.product_tmpl_id.product_variant_ids
            wizard.product_selectable_ids = products

    picking_id = fields.Many2one(
        "stock.picking",
        default=lambda self: self._default_picking_id(),
    )
    company_id = fields.Many2one(related="picking_id.company_id")
    picking_type = fields.Selection(related="picking_id.picking_type_id.code")
    product_id = fields.Many2one("product.product")
    product_selectable_ids = fields.Many2many(
        "product.product",
        compute="_compute_product_selectable_ids",
    )
    quantity = fields.Integer(default=0)
    line_ids = fields.One2many(
        "stock.picking.kit.wizard.line",
        "wizard_id",
    )

    @api.onchange("product_id", "quantity")
    def onchange_for_move_line_ids(self):
        "Lines populated from the Kit BoM"
        Product = self.env["product.product"]
        if self.product_id and self.quantity:
            if self.product_id.is_kits:
                # Kits are exploded
                component_ids = self.product_id.get_components()
                components = Product.browse(component_ids)
            else:
                # Regular serial products are simply added
                components = self.product_id
            values = []
            for x in range(self.quantity):
                is_start_pack = True
                for component in components:
                    value = {
                        "wizard_id": self.id,
                        "component_id": component.id,
                        "number": x + 1,
                        "is_start_pack": is_start_pack,
                    }
                    values.append(value)
                    is_start_pack = False
            self.line_ids.create(values)
        else:
            self.line_ids.unlink()
        return

    def action_apply(self):
        self.ensure_one()
        MoveLine = self.env["stock.move.line"]
        pack_lines = MoveLine
        for wizard_line in self.line_ids.filtered("lot_name"):
            move_line = wizard_line._get_move_line_to_update()
            if not move_line:
                raise exceptions.UserError(
                    _(
                        "No matching Detailed Operations line found"
                        " for %(name)s # %(number)s."
                    )
                    % {
                        "name": wizard_line.component_id.display_name,
                        "number": wizard_line.number,
                    }
                )
            # else:
            if wizard_line.is_start_pack and pack_lines:
                self._put_in_pack(pack_lines)
                pack_lines = MoveLine
            move_line.lot_name = wizard_line.lot_name
            move_line.qty_done = wizard_line.qty_done
            pack_lines |= move_line
        # Don't forget to add the last Pack
        if pack_lines:
            self._put_in_pack(pack_lines)
        return

    def _put_in_pack(self, move_lines):
        # If Packs option is enabled for the user
        # Creates a Pack for the given Move Lines
        # and sets pack name to the Lot of the first line
        self.ensure_one()
        has_package_group = self.user_has_groups("stock.group_tracking_lot")
        if move_lines and has_package_group:
            package = self.picking_id._put_in_pack(move_lines)
            main_lot = move_lines[:1].lot_name
            if main_lot:
                package.name = main_lot
            return package


class StockPickingKitWizardLine(models.TransientModel):
    _name = "stock.picking.kit.wizard.line"
    _description = "Kit Picking Wizard Line"

    def _get_move_line_to_update(self):
        picking_move_lines = self.wizard_id.picking_id.move_line_ids
        return picking_move_lines.filtered(
            lambda x: x.product_id == self.component_id and not x.lot_name
        )[:1]

    wizard_id = fields.Many2one("stock.picking.kit.wizard")
    number = fields.Char("Item#")
    is_start_pack = fields.Boolean()
    component_id = fields.Many2one("product.product")
    lot_name = fields.Char("Serial#")
    qty_done = fields.Float(default=1)
    tracking = fields.Selection(related="component_id.tracking")
