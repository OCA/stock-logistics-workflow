# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class StockMoveDelayReport(models.Model):
    _name = "stock.move.delay.report"
    _description = "Delay Analysis Report"
    _auto = False

    date = fields.Date("Date Scheduled", readonly=True)
    move_id = fields.Many2one("stock.move", "Stock Move #", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    reference = fields.Char("Reference", readonly=True)
    location_src_id = fields.Many2one("stock.location", "From", readonly=True)
    location_dest_id = fields.Many2one("stock.location", "To", readonly=True)
    date_delay = fields.Float("Date Delay", group_operator="avg", readonly=True)
    done_on_time = fields.Float("Done on Time", group_operator="avg", readonly=True)
    product_uom = fields.Many2one("uom.uom", "Unit of Measure", readonly=True)
    responsible_id = fields.Many2one("res.partner", "Responsible", readonly=True)

    def _done_on_time(self):
        return """
            case when sm.date_delay > 0 then 0.0 else 100.0 end as done_on_time
        """

    def _select(self):
        return """
            sm.id,
            sm.date,
            sm.id AS move_id,
            sm.product_id,
            sm.reference,
            sm.location_id AS location_src_id,
            sm.location_dest_id,
            sm.date_delay,
            %s,
            sm.product_uom,
            sm.responsible_id
        """ % (
            self._done_on_time()
        )

    def _from(self):
        return """
            stock_move AS sm
        """

    def _query(self):
        return """
            (SELECT %s
            FROM %s
            WHERE sm.state = 'done' AND sm.responsible_id IS NOT NULL)
        """ % (
            self._select(),
            self._from(),
        )

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # pylint: disable=E8103
        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query())
        )
