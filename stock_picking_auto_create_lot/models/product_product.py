from odoo import api, fields, models

from .res_config_settings import CONFIG_PARAM_SKU_TRAILING


class ProductProduct(models.Model):
    _inherit = "product.product"

    auto_create_lot_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Auto Lot/Serial Sequence",
        copy=False,
        help="Dedicated per-product sequence used for SKU-based lot/serial generation.",
    )

    @api.model
    def _auto_lot_get_trailing(self) -> int:
        """Return SKU-based numbers trailing (padding) from system settings.

        :return: Padding width (leading zeroes) for SKU-based numbers.
        :rtype: int
        """
        ir_config_value = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(CONFIG_PARAM_SKU_TRAILING, default="0")
        )
        try:
            trailing = int(ir_config_value)
        except (TypeError, ValueError):
            trailing = 0
        return max(trailing, 0)

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        products._auto_lot_sequence_sync_if_needed()
        return products

    def write(self, vals):
        res = super().write(vals)
        # SKU change affects prefix; company change affects sequence company
        if {"default_code", "company_id"} & set(vals):
            self._auto_lot_sequence_sync_if_needed()
        return res

    def unlink(self):
        """Delete related per-product sequences together with products.

        :return: Unlink result from super.
        :rtype: bool
        """
        sequences = self.auto_create_lot_sequence_id
        res = super().unlink()
        if sequences:
            sequences.sudo().unlink()
        return res

    def _auto_lot_sequence_sync_if_needed(self, trailing: int | None = None):
        """Create/update per-product sequence for SKU-based generation.

        Sequence is created only for products with:
          - auto_create_lot_option == 'sku_based' on template
          - non-empty SKU (default_code)

        Sequence properties:
          - prefix: '<SKU>-'
          - padding: trailing from settings
          - company_id: product company (or False)

        :param int trailing: Optional padding override.
          If not provided, taken from settings.
        """
        products = self.filtered(
            lambda p: p.product_tmpl_id.auto_create_lot_option == "sku_based"
            and p.default_code
        )
        if not products:
            return

        trailing = (
            self._auto_lot_get_trailing() if trailing is None else max(int(trailing), 0)
        )

        IrSequence = self.env["ir.sequence"].sudo()

        seq_vals_list: list[dict] = []
        create_products: list = []
        seq_updates: list[tuple] = []

        for product in products:
            prefix = f"{product.default_code}-"
            company_id = product.company_id.id or False
            seq = product.auto_create_lot_sequence_id

            if not seq:
                create_products.append(product)
                seq_vals_list.append(
                    {
                        "name": f"Lot/Serial for {product.default_code}",
                        "implementation": "standard",
                        "prefix": prefix,
                        "padding": trailing,
                        "number_next_actual": 1,
                        "number_increment": 1,
                        "company_id": company_id,
                    }
                )
                continue

            vals = {}
            if seq.prefix != prefix:
                vals["prefix"] = prefix
            if seq.padding != trailing:
                vals["padding"] = trailing
            if (seq.company_id.id or False) != company_id:
                vals["company_id"] = company_id

            if vals:
                seq_updates.append((seq, vals))

        if seq_vals_list:
            created = IrSequence.create(seq_vals_list)
            for product, seq in zip(create_products, created, strict=False):
                product.auto_create_lot_sequence_id = seq.id

        for seq, vals in seq_updates:
            seq.write(vals)
