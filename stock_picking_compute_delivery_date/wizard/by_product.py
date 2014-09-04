from openerp.osv import orm


class ComputeDeliveryDateByProductWizard(orm.TransientModel):

    _name = 'compute.delivery.date.by.product.wizard'

    def do_compute(self, cr, uid, ids, context=None):
        pick_obj = self.pool['stock.picking.out']
        product_obj = self.pool['product.product']

        product_ids = context['active_ids']
        for product in product_obj.browse(cr, uid, product_ids,
                                          context=context):
            pick_obj.compute_delivery_dates(cr, uid, product, context=context)

        return True


class ComputeAllDeliveryDatesWizard(orm.TransientModel):

    _name = 'compute.all.delivery.dates.wizard'

    def do_compute(self, cr, uid, ids, context=None):
        pick_obj = self.pool['stock.picking.out']
        pick_obj.compute_all_delivery_dates(cr, uid, context=context)

        return True
