from openerp import models, api


class Quant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_get_prefered_domain(self, location, product, qty, domain=None,
                                   prefered_domain_list=[],
                                   restrict_lot_id=False,
                                   restrict_partner_id=False):
        if domain is None:
            domain = []

        my_partner = location.company_id.partner_id
        if restrict_partner_id == my_partner.id or not restrict_partner_id:
            domain += [
                '|',
                ('owner_id', '=', my_partner.id),
                ('owner_id', '=', False)
            ]
            restrict_partner_id = False
        else:
            domain += [
                ('owner_id', '=', restrict_partner_id),
            ]

        return super(Quant, self).quants_get_prefered_domain(
            location, product, qty, domain, prefered_domain_list,
            restrict_lot_id, restrict_partner_id)
