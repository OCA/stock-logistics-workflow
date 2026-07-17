# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class StockReceptionDiscrepancyDistributionWiz(models.TransientModel):
    _name = "stock.reception.discrepancy.distribution.wiz"
    _description = "Destination moves to change quantities"

    move_id = fields.Many2one(comodel_name="stock.move")
    product_id = fields.Many2one(related="move_id.product_id", readonly=True)
    product_uom = fields.Many2one(related="move_id.product_uom")
    move_qty_done = fields.Float(related="move_id.quantity")
    move_dest_demand = fields.Float(
        compute="_compute_move_dest_demand", digits="Product Unit of Measure"
    )
    over_quantity = fields.Float(
        compute="_compute_move_dest_demand", digits="Product Unit of Measure"
    )
    # This field is not defined as related to avoid issue with create and delete
    # attributes in the view
    move_dest_ids = fields.One2many(
        comodel_name="stock.move",
        compute="_compute_move_dest_ids",
        inverse="_inverse_move_dest_ids",
    )

    @api.depends("move_dest_ids.product_uom_qty", "move_qty_done")
    def _compute_move_dest_demand(self):
        for wiz in self:
            wiz.move_dest_demand = sum(wiz.move_dest_ids.mapped("product_uom_qty"))
            wiz.over_quantity = wiz.move_qty_done - wiz.move_dest_demand

    @api.depends("move_id")
    def _compute_move_dest_ids(self):
        for wiz in self:
            wiz.move_dest_ids = wiz.move_id.move_dest_ids

    def _inverse_move_dest_ids(self):
        """To store changes on stock moves"""
        for wiz in self:
            wiz.move_id.move_dest_ids = wiz.move_dest_ids

    def action_confirm(self):
        # Update initial demand to avoid an extra picking when use multi steps reception
        # and MTO
        if self.move_id.quantity > self.move_id.product_uom_qty:
            self.move_id.product_uom_qty = self.move_id.quantity
