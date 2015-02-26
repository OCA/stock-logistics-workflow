# -*- coding: utf-8 -*-
#
#
#    Author: Yannick Vaucher
#    Copyright 2015 Camptocamp SA
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
#
from openerp import models, api, fields, exceptions, _


class ShipmentPlanCreator(models.TransientModel):

    """Create a shipment plan from stock.picking or stock move.
    This will take all related stock move from the selected picking
    and put them in the shipment plan."""

    _name = 'shipment.plan.creator'
    _description = 'Shipment Plan Creator'

    shipment_id = fields.Many2one(
        'shipment.plan', 'Shipment',
        domain="[('state', '=', 'draft'),"
               " ('from_address_id', '=', from_address_id),"
               " ('to_address_id', '=', to_address_id)]",
        help="Shipment to which moves will be added.\nOnly shipment in draft "
             "can be extended.",
    )

    move_ids = fields.One2many(
        compute=lambda rec: True,
        comodel_name='stock.move',
        string='Selected Moves',
    )

    initial_etd = fields.Datetime(
        'Initial ETD',
        help="Initial Estimated Time of Departure"
    )
    initial_eta = fields.Datetime(
        'Initial ETA',
        help="Initial Estimated Time of Arrival"
    )
    from_address_id = fields.Many2one(
        'res.partner', 'From Address',
        readonly=True,
    )
    to_address_id = fields.Many2one(
        'res.partner',
        'To Address',
        readonly=True,
    )
    consignee_id = fields.Many2one(
        'res.partner',
        'Consignee',
    )
    carrier_tracking_ref = fields.Char(
        'Tracking Ref.',
    )

    @api.model
    def _get_shipment_data(self, moves):
        """ Create arrival moves based on departure moves

        """
        data = {}
        from_addresses = moves.mapped('ship_from_address_id')
        if len(from_addresses) > 1:
            raise exceptions.Warning("Multiple From Address")
        to_addresses = moves.mapped('ship_to_address_id')
        if len(to_addresses) > 1:
            raise exceptions.Warning("Multiple To Address")
        data.update(
            from_address_id=from_addresses.id,
            to_address_id=to_addresses.id
        )

        etds = set(m.date_expected for m in moves)
        etas = set(m.move_dest_id.date_expected for m in moves)
        if len(etds) == 1:
            data['initial_etd'] = etds.pop()
        if len(etas) == 1:
            data['initial_eta'] = etas.pop()
        tracking_refs = set(m.picking_id.carrier_tracking_ref for m in moves)
        if len(tracking_refs) == 1:
            data['carrier_tracking_ref'] = tracking_refs.pop()
        return data

    @api.model
    def default_get(self, fields_list):
        """ Take the pricelist of the lrs by default. Show the
        available choice for the user.
        """
        defaults = super(ShipmentPlanCreator, self).default_get(fields_list)

        model = self.env.context['active_model']
        active_ids = self.env.context['active_ids']
        recs = self.env[model].browse(active_ids)
        if model == 'stock.picking':
            recs = recs.mapped('move_lines')
        defaults['move_ids'] = recs.ids
        data = self._get_shipment_data(recs)
        defaults.update(data)
        return defaults

    def _check_departure_moves(self):
        """ Departure moves checks:

          - not already assigned to a shipment plan
          - in confirmed, waiting or assigned state
          - going to transit location
          - have chained move defined

          After check there should be at least one move to allow
          shipment creation.
        """
        mvs_already_shipped = self.move_ids.filtered('departure_shipment_id')
        residual = self.move_ids - mvs_already_shipped
        mvs_wrong_state = residual.filtered(
            lambda rec: rec.state not in ('confirmed', 'waiting', 'assigned'))
        residual -= mvs_wrong_state
        mvs_not_transit = residual.filtered(
            lambda rec: rec.location_dest_id.usage != 'transit')
        residual -= mvs_not_transit
        mvs_no_dest = residual.filtered(
            lambda rec: not rec.move_dest_id)
        mvs_ok = residual - mvs_no_dest
        if not mvs_ok:
            problems = [
                _("No valid stock moves found to create the shipment!"),
                _("(Only transit move that are not departure moves of a "
                  "shipment plan and in confirm, waiting or assigned state can"
                  " be used)")
            ]
            msg_shipped = _('Shipment %s already covers moves %s')
            cover_shipments = mvs_already_shipped.mapped(
                'departure_shipment_id')
            for ship in cover_shipments:
                mvs = mvs_already_shipped.filtered(
                    lambda rec: rec.departure_shipment_id == ship)
                str_mvs = u', '.join(['%s [%s]' % (mv.id, mv.name)
                                     for mv in mvs])
                problems.append(msg_shipped % (ship.name, str_mvs))

            msg_wrong_state = _('Moves %s from picking %s are in state %s')
            states = set(mvs_wrong_state.mapped('state'))
            pickings = mvs_wrong_state.mapped('picking_id')
            for pick in pickings:
                for state in states:
                    mvs = mvs_wrong_state.filtered(
                        lambda rec:
                            rec.picking_id == pick and
                            rec.state == state)
                    if mvs:
                        str_mvs = u', '.join(['%s [%s]' % (mv.id, mv.name)
                                             for mv in mvs])
                        problems.append(msg_wrong_state
                                        % (str_mvs,
                                           pick.name, state))
            if mvs_not_transit:
                msg_not_transit = _("Moves %s are not going to Transit.")
                str_mvs = u', '.join(['%s [%s]' % (mv.id, mv.name)
                                     for mv in mvs_not_transit])
                problems.append(msg_not_transit % str_mvs)
            if mvs_no_dest:
                msg_no_dest = _("Moves %s have no chained move set.")
                str_mvs = u', '.join(['%s [%s]' % (mv.id, mv.name)
                                     for mv in mvs_no_dest])
                problems.append(msg_no_dest % str_mvs)

            raise exceptions.Warning(u'\n'.join(problems))
        return True

    @api.multi
    def _compute_shipment_data(self):
        """ Compute shipment data from wizard values

        """
        data = {}
        for field in ['from_address_id', 'to_address_id']:
            rec = self[field]
            if rec:
                data[field] = rec.id
        for field in ['initial_etd', 'initial_eta', 'carrier_tracking_ref']:
            data[field] = self[field]
        return data

    @api.multi
    def action_create_shipment(self):
        """ Create the shipment
        """
        model = self.env.context['active_model']
        active_ids = self.env.context['active_ids']
        recs = self.env[model].browse(active_ids)
        if model == 'stock.picking':
            recs = recs.mapped('move_lines')

        self.move_ids = recs

        self._check_departure_moves()
        if not self.shipment_id:
            data = self._compute_shipment_data()
            self.shipment_id = self.env['shipment.plan'].create(data)
        # for move_id in move_ids:
        recs.write({'departure_shipment_id': self.shipment_id.id})
        dest_moves = recs.mapped('move_dest_id')
        dest_moves.write({'arrival_shipment_id': self.shipment_id.id})

        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('shipment_id')
    def onchange_shipment(self):
        if self.shipment_id:
            copy_fields = [
                'initial_etd', 'initial_eta',
                'from_address_id', 'to_address_id',
                'consignee_id', 'carrier_tracking_ref']
            for field in copy_fields:
                self[field] = self.shipment_id[field]
