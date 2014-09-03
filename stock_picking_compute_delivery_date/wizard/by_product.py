from openerp.osv import orm


class ComputeDateWizard(orm.TransientModel):

    _name = 'compute.date.wizard'

    def do_compute(self, cr, uid, ids, context=None):
        pick_obj = self.pool['stock.picking.out']
        product_obj = self.pool['product.product']

        product_ids = context['active_ids']
        for product in product_obj.browse(cr, uid, product_ids,
                                          context=context):
            pick_obj.compute_delivery_dates(cr, uid, product, context=context)

        return True
