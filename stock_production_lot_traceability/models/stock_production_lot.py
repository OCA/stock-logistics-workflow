# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    produce_lot_ids = fields.Many2many(
        string="Produced Lots/Serial Numbers",
        comodel_name="stock.production.lot",
        compute="_compute_produce_lot_ids",
        help="Lots that were directly or indirectly produced from this lot",
    )
    produce_lot_count = fields.Integer(
        string="Produced Lots/Serial Numbers Count",
        compute="_compute_produce_lot_ids",
    )
    consume_lot_ids = fields.Many2many(
        string="Consumed Lots/Serial Numbers",
        comodel_name="stock.production.lot",
        compute="_compute_consume_lot_ids",
        help="Lots that were directly or indirectly consumed to produce this lot",
    )
    consume_lot_count = fields.Integer(
        string="Consumed Lots/Serial Numbers Count",
        compute="_compute_consume_lot_ids",
    )

    def _compute_produce_lot_ids(self):
        """Compute the lots that were produced from this lot."""
        data = {}
        if self.ids:
            self.env["stock.move.line"].flush(
                ["state", "lot_id", "produce_line_ids", "consume_line_ids"]
            )
            self.env.cr.execute(
                """
                    WITH RECURSIVE produce_lots AS (
                        SELECT
                            consume_line.lot_id AS lot_id,
                            consume_line.lot_id AS consume_lot_id,
                            produce_line.lot_id AS produce_lot_id
                        FROM stock_move_line_consume_rel rel
                        INNER JOIN stock_move_line
                            AS consume_line
                            ON rel.produce_line_id = consume_line.id
                        INNER JOIN stock_move_line
                            AS produce_line
                            ON rel.consume_line_id = produce_line.id
                        WHERE consume_line.lot_id IN %s
                        AND   produce_line.lot_id IS NOT NULL
                        AND   consume_line.state = 'done'
                        AND   produce_line.state = 'done'
                        GROUP BY
                            consume_line.lot_id,
                            produce_line.lot_id
                    UNION
                        SELECT
                            produce_lots.lot_id AS lot_id,
                            consume_line.lot_id AS consume_lot_id,
                            produce_line.lot_id AS produce_lot_id
                        FROM stock_move_line_consume_rel rel
                        INNER JOIN stock_move_line
                            AS consume_line
                            ON rel.produce_line_id = consume_line.id
                        INNER JOIN stock_move_line
                            AS produce_line
                            ON rel.consume_line_id = produce_line.id
                        JOIN produce_lots
                            ON consume_line.lot_id = produce_lots.produce_lot_id
                        WHERE consume_line.lot_id IS NOT NULL
                        AND   produce_line.lot_id IS NOT NULL
                        AND   consume_line.state = 'done'
                        AND   produce_line.state = 'done'
                        GROUP BY
                            consume_line.lot_id,
                            produce_line.lot_id,
                            produce_lots.lot_id
                    )
                    SELECT lot_id, ARRAY_AGG(produce_lot_id) AS produce_lot_ids
                    FROM produce_lots
                    GROUP BY lot_id
                """,
                (tuple(self.ids),),
            )
            data = dict(self.env.cr.fetchall())
        for rec in self:
            produce_lot_ids = data.get(rec.id, [])
            rec.produce_lot_ids = [(6, 0, produce_lot_ids)]
            rec.produce_lot_count = len(produce_lot_ids)

    def _compute_consume_lot_ids(self):
        """Compute the lots that were consumed to produce this lot."""
        data = {}
        if self.ids:
            self.env["stock.move.line"].flush(
                ["state", "lot_id", "produce_line_ids", "consume_line_ids"]
            )
            self.env.cr.execute(
                """
                    WITH RECURSIVE consume_lots AS (
                        SELECT
                            produce_line.lot_id AS lot_id,
                            produce_line.lot_id AS produce_lot_id,
                            consume_line.lot_id AS consume_lot_id
                        FROM stock_move_line_consume_rel rel
                        INNER JOIN stock_move_line
                            AS consume_line
                            ON rel.produce_line_id = consume_line.id
                        INNER JOIN stock_move_line
                            AS produce_line
                            ON rel.consume_line_id = produce_line.id
                        WHERE produce_line.lot_id IN %s
                        AND   consume_line.lot_id IS NOT NULL
                        AND   produce_line.state = 'done'
                        AND   consume_line.state = 'done'
                        GROUP BY
                            produce_line.lot_id,
                            consume_line.lot_id
                    UNION
                        SELECT
                            consume_lots.lot_id AS lot_id,
                            produce_line.lot_id AS produce_lot_id,
                            consume_line.lot_id AS consume_lot_id
                        FROM stock_move_line_consume_rel rel
                        INNER JOIN stock_move_line
                            AS consume_line
                            ON rel.produce_line_id = consume_line.id
                        INNER JOIN stock_move_line
                            AS produce_line
                            ON rel.consume_line_id = produce_line.id
                        JOIN consume_Lots
                            ON produce_line.lot_id = consume_lots.consume_lot_id
                        WHERE consume_line.lot_id IS NOT NULL
                        AND   produce_line.lot_id IS NOT NULL
                        AND   consume_line.state = 'done'
                        AND   produce_line.state = 'done'
                        GROUP BY
                            consume_line.lot_id,
                            produce_line.lot_id,
                            consume_lots.lot_id
                    )
                    SELECT lot_id, ARRAY_AGG(consume_lot_id) AS consume_lot_ids
                    FROM consume_lots
                    GROUP BY lot_id
                """,
                (tuple(self.ids),),
            )
            data = dict(self.env.cr.fetchall())
        for rec in self:
            consume_lot_ids = data.get(rec.id, [])
            rec.consume_lot_ids = [(6, 0, consume_lot_ids)]
            rec.consume_lot_count = len(consume_lot_ids)

    def action_view_produce_lots(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_production_lot_form"
        )
        action["context"] = {}
        action["domain"] = [("id", "in", self.produce_lot_ids.ids)]
        action["name"] = _("Produced Lots")
        return action

    def action_view_consume_lots(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_production_lot_form"
        )
        action["context"] = {}
        action["domain"] = [("id", "in", self.consume_lot_ids.ids)]
        action["name"] = _("Consumed Lots")
        return action
