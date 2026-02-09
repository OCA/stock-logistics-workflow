from odoo import fields, models


class SelectReusablePackage(models.TransientModel):
    _name = "select.reusable.package"
    _description = "Select Reusable Package"

    picking_id = fields.Many2one("stock.picking", required=True)
    warehouse_id = fields.Many2one(
        related="picking_id.picking_type_id.warehouse_id",
    )
    package_id = fields.Many2one(
        "stock.quant.package",
        string="Reusable Package",
        required=True,
        domain="[('package_use', '=', 'reusable'), "
        "('location_id.usage', '=', 'internal'), "
        "('location_id', 'child_of', warehouse_id)]",
    )

    def action_confirm(self):
        return self.picking_id.with_context(
            reusable_package_id=self.package_id.id
        ).action_put_in_pack(
            move_lines_to_pack=self.env.context.get("move_lines_to_pack")
        )
