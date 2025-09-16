# Copyright 2024 Quartile (https://www.quartile.co)
# Copyright 2025 Alberto Martínez <alberto.martinez@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestStockValuationFifoCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_categ = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "property_cost_method": "fifo",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": cls.product_categ.id,
                "tracking": "lot",
            }
        )
        cls.vendor_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.cust_loc = cls.env.ref("stock.stock_location_customers")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.pick_type_in = cls.env.ref("stock.picking_type_in")
        cls.pick_type_out = cls.env.ref("stock.picking_type_out")
        cls.landed_cost = cls.env["product.product"].create(
            {
                "name": "Landed Cost",
                "detailed_type": "service",
                "landed_cost_ok": True,
                "property_account_expense_id": cls.env.ref(
                    "l10n_generic_coa.1_expense"
                ).id,
            }
        )
        cls.lot1 = cls.env["stock.production.lot"].create(
            {
                "name": "0001",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )

    def create_picking(self, op_type, lot_ids, ml_qty=5.0, price=0.0):
        loc = self.vendor_loc
        loc_dest = self.stock_loc
        pick_type = self.pick_type_in
        if op_type == "out":
            loc = self.stock_loc
            loc_dest = self.cust_loc
            pick_type = self.pick_type_out
        pick = self.env["stock.picking"].create(
            {
                "location_id": loc.id,
                "location_dest_id": loc_dest.id,
                "picking_type_id": pick_type.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test",
                "product_id": self.product.id,
                "location_id": loc.id,
                "location_dest_id": loc_dest.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": ml_qty * len(lot_ids),
                "picking_id": pick.id,
                "price_unit": price,
            }
        )
        for lot in lot_ids:
            self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": pick.id,
                    "product_id": self.product.id,
                    "location_id": loc.id,
                    "location_dest_id": loc_dest.id,
                    "product_uom_id": move.product_uom.id,
                    "qty_done": ml_qty,
                    "lot_id": lot.id,
                }
            )
        pick.action_confirm()
        pick.action_assign()
        pick._action_done()
        return pick, move

    def create_landed_cost(self, picking, cost):
        landed_cost = self.env["stock.landed.cost"].create(
            dict(
                picking_ids=[(6, 0, [picking.id])],
                account_journal_id=self.env.company.lc_journal_id.id
                or self.env["ir.property"]
                ._get("property_stock_journal", "product.category")
                .id,
                cost_lines=[
                    (
                        0,
                        0,
                        {
                            "name": "equal split",
                            "split_method": "equal",
                            "price_unit": cost,
                            "product_id": self.landed_cost.id,
                        },
                    )
                ],
            )
        )
        landed_cost.compute_landed_cost()
        landed_cost.button_validate()
        return landed_cost

    def return_picking(self, picking, return_qty):
        return_picking_wizard_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        return_picking_wizard = return_picking_wizard_form.save()
        return_picking_wizard.product_return_moves.write({"quantity": return_qty})
        return_picking_wizard_action = return_picking_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(
            return_picking_wizard_action["res_id"]
        )
        return_move = return_picking.move_ids_without_package
        return_move.move_line_ids.qty_done = return_qty
        return_picking.button_validate()
        return return_picking
