# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    pack_weight = fields.Float("Weight (kg)")
    estimated_pack_weight = fields.Float(
        "Estimated weight (kg)",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_estimated_pack_weight",
        help="Based on the weight of the product.",
    )
    # lngth IS NOT A TYPO: https://github.com/odoo/odoo/issues/41353
    lngth = fields.Integer("Length (mm)", help="length in millimeters")
    width = fields.Integer("Width (mm)", help="width in millimeters")
    height = fields.Integer("Height (mm)", help="height in millimeters")
    volume = fields.Float(
        u"Volume (m³)",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
        help="volume in cubic meters",
    )

    def _get_picking_pack_operation_ids_per_package(self, picking_id):
        if not picking_id:
            return {}
        pack_operations = self.env["stock.pack.operation"].search(
            [
                ("result_package_id", "in", self.ids),
                ("picking_id", "=", picking_id),
            ]
        )
        res = dict.fromkeys(self.ids, self.env["stock.pack.operation"])
        for pop in pack_operations:
            res.setdefault(pop.result_package_id, set(pop.ids))
            res[pop.result_package_id].add(pop.id)
        return res

    def _get_weight_from_pack_operations(self, pack_operations):
        weigths = []
        for pop in pack_operations:
            product = pop.product_id or pop.package_id.single_product_id
            qty_done = pop.product_uom_id._compute_quantity(
                pop.qty_done, product.uom_id
            )
            weigth = pop.package_id.estimated_pack_weight or product.weight
            weigths.append(weigth * qty_done)
        return sum(weigths)

    @api.depends("quant_ids", "children_ids")
    def _compute_estimated_pack_weight(self):
        picking_id = self.env.context.get("picking_id")
        pack_operation_ids_per_package = (
            self._get_picking_pack_operation_ids_per_package(
                picking_id
            )
        )
        for package in self:
            weight = 0
            for quant in package.quant_ids:
                weight += quant.qty * quant.product_id.weight
            for pack in package.children_ids:
                pack._compute_weight()
                weight += pack.weight
            if (
                not package.quant_ids
                and not package.children_ids
                and picking_id
            ):
                # compute the height from the pricking if package is
                # the destination of some pack operations
                pack_operation_ids = pack_operation_ids_per_package.get(
                    package, []
                )
                pack_operations = self.env["stock.pack.operation"].browse(
                    pack_operation_ids
                )
                weight = package._get_weight_from_pack_operations(
                    pack_operations
                )

            package.estimated_pack_weight = weight

    @api.depends("lngth", "width", "height")
    def _compute_volume(self):
        for pack in self:
            pack.volume = (pack.lngth * pack.width * pack.height) / 1000.0 ** 3

    def auto_assign_packaging(self):
        self = self.with_context(_auto_assign_packaging=True)
        res = super(StockQuantPackage, self).auto_assign_packaging()
        return res

    def write(self, vals):
        res = super(StockQuantPackage, self).write(vals)
        if self.env.context.get("_auto_assign_packaging") and vals.get(
            "product_packaging_id"
        ):
            self._update_dimensions_from_packaging(override=False)
        return res

    def _update_dimensions_fields(self):
        # source: destination
        return {
            "lngth": "lngth",
            "width": "width",
            "height": "height",
            "max_weight": "pack_weight",
        }

    def _update_dimensions_from_packaging(self, override=False):
        for package in self:
            if not package.product_packaging_id:
                continue
            dimension_fields = self._update_dimensions_fields()
            for source, dest in dimension_fields.items():
                if not override and package[dest]:
                    continue
                package[dest] = package.product_packaging_id[source]

    @api.onchange("product_packaging_id")
    def onchange_product_packaging_id(self):
        self._update_dimensions_from_packaging(override=True)
