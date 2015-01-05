from openerp import models, api, fields


class Quant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self, vals):
        """Set the owner based on the location.

        This is not a method because we need to know the location.

        """
        if not vals.get('owner_id'):
            Company = self.env['res.company']
            location = self.env['stock.location'].browse(vals['location_id'])

            vals['owner_id'] = (
                location.partner_id.id
                or location.company_id.partner_id.id
                or Company.browse(
                    Company._company_default_get('stock.quant')
                ).partner_id.id
            )

        return super(Quant, self).create(vals)

    owner_id = fields.Many2one('res.partner', 'Owner',
                               help="This is the owner of the quant",
                               readonly=True,
                               select=True,
                               required=True)

    @api.model
    def quants_get_prefered_domain(self, location, product, qty, domain=None,
                                   prefered_domain_list=None,
                                   restrict_lot_id=False,
                                   restrict_partner_id=False):
        if domain is None:
            domain = []
        if prefered_domain_list is None:
            prefered_domain_list = []

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
