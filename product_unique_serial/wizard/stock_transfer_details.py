# -*- coding: utf-8 -*-

from lxml import etree

from openerp import models, api


# TODO: Looking for how append domain string
def domain_str_append(old_domain_str, subdomain_str):
    return old_domain_str.replace(
        "]",
        ", " + subdomain_str + "]")


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """
        Allow create serial only with incoming picking
        Set option "no_create = True"
        when picking type is different to incoming.
        """
        res = super(StockTransferDetails, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        context = self._context
        if 'item_ids' in res['fields']:
            arch = res['fields']['item_ids'][
                'views']['tree']['arch']
            doc = etree.XML(arch)
            if context.get('active_model') == 'stock.picking' \
               and context.get('active_id'):
                picking = self.env['stock.picking'].\
                    browse(context['active_id'])
                for node in doc.xpath("//field[@name='lot_id']"):
                    if picking.picking_type_id.code != 'incoming':
                        node.set('options', "{'no_create': True}")
                        # Don't show unused serial.
                        # allow to select a serial with moves.
                        # TODO: Disable this option when
                        #       fields.function last_location_id
                        #       was fix it
                        sub_domain = "('quant_ids', '!=', [])"
                        # Set domain to show only serial number
                        # that exists in source location
                        # TODO: Enable when fields.function
                        #       last_location_id was fix it
                        # sub_domain = "('last_location_id', '=', " + \
                        #     "sourceloc_id)"
                    else:
                        # Don't show old serial number
                        # just allow to create new one or
                        # allow to select a serial without moves
                        sub_domain = "('quant_ids', '=', [])"
                    new_domain = domain_str_append(
                        node.get('domain'), sub_domain)
                    node.set('domain', new_domain)
                res['fields']['item_ids']['views'][
                    'tree']['arch'] = etree.tostring(doc)
        return res
