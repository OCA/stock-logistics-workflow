from odoo import _, api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        self._apply_package_consumption()
        return super()._action_done()

    def _apply_package_consumption(self):
        for picking in self:
            if picking.picking_type_code != "outgoing":
                return

            product_qty_dict = {}
            for package in picking.package_ids:
                if not package.package_type_id.product_id:
                    continue
                if not product_qty_dict.get(package.package_type_id.product_id.id):
                    product_qty_dict.update({package.package_type_id.product_id.id: 0})
                product_qty_dict[package.package_type_id.product_id.id] += 1

            move_vals = []
            for product_id, qty in product_qty_dict.items():
                move_vals.append(
                    self._get_package_consumption_move_values(picking, product_id, qty)
                )
            moves = (
                self.env["stock.move"]
                .with_context(inventory_mode=False)
                .create(move_vals)
            )
            moves._action_done()

    @api.model
    def _get_package_consumption_move_values(self, picking_id, product_id, qty):
        """Called on validation of outgoing pickings

        :param picking_id: `stock.picking`
        :param product_id: int
        :param qty: float
        :return: dict with all values needed to create a new `stock.move`
                 with its move line to consume package product
        """
        self.ensure_one()
        name = _("Product Packaging used on %s", picking_id.name)
        product = self.env["product.product"].browse(product_id)

        return {
            "name": name,
            "product_id": product.id,
            "product_uom": product.uom_id.id,
            "product_uom_qty": qty,
            "company_id": picking_id.company_id.id or self.env.company.id,
            "state": "confirmed",
            "location_id": picking_id.location_id.id,
            "location_dest_id": picking_id.location_dest_id.id,
            "restrict_partner_id": picking_id.owner_id.id,
            "is_inventory": True,
            "picked": True,
            "move_line_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": product.id,
                        "product_uom_id": product.uom_id.id,
                        "quantity": qty,
                        "location_id": picking_id.location_id.id,
                        "location_dest_id": picking_id.location_dest_id.id,
                        "company_id": picking_id.company_id.id or self.env.company.id,
                        "lot_id": False,
                        "package_id": False,
                        "result_package_id": False,
                        "owner_id": picking_id.owner_id.id,
                    },
                )
            ],
        }
