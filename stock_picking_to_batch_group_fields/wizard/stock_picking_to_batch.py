# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPickingToBatch(models.TransientModel):
    _inherit = "stock.picking.to.batch"

    batch_by_group = fields.Boolean(
        string="Grouped by fields",
        help="If set, multiple batch picking will be created, one per group field",
    )
    group_field_ids = fields.One2many(
        comodel_name="stock.picking.batch.creator.group.field",
        inverse_name="picking_to_batch_id",
        string="Group by field",
        help="If set any, multiple batch picking will be created, one per "
        "group field",
    )

    @api.onchange("batch_by_group")
    def onchange_batch_by_group(self):
        if self.batch_by_group:
            self.group_field_ids = False
            for index, field in enumerate(self.load_store_fields()):
                self.group_field_ids += self.group_field_ids.new(
                    {"sequence": index, "field_id": field.id}
                )

    def load_store_fields(self):
        group_field_names = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("stock_picking_to_batch_group_fields.group_field")
        )
        if not group_field_names:
            return self.env["ir.model.fields"].browse()

        return self.env["ir.model.fields"].search(
            [
                ("model", "=", "stock.picking"),
                ("name", "in", group_field_names.split(",")),
            ]
        )

    @api.model
    def default_get(self, fields):
        """
        Set last grouped fields used that are stored in config parameters
        """
        res = super().default_get(fields)
        group_fields = self.load_store_fields()
        res["batch_by_group"] = group_fields and True or False
        return res

    def create_multiple_batch(self, domain):
        """Create n batch pickings by grouped fields selected"""
        StockPicking = self.env["stock.picking"]
        groupby = [f.field_id.name for f in self.group_field_ids]
        pickings_grouped = StockPicking.read_group(domain, groupby, groupby, lazy=False)
        if not pickings_grouped:
            raise UserError(
                _(
                    "All selected pickings are already in a batch picking "
                    "or are in a wrong state."
                )
            )
        batchs = self.env["stock.picking.batch"]
        for group in pickings_grouped:
            batch = self.env["stock.picking.batch"].create(
                {
                    "user_id": self.user_id.id,
                }
            )
            StockPicking.search(group["__domain"]).write({"batch_id": batch.id})
            if self.mode == "new" and not self.is_create_draft:
                batch.action_confirm()
            batchs |= batch
        return batchs

    def attach_pickings(self):
        if self.mode == "new" and self.batch_by_group and self.group_field_ids:
            domain = [
                ("id", "in", self.env.context["active_ids"]),
                ("batch_id", "=", False),
                ("state", "not in", ("cancel", "done")),
            ]
            batchs = self.create_multiple_batch(domain)
            self.env["ir.config_parameter"].sudo().set_param(
                "stock_picking_to_batch_group_fields.group_field",
                ",".join([f.field_id.name for f in self.group_field_ids]),
            )
        else:
            super().attach_pickings()
            batchs = (
                self.env["stock.picking"]
                .browse(self.env.context.get("active_ids"))
                .batch_id
            )
        return self.action_view_batch_picking(batchs)

    def action_view_batch_picking(self, batch_pickings):
        if len(batch_pickings) > 1:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "stock_picking_batch.stock_picking_batch_action"
            )
            action["domain"] = [("id", "in", batch_pickings.ids)]
        else:
            action = batch_pickings.get_formview_action()
        return action


class StockBatchPickingCreatorGroupField(models.TransientModel):
    _name = "stock.picking.batch.creator.group.field"
    _description = "Batch Picking Creator Group Field"
    _order = "sequence, id"

    picking_to_batch_id = fields.Many2one(
        comodel_name="stock.picking.to.batch",
        ondelete="cascade",
        required=True,
    )
    sequence = fields.Integer(help="Group by picking field", default=0)
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field to group",
        domain=[("model", "=", "stock.picking"), ("store", "=", True)],
        required=True,
    )
