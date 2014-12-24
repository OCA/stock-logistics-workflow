from openerp import models


class Product(models.Model):
    _inherit = 'product.template'

    def action_open_quants(self, cr, uid, ids, context=None):
        result = super(Product, self).action_open_quants(cr, uid, ids, context)
        result['context'] = (
            "{'search_default_locationgroup': 1, "
            "'search_default_ownergroup': 1, "
            "'search_default_internal_loc': 1}"
        )
        return result
