# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


_logger = logging.getLogger(__name__)


class StockWarehouse(orm.Model):
    _inherit = 'stock.warehouse'

    _columns = {
        'reception_steps': fields.selection(
            [('one_step',
              'Receive goods directly in stock (1 step)'
              ),
             ('two_steps',
              'Unload in input location then go to stock (2 steps)'
              ),
             ('three_steps',
              'Unload in input location, go through a quality control before '
              'being admitted in stock (3 steps)'
              ),
             ('transit_one_step',
              'Receive goods directly in stock from Transit (transit + 1 step)'
              ),
             ('transit_two_steps',
              'Unload in input location from Transit then go to stock '
              '(transit + 2 steps)'
              ),
             ('transit_three_steps',
              'Unload in input location from Transit, go through a quality '
              'control before being admitted in stock (transit + 3 steps)'
              ),
             ],
            'Incoming Shipments',
            help="Default incoming route to follow", required=True),

        'delivery_steps': fields.selection(
            [('ship_only',
              'Ship directly from stock (Ship only)'
              ),
             ('pick_ship',
              'Bring goods to output location before shipping (Pick + Ship)'
              ),
             ('pick_pack_ship',
              'Make packages into a dedicated location, then bring them to '
              'the output location for shipping (Pick + Pack + Ship)'
              ),
             ('ship_transit',
              'Ship from stock to Transit location'
              ),
             ('pick_ship_transit',
              'Bring goods to output location before shipping to Transit'
              ),
             ('pick_pack_ship_transit',
              'Make packages into a dedicated location, then bring them to '
              'the output location for shipping to transit'
              ),
             ],
            'Outgoing Shippings',
            help="Default outgoing route to follow", required=True),

        'transit_in_type_id': fields.many2one('stock.picking.type',
                                              'In Transit Type'),
        'transit_out_type_id': fields.many2one('stock.picking.type',
                                               'Out Transit Type'),
        'wh_transit_in_loc_id': fields.many2one('stock.location',
                                                'Incoming Transit'),
        'wh_transit_out_loc_id': fields.many2one('stock.location',
                                                 'Outgoing Transit'),
    }

    def create(self, cr, uid, vals, context=None):
        transit_in, transit_out = self._create_transit_locations(
            cr, uid,
            vals.get('company_id'),
            vals.get('reception_steps', ''),
            vals.get('delivery_steps', ''),
            context)
        vals['wh_transit_in_loc_id'] = transit_in
        vals['wh_transit_out_loc_id'] = transit_out
        return super(StockWarehouse, self).create(cr, uid, vals, context)

    def _create_transit_locations(self, cr, uid,
                                  company_id,
                                  reception_steps,
                                  delivery_steps,
                                  context):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx['active_test'] = False
        data_obj = self.pool.get('ir.model.data')
        location_obj = self.pool.get('stock.location')
        try:
            out_id = data_obj.get_object_reference(
                cr, uid, 'stock_route_transit', 'transit_outgoing')[1]
        except:
            _logger.warning('missing ir_model_data: '
                            'stock_route_transit.transit_outgoing')
            out_id = location_obj.create(
                cr, uid,
                {'name': _('Outgoing Transit'),
                 'usage': 'transit',
                 'active': ('transit' in delivery_steps),
                 'company_id': company_id,
                 },
                context=ctx
                )
        in_id = location_obj.create(cr, uid,
                                    {'name': _('Incoming Transit'),
                                     'usage': 'transit',
                                     'active': ('transit' in reception_steps),
                                     'company_id': company_id,
                                     },
                                    context=ctx)
        return in_id, out_id

    def get_routes_dict(self, cr, uid, ids, warehouse, context=None):
        """return a dict of routes. Keys are the possible
        reception/delivery steps, values are tuples of 2 elements:
        1. the name of the route
        2. a list of 0, 1 or 2 tuples of (from_loc, dest_loc, pick_type_id),
           giving the different steps of the route.
        The list is processed by `_get_push_pull_rules`.

        """
        _super = super(StockWarehouse, self)
        routes_dict = _super.get_routes_dict(cr, uid, ids, warehouse, context)
        customer_loc, supplier_loc = self._get_partner_locations(
            cr, uid, ids, context=context)
        warehouse._ensure_transit_loc()
        new_routes = {
            'transit_one_step': (_('Receipt in 1 step from Transit'),
                                 [(warehouse.wh_transit_in_loc_id,
                                   warehouse.lot_stock_id,
                                   warehouse.in_type_id.id
                                   ),
                                  ]
                                 ),
            'transit_two_steps': (_('Receipt in 2 steps from Transit'),
                                  [(warehouse.wh_transit_in_loc_id,
                                    warehouse.wh_input_stock_loc_id,
                                    warehouse.in_type_id.id,
                                    ),
                                   (warehouse.wh_input_stock_loc_id,
                                    warehouse.lot_stock_id,
                                    warehouse.in_type_id.id,
                                    ),
                                   ]
                                  ),
            'transit_three_steps': (_('Receipt in 3 steps from Transit'),
                                    [(warehouse.wh_transit_in_loc_id,
                                      warehouse.wh_input_stock_loc_id,
                                      warehouse.in_type_id.id,
                                      ),
                                     (warehouse.wh_input_stock_loc_id,
                                      warehouse.wh_qc_stock_loc_id,
                                      warehouse.int_type_id.id
                                      ),
                                     (warehouse.wh_qc_stock_loc_id,
                                      warehouse.lot_stock_id,
                                      warehouse.int_type_id.id
                                      ),
                                     ]
                                    ),
            'ship_transit': (_('Ship to Transit'),
                             [(warehouse.lot_stock_id,
                               warehouse.wh_transit_out_loc_id,
                               warehouse.out_type_id.id
                               ),
                              (warehouse.wh_transit_out_loc_id,
                               customer_loc,
                               warehouse.transit_out_type_id.id
                               ),
                              ]
                             ),
            'pick_ship_transit': (_('Pick + Ship + Transit'),
                                  [(warehouse.lot_stock_id,
                                    warehouse.wh_output_stock_loc_id,
                                    warehouse.pick_type_id.id
                                    ),
                                   (warehouse.wh_output_stock_loc_id,
                                    warehouse.wh_transit_out_loc_id,
                                    warehouse.out_type_id.id
                                    ),
                                   (warehouse.wh_transit_out_loc_id,
                                    customer_loc,
                                    warehouse.transit_out_type_id.id
                                    ),
                                   ]
                                  ),
            'pick_pack_ship_transit': (_('Pick + Pack + Ship + Transit'),
                                       [(warehouse.lot_stock_id,
                                         warehouse.wh_pack_stock_loc_id,
                                         warehouse.pick_type_id.id
                                         ),
                                        (warehouse.wh_pack_stock_loc_id,
                                         warehouse.wh_output_stock_loc_id,
                                         warehouse.pack_type_id.id
                                         ),
                                        (warehouse.wh_output_stock_loc_id,
                                         warehouse.wh_transit_out_loc_id,
                                         warehouse.out_type_id.id
                                         ),
                                        (warehouse.wh_transit_out_loc_id,
                                         customer_loc,
                                         warehouse.transit_out_type_id.id
                                         ),
                                        ]
                                       ),
        }
        routes_dict.update(new_routes)
        return routes_dict

    def _ensure_transit_loc(self, cr, uid, ids, context=None):
        """make sure there are output and input transit location set
        and the picking types too

        they can be missing e.g. for warehouses created before the installation
        of the addon
        """
        for warehouse in self.browse(cr, uid, ids, context=context):
            if not (warehouse.wh_transit_out_loc_id
                    and warehouse.wh_transit_in_loc_id):
                # this can happen for warehouses created before this module was
                # installed
                in_id, out_id = self._create_transit_locations(
                    cr, uid,
                    warehouse.company_id.id,
                    warehouse.reception_steps,
                    warehouse.delivery_steps,
                    context)
                warehouse.write(
                    {'wh_transit_in_loc_id': in_id,
                     'wh_transit_out_loc_id': out_id})
            if not (warehouse.transit_in_type_id
                    and warehouse.transit_out_type_id):
                self._create_transit_sequences_and_picking_types(cr, uid,
                                                                 warehouse,
                                                                 context)

    def switch_location(self, cr, uid, ids,
                        warehouse,
                        new_reception_step=False,
                        new_delivery_step=False,
                        context=None):
        """set unused locations to active=False"""
        super(StockWarehouse, self).switch_location(cr, uid, ids,
                                                    warehouse,
                                                    new_reception_step,
                                                    new_delivery_step,
                                                    context)
        # we need to duplicate the code in stock because of hard coded
        # constants
        location_obj = self.pool.get('stock.location')
        new_reception_step = new_reception_step or warehouse.reception_steps
        new_delivery_step = new_delivery_step or warehouse.delivery_steps
        if warehouse.reception_steps != new_reception_step:
            if new_reception_step == 'transit_one_step':
                location_obj.write(cr, uid,
                                   warehouse.wh_input_stock_loc_id.id,
                                   {'active': False},
                                   context=context)
            if new_reception_step == 'transit_three_steps':
                location_obj.write(cr, uid,
                                   warehouse.wh_qc_stock_loc_id.id,
                                   {'active': True},
                                   context=context)

        if warehouse.delivery_steps != new_delivery_step:
            if new_delivery_step == 'ship_transit':
                location_obj.write(cr, uid,
                                   warehouse.wh_output_stock_loc_id.id,
                                   {'active': True},
                                   context=context)
            if new_delivery_step == 'pick_pack_ship_transit':
                location_obj.write(cr, uid,
                                   warehouse.wh_pack_stock_loc_id.id,
                                   {'active': True},
                                   context=context)
        warehouse._ensure_transit_loc()
        # incoming transit
        other_wh_ids = self.search(cr, uid,
                                   [('id', '!=', warehouse.id),
                                    ('wh_transit_in_loc_id', '=',
                                     warehouse.wh_transit_in_loc_id.id)
                                    ],
                                   context=context)
        other_wh = self.browse(cr, uid, other_wh_ids, context=context)
        transit_receptions = ['transit' in (new_reception_step or '')] + \
                             ['transit' in other.reception_steps
                              for other in other_wh]
        transit_in_active = any(transit_receptions)
        warehouse.wh_transit_in_loc_id.write({'active': transit_in_active})
        # outgoing transit
        other_wh_ids = self.search(cr, uid,
                                   [('id', '!=', warehouse.id),
                                    ('wh_transit_out_loc_id', '=',
                                     warehouse.wh_transit_out_loc_id.id)
                                    ],
                                   context=context)
        other_wh = self.browse(cr, uid, other_wh_ids, context=context)
        transit_deliveries = ['transit' in (new_delivery_step or '')] + \
                             ['transit' in other.delivery_steps
                              for other in other_wh]
        transit_out_active = any(transit_deliveries)
        warehouse.wh_transit_out_loc_id.write({'active': transit_out_active})
        return True

    def change_route(self, cr, uid, ids,
                     warehouse,
                     new_reception_step=False,
                     new_delivery_step=False,
                     context=None):
        """change input_loc, output_loc
        update active fiels on picking_types

                update location_dest (resp. src) of in (resp. out) picking type
        remove all routes of the WH and recreate them
        """
        super(StockWarehouse, self).change_route(cr, uid, ids,
                                                 warehouse,
                                                 new_reception_step,
                                                 new_delivery_step,
                                                 context)
        # due to poor design in base class, we need to redo everything... :-(
        # and add our stuff
        picking_type_obj = self.pool.get('stock.picking.type')
        route_obj = self.pool.get('stock.location.route')
        new_reception_step = new_reception_step or warehouse.reception_steps
        new_delivery_step = new_delivery_step or warehouse.delivery_steps
        if new_reception_step in ('transit_one_step', 'one_step'):
            input_loc = warehouse.lot_stock_id
        else:
            input_loc = warehouse.wh_input_stock_loc_id
        if new_delivery_step in ('ship_transit', 'ship_only'):
            output_loc = warehouse.lot_stock_id
        else:
            output_loc = warehouse.wh_output_stock_loc_id

        wh = warehouse
        picking_type_writes = [
            (wh.in_type_id.id, {'default_location_dest_id': input_loc.id}),
            (wh.out_type_id.id, {'default_location_src_id': output_loc.id}),
            (wh.pick_type_id.id,
             {'active': new_delivery_step in ('ship_only', 'ship_transit')}),
            (wh.pack_type_id.id,
             {'active': new_delivery_step.startswith('pick_pack_ship')}),
            (wh.transit_in_type_id.id,
             {'active': 'transit' in new_reception_step}),
            (wh.transit_out_type_id.id,
             {'active': 'transit' in new_reception_step}),
        ]
        for pick_type_id, vals in picking_type_writes:
            picking_type_obj.write(
                cr, uid, pick_type_id, vals, context=context)

        # fix active field of the crossdock route
        if new_reception_step.endswith('one_step'):
            cross_dock_active = False
        elif new_delivery_step in ('ship_transit', 'ship_only'):
            cross_dock_active = False
        else:
            cross_dock_active = True
        route_obj.write(cr, uid,
                        warehouse.crossdock_route_id.id,
                        {'active': cross_dock_active},
                        context=context)

        return True

    def create_sequences_and_picking_types(self, cr, uid,
                                           warehouse,
                                           context=None):
        _super = super(StockWarehouse, self)
        _super.create_sequences_and_picking_types(cr, uid, warehouse, context)
        self._create_transit_sequences_and_picking_types(cr, uid,
                                                         warehouse,
                                                         context)
        return True

    def _create_transit_sequences_and_picking_types(self, cr, uid,
                                                    warehouse,
                                                    context=None):
        seq_obj = self.pool.get('ir.sequence')
        picking_type_obj = self.pool.get('stock.picking.type')
        # create new sequences
        seq_values = {'name': warehouse.name + _(' Sequence incoming transit'),
                      'prefix': warehouse.code + '/TR-IN/',
                      'padding': 5}
        in_transit_seq_id = seq_obj.create(cr,
                                           SUPERUSER_ID,
                                           seq_values,
                                           context=context)
        seq_values = {'name': warehouse.name + _(' Sequence outgoing transit'),
                      'prefix': warehouse.code + '/TR-OUT/',
                      'padding': 5}
        out_transit_seq_id = seq_obj.create(cr,
                                            SUPERUSER_ID,
                                            seq_values,
                                            context=context)
        customer_loc, supplier_loc = self._get_partner_locations(
            cr, uid, warehouse.id, context=context)
        pick_type_val = {'name': _('In Transit'),
                         'warehouse_id': warehouse.id,
                         'code': 'incoming',
                         'sequence_id': in_transit_seq_id,
                         'default_location_src_id': supplier_loc.id,
                         'default_location_dest_id':
                             warehouse.wh_input_stock_loc_id.id,
                         'active': 'transit' in warehouse.reception_steps,
                         }
        in_transit_type = picking_type_obj.create(cr, uid,
                                                  pick_type_val,
                                                  context=context)
        pick_type_val = {'name': _('Out Transit'),
                         'warehouse_id': warehouse.id,
                         'code': 'outgoing',
                         'sequence_id': out_transit_seq_id,
                         'default_location_src_id':
                             warehouse.wh_output_stock_loc_id.id,
                         'default_location_dest_id': customer_loc.id,
                         'active': 'transit' in warehouse.delivery_steps,
                         }
        out_transit_type = picking_type_obj.create(cr, uid,
                                                   pick_type_val,
                                                   context=context)
        self.write(cr, uid, warehouse.id,
                   {'transit_in_type_id': in_transit_type,
                    'transit_out_type_id': out_transit_type,
                    },
                   context=context)
