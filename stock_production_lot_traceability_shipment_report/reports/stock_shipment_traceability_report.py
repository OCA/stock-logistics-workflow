# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from textwrap import dedent, indent

from odoo import api, fields, models, tools


class StockMoveLineDeliveryReport(models.Model):
    _name = "stock.shipment.traceability.report"
    _description = "Analysis on received/delivered stock lines"
    _auto = False
    _order = "date asc"

    name = fields.Char(readonly=True)
    date = fields.Datetime(readonly=True)
    usage = fields.Selection(
        selection=[("customer", "Customer"), ("supplier", "Supplier")],
        readonly=True,
    )
    direction = fields.Selection([("in", "In"), ("out", "Out")], readonly=True)
    kind = fields.Selection(
        [
            ("reception", "Reception"),
            ("in_return", "Supplier Return"),
            ("delivery", "Delivery"),
            ("out_return", "Customer Return"),
        ],
        readonly=True,
    )
    move_id = fields.Many2one("stock.move", "Move", readonly=True)
    group_id = fields.Many2one("procurement.group", "Procurement Group", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    product_uom_id = fields.Many2one("uom.uom", "Unit of Measure", readonly=True)
    product_uom_qty = fields.Float("Quantity", readonly=True)
    product_uom_qty_directed = fields.Float(
        "Quantity (directed)",
        help="Quantity directed to the customer/supplier.",
        readonly=True,
    )
    picking_id = fields.Many2one("stock.picking", "Picking", readonly=True)
    owner_id = fields.Many2one("res.partner", "Owner", readonly=True)
    location_id = fields.Many2one("stock.location", "From", readonly=True)
    location_dest_id = fields.Many2one("stock.location", "To", readonly=True)
    origin = fields.Char(readonly=True)
    reference = fields.Char(readonly=True)
    lot_id = fields.Many2one("stock.production.lot", "Lot/Serial Number", readonly=True)
    company_id = fields.Many2one("res.company", "Company", readonly=True)
    partner_id = fields.Many2one("res.partner", "Partner", readonly=True)

    def _with_expressions(self):
        return []

    def _with(self):
        expressions = self._with_expressions()
        return ("WITH %s" % ", ".join(expressions)) if expressions else ""

    def _select_fields(self):
        return {
            "id": "sml.id",
            "name": "sm.name",
            "date": "sml.date",
            "usage": """
                COALESCE(
                    NULLIF(sl_from.usage, 'internal'),
                    NULLIF(sl_dest.usage, 'internal')
                )
            """,
            "direction": """
                (
                    CASE
                    WHEN sl_from.usage = 'internal' THEN 'out'
                    ELSE 'in'
                    END
                )
            """,
            "kind": """
                (
                    CASE
                    WHEN sl_dest.usage = 'customer' THEN 'delivery'
                    WHEN sl_from.usage = 'supplier' THEN 'reception'
                    WHEN sl_from.usage = 'customer' THEN 'out_return'
                    WHEN sl_dest.usage = 'supplier' THEN 'in_return'
                    END
                )
            """,
            "move_id": "sml.move_id",
            "group_id": "sm.group_id",
            "product_id": "sml.product_id",
            "product_uom_id": "pt.uom_id",
            "product_uom_qty": """
                (
                    CASE
                    WHEN sl_from.usage = 'internal' THEN -sml.qty_done
                    ELSE sml.qty_done
                    END
                )
            """,
            "product_uom_qty_directed": """
                CASE
                WHEN sl_from.usage = 'internal'
                THEN -sml.qty_done
                ELSE sml.qty_done
                END
                *
                CASE
                WHEN (
                    COALESCE(
                        NULLIF(sl_from.usage, 'internal'),
                        NULLIF(sl_dest.usage, 'internal')
                    )
                    = 'customer'
                )
                THEN -1
                ELSE 1
                END
            """,
            "picking_id": "sm.picking_id",
            "owner_id": "sml.owner_id",
            "location_id": "sml.location_id",
            "location_dest_id": "sml.location_dest_id",
            "origin": "sm.origin",
            "reference": "sm.reference",
            "lot_id": "sml.lot_id",
            "company_id": "sm.company_id",
            "partner_id": "sp.partner_id",
        }

    def _select_expressions(self):
        return [
            "%s AS %s" % (dedent(expr).strip(), fname)
            for fname, expr in self._select_fields().items()
        ]

    def _select(self):
        indented_expressions = (
            indent(expr, "    ") for expr in self._select_expressions()
        )
        return "SELECT\n%s" % ",\n".join(indented_expressions)

    def _from(self):
        return "FROM stock_move_line sml"

    def _join_expressions(self):
        return [
            "INNER JOIN stock_move sm ON sm.id = sml.move_id",
            "INNER JOIN stock_picking sp ON sp.id = sm.picking_id",
            "INNER JOIN product_product pp ON pp.id = sml.product_id",
            "INNER JOIN product_template pt ON pt.id = pp.product_tmpl_id",
            "INNER JOIN stock_location sl_from ON sl_from.id = sml.location_id",
            "INNER JOIN stock_location sl_dest ON sl_dest.id = sml.location_dest_id",
        ]

    def _join(self):
        return "\n".join(self._join_expressions())

    def _where_expressions(self):
        return [
            "sml.state = 'done'",
            """
            (
                (
                    sl_from.usage = 'internal'
                    AND sl_dest.usage IN ('customer', 'supplier')
                ) OR (
                    sl_from.usage IN ('customer', 'supplier')
                    AND sl_dest.usage = 'internal'
                )
            )
            """,
        ]

    def _where(self):
        expressions = self._where_expressions()
        return "WHERE %s" % "\nAND ".join(expressions) if expressions else ""

    def _groupby_expressions(self):
        return []

    def _groupby(self):
        expressions = self._groupby_expressions()
        return "GROUP BY %s" % ", ".join(expressions) if expressions else ""

    def _query(self):
        return "\n".join(
            (
                self._with(),
                self._select(),
                self._from(),
                self._join(),
                self._where(),
                self._groupby(),
            )
        )

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            "CREATE or REPLACE VIEW %s AS (%s)" % (self._table, self._query())
        )
