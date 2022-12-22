# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged

from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import (
    ValuationReconciliationTestCommon,
)


@tagged("post_install", "-at_install")
class TestStockLandedCostsMrpSubcontracting(ValuationReconciliationTestCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        # Get required Model
        cls.account_model = cls.env["account.account"].sudo()
        cls.quant_model = cls.env["stock.quant"]
        # Get required Model data
        # Extend the permissions of the user testing
        cls.env.user.groups_id |= cls.env.ref("stock.group_stock_manager")
        # Activate the subcontracting flag in the res.config.settings.
        # - On install mrp_subcontracting all companies activated this feature
        # Create a vendor that will be in charge of the subcontracting.
        cls.subcontracting_vendor = cls.env["res.partner"].create(
            {"name": "subcontracting_vendor"}
        )
        cls.wh = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location = cls.wh.lot_stock_id
        # Create a vendor that will be in charge of the additional landed costs.
        cls.costs_vendor = cls.env["res.partner"].create({"name": "costs_vendor"})
        # Create a product category with costing method FIFO and inventory
        # valuation = automated.
        cls.valuation_acc = cls.company_data["default_account_stock_valuation"]
        cls.input_acc = cls.company_data["default_account_stock_in"]
        cls.output_acc = cls.company_data["default_account_stock_out"]
        cls.category_fifo_automated = (
            cls.env["product.category"]
            .with_company(cls.env.company)
            .create(
                {
                    "name": "category_fifo_automated",
                    "property_cost_method": "fifo",
                    "property_valuation": "real_time",
                    "property_stock_valuation_account_id": cls.valuation_acc.id,
                    "property_stock_account_input_categ_id": cls.input_acc.id,
                    "property_stock_account_output_categ_id": cls.output_acc.id,
                }
            )
        )

        cls.category_landed_costs = (
            cls.env["product.category"]
            .with_company(cls.env.company)
            .create(
                {
                    "name": "category_landed_costs",
                    "property_cost_method": "standard",
                    "property_valuation": "manual_periodic",
                    "property_stock_valuation_account_id": cls.valuation_acc.id,
                    "property_stock_account_input_categ_id": cls.input_acc.id,
                    "property_stock_account_output_categ_id": cls.output_acc.id,
                }
            )
        )
        # Create a product that will be the subcontracted, using the category
        # that was created. Add the buy route
        cls.product_subcontracted = cls.env["product.product"].create(
            {
                "name": "product_subcontracted",
                "type": "product",
                "categ_id": cls.category_fifo_automated.id,
                "route_ids": [
                    (6, 0, cls.env.ref("purchase_stock.route_warehouse0_buy").ids)
                ],
            }
        )
        # Add a supplierinfo record to the product, with the subcontracting
        # vendor and the cost of $10 corresponding to the subcontracting
        # service.
        cls.env["product.supplierinfo"].create(
            {
                "name": cls.subcontracting_vendor.id,
                "price": 10,
                "product_tmpl_id": cls.product_subcontracted.product_tmpl_id.id,
                "delay": 1,
            }
        )
        # Create a component product. Set the routes 'Buy' and 'Resupply
        # Subcontractor on Order'. Add a starting cost of $10.
        cls.product_component = cls.env["product.product"].create(
            {
                "name": "product_component",
                "type": "product",
                "categ_id": cls.category_fifo_automated.id,
                "route_ids": [
                    (
                        6,
                        0,
                        cls.env.ref("purchase_stock.route_warehouse0_buy").ids
                        + cls.env.ref(
                            "mrp_subcontracting.route_resupply_subcontractor_mto"
                        ).ids,
                    )
                ],
                "standard_price": 10.0,
            }
        )
        # Add 1 units to the stock on hand for the component.
        cls.quant_model.with_user(cls.env.user)._update_available_quantity(
            cls.product_component, cls.stock_location, 1.0
        )
        # Create a bill of materials of type subcontracting and add the above
        # component. 1 unit of the finished product requires 1 unit of the
        # component. Set as vendor of the bill of material the subcontracting
        # partner.
        bom_form = Form(cls.env["mrp.bom"])
        bom_form.type = "subcontract"
        bom_form.product_tmpl_id = cls.product_subcontracted.product_tmpl_id
        bom_form.subcontractor_ids.add(cls.subcontracting_vendor)
        with bom_form.bom_line_ids.new() as bom_line:
            bom_line.product_id = cls.product_component
            bom_line.product_qty = 1
        cls.bom = bom_form.save()
        # Create a product for the landed costs. Set the flag 'landed cost'.
        cls.product_landed_cost = cls.env["product.product"].create(
            {
                "name": "product_landed_cost",
                "type": "service",
                "categ_id": cls.category_landed_costs.id,
                "landed_cost_ok": True,
            }
        )

    @classmethod
    def _create_account(cls, acc_type, name, code, company, reconcile=False):
        """Create an account."""
        account = cls.account_model.create(
            {
                "name": name,
                "code": code,
                "user_type_id": acc_type.id,
                "company_id": company.id,
                "reconcile": reconcile,
            }
        )
        return account

    def done_picking(self, picking):
        picking.action_confirm()
        picking.action_assign()
        res_dict = picking.button_validate()
        wizard = Form(
            self.env[(res_dict.get("res_model"))].with_context(res_dict.get("context"))
        ).save()
        wizard.process()
        return True

    def test_01(self):
        # Create a purchase order for the subcontracting vendor and the
        # subcontracted product. Confirm the PO
        po = Form(self.env["purchase.order"])
        po.partner_id = self.subcontracting_vendor
        with po.order_line.new() as invoice_line:
            invoice_line.product_id = self.product_subcontracted
            invoice_line.product_qty = 1
            invoice_line.price_unit = 10
        po = po.save()
        po.button_confirm()
        # Locate the delivery order that has been created for the component
        # from the stock location to the subcontracting location and complete
        # it.
        delivery_order = self.env["stock.picking"].search(
            [
                ("partner_id", "=", po.partner_id.id),
                ("location_dest_id", "=", po.company_id.subcontracting_location_id.id),
                ("state", "!=", "done"),
            ]
        )
        self.done_picking(delivery_order)
        # Locate the incoming shipment associated with the Purchase Order and
        # complete it.
        if po.picking_ids:
            self.done_picking(po.picking_ids[0])
        # Check that inventory valuation for the subcontracted product is now
        # $20 ($10 for the subcontracting process + $10 for the component)
        self.assertEqual(self.product_subcontracted.standard_price, 20.0)
        # Create a vendor bill for the landed costs. Add the landed cost
        # vendor and add a line with the landed cost product, with cost $10.
        self.product_landed_cost.with_company(self.env.company).categ_id.write(
            {
                "property_stock_valuation_account_id": self.valuation_acc.id,
                "property_stock_account_input_categ_id": self.input_acc.id,
                "property_stock_account_output_categ_id": self.output_acc.id,
            }
        )
        self.product_subcontracted.with_company(self.env.company).categ_id.write(
            {
                "property_stock_valuation_account_id": self.valuation_acc.id,
                "property_stock_account_input_categ_id": self.input_acc.id,
                "property_stock_account_output_categ_id": self.output_acc.id,
            }
        )
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        )
        move_form.invoice_date = move_form.date
        move_form.partner_id = self.costs_vendor
        with move_form.invoice_line_ids.new() as invoice_line:
            invoice_line.product_id = self.product_landed_cost
            invoice_line.quantity = 1
            invoice_line.price_unit = 10
        move = move_form.save()
        move.action_post()
        # Create a landed cost from the vendor bill and add the incoming
        # shipment associated with the PO.
        res_actions = move.button_create_landed_costs()
        landed_cost = self.env["stock.landed.cost"].browse(
            res_actions.get("res_id", False)
        )
        landed_cost_form = Form(landed_cost)
        landed_cost_form.picking_ids.add(po.picking_ids)
        landed_cost_form.save()
        # Compute the landed cost and complete it.
        landed_cost.compute_landed_cost()
        landed_cost.button_validate()
        # Verify that the inventory valuation for the subcontracted product
        # is now $30 (the inventory valuation has increased by $10 due to the
        # landed cost being added.)
        self.assertEqual(
            sum(self.product_subcontracted.mapped("stock_valuation_layer_ids.value")),
            30.0,
        )
