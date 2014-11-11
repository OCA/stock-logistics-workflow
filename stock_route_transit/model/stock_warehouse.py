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

from openerp.osv import orm, fields

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
              'Make packages into a dedicated location, then bring them to the '
              'output location for shipping (Pick + Pack + Ship)'
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

        'transit_type_id': fields.many2one('stock.picking.type', 'Transit Type'),
        'wh_transit_in_loc_id': fields.many2one('stock.location', 'Incoming Transit'),
        'wh_transit_out_loc_id': fields.many2one('stock.location', 'Incoming Transit'),
        }


    def get_routes_dict(self, cr, uid, ids, warehouse, context=None):
        """
        return a dict of routes. Keys are the possible reception/delivery steps, values are tuples of 2 elements:
        1. the name of the route
        2. a list of 0, 1 or 2 tuples of (from_loc, dest_loc, pick_type_id), giving the different steps of the route. 
        The list is processed by `_get_push_pull_rules`.
        """
        _super = super(StockWarehouse, self)
        routes_dict = _super.get_routes_dict(cr, uid, ids, warehouse, context)
        return routes_dict
        customer_loc, supplier_loc = self._get_partner_locations(cr, uid, ids, context=context)
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
                               warehouse.transit_type_id.id
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
                                    warehouse.transit_type_id.id
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
                                         warehouse.transit_type_id.id
                                         ),
                                        ]
                                       ),
            }
        routes_dict.update(new_routes)
        return routes_dict


#    def switch_location(self, cr, uid, ids, warehouse, new_reception_step=False, new_delivery_step=False, context=None):
#        """set unused locations to active=False"""

#    def change_route(self, cr, uid, ids, warehouse, new_reception_step=False, new_delivery_step=False, context=None):
#        """change input_loc, output_loc
#        update active fiels on picking_types
#        update lication_dest (resp. src) of in (resp. out) picking type
#        remove all routes of the WH and recreate them
#        """ 

    def create_sequences_and_picking_types(self, cr, uid, warehouse, context=None):
        _super = super(StockWarehouse, self)
        _super.create_sequences_and_picking_types(cr, uid, warehouse, context)
        seq_obj = self.pool.get('ir.sequence')
        picking_type_obj = self.pool.get('stock.picking.type')
        # create new sequences
        in_transit_seq_id = seq_obj.create(cr,
                                           SUPERUSER_ID,
                                           values={'name': warehouse.name + _(' Sequence incoming transit'),
                                                   'prefix': warehouse.code+ '/TR-IN/',
                                                   'padding':5},
                                           context=context)
        out_transit_seq_id = seq_obj.create(cr,
                                            SUPERUSER_ID,
                                            values={'name': warehouse.name + _(' Sequence outgoing transit'),
                                                    'prefix': warehouse.code+ '/TR-OUT/',
                                                    'padding':5},
                                            context=context)
        
