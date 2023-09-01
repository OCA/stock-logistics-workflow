from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'


    def _gather_sanitized(self, location_id=None, lot_id=None, package_id=None):
        location_id = self.location_id if location_id is None else self.env['stock.location'].browse(location_id)
        lot_id = self.lot_id if lot_id is None else self.env['stock.production.lot'].browse(lot_id)
        package_id = self.package_id if package_id is None else self.env['stock.quant.package'].browse(package_id)

        return self.env['stock.quant']._gather(
            self.product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
        ).filtered(lambda q: q.lot_id == lot_id and q.package_id == package_id)

    def _will_cause_negative(self, qty=None, location_id=None, lot_id=None, package_id=None):
        self.ensure_one()

        is_forbidden = (
            not self.product_id.allow_negative_stock
            and not self.product_id.categ_id.allow_negative_stock
            and not self.location_id.allow_negative_stock
        )

        if self.product_id.type != 'product' or self.location_id.usage not in ['internal', 'transit'] or not is_forbidden:
            return False

        quants = self._gather_sanitized(
            location_id=location_id,
            lot_id=lot_id,
            package_id=package_id,
        )

        qty_done = self.qty_done if qty is None else qty
        total_qty_available = sum(quants.mapped('quantity') or [0])
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        if float_compare(total_qty_available, qty_done, precision_digits=precision) == -1:
            location_id = self.location_id if location_id is None else self.env['stock.location'].browse(location_id)
            raise ValidationError(_(
                    'You cannot validate this stock operation because the '
                    'stock level of the product %(name)s%(name_lot)s would '
                    'become negative '
                    '(%(q_quantity)s) on the stock location %(complete_name)s '
                    'and negative stock is '
                    'not allowed for this product and/or location.'
                ) % {
                    'name': self.product_id.display_name,
                    'name_lot': lot_id and ' lot %s' % lot_id.name_get()[0][1] or '',
                    'q_quantity': float_round(total_qty_available - qty_done, precision_digits=precision),
                    'complete_name': location_id.complete_name,
                })

    @api.model
    def create(self, vals):
        res = super(StockMoveLine, self).create(vals)

        if 'qty_done' in vals and vals['qty_done'] > 0:
            for rec in res:
                rec._will_cause_negative()

        return res

    def write(self, vals):
        if {'qty_done', 'location_id', 'package_id', 'lot_id'} & vals.keys():
            for rec in self:
                rec._will_cause_negative(qty=vals.get('qty_done'), location_id=vals.get('location_id'), package_id=vals.get('package_id'), lot_id=vals.get('lot_id'))

        return super(StockMoveLine, self).write(vals)
