# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero
from odoo.addons import decimal_precision as dp


class StockReturnRequest(models.Model):
    _name = 'stock.return.request'
    _description = 'Perform stock returns across pickings'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        'Reference',
        default=lambda self: _('New'),
        copy=False,
        readonly=True,
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    return_type = fields.Selection(
        selection=[
            ('supplier', 'Return to Supplier'),
            ('customer', 'Return from Customer'),
            ('internal', 'Return to Internal location'),
        ],
        string='Return type',
        required=True,
        help='Supplier - Search for incoming moves from this supplier\n'
             'Customer - Search for outgoing moves to this customer\n'
             'Internal - Search for outgoing moves to this location.',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    return_from_location = fields.Many2one(
        comodel_name='stock.location',
        string='Return from',
        help='Return from this location',
        required=True,
        domain='[("usage", "=", "internal")]',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    return_to_location = fields.Many2one(
        comodel_name='stock.location',
        string='Return to',
        help='Return to this location',
        required=True,
        domain='[("usage", "=", "internal")]',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    return_order = fields.Selection(
        selection=[
            ('date desc, id desc', 'Newer first'),
            ('date asc, id desc', 'Older first'),
        ],
        default='date desc, id desc',
        required=True,
        string='Return Order',
        help='The returns will be performed searching moves in '
             'the given order.',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    from_date = fields.Date(
        string="Search moves up to this date",
    )
    picking_types = fields.Many2many(
        comodel_name='stock.picking.type',
        string="Operation types",
        help="Restrict operation types to search for",
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Open'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange',
    )
    returned_picking_ids = fields.One2many(
        comodel_name='stock.picking',
        inverse_name='stock_return_request_id',
        string='Returned Pickings',
        readonly=True,
        copy=False,
    )
    to_refund = fields.Boolean(
        string="To refund",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    show_to_refund = fields.Boolean(
        compute='_compute_show_to_refund',
        default=lambda self: 'to_refund' in self.env['stock.move']._fields,
        readonly=True,
        help="Whether to show it or not depending on the availability of"
             "the stock_account module (so a bridge module is not necessary)",
    )
    line_ids = fields.One2many(
        comodel_name='stock.return.request.line',
        inverse_name='request_id',
        string='Stock Return',
        copy=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    note = fields.Text(
        string="Comments",
        help="They will be visible on the report",
    )

    @api.onchange('return_type', 'partner_id')
    def onchange_locations(self):
        """UI helpers to determine locations"""
        warehouse = self._default_warehouse_id()
        if self.return_type == 'supplier':
            self.return_to_location = (
                self.partner_id.property_stock_supplier)
            if self.return_from_location.usage != 'internal':
                self.return_from_location = warehouse.lot_stock_id.id
        if self.return_type == 'customer':
            self.return_from_location = (
                self.partner_id.property_stock_customer)
            if self.return_to_location.usage != 'internal':
                self.return_to_location = warehouse.lot_stock_id.id
        if self.return_type == 'internal':
            self.partner_id = False
            if self.return_to_location.usage != 'internal':
                self.return_to_location = warehouse.lot_stock_id.id
            if self.return_from_location.usage != 'internal':
                self.return_from_location = warehouse.lot_stock_id.id

    @api.model
    def _default_warehouse_id(self):
        warehouse = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.user.company_id.id),
        ], limit=1)
        return warehouse

    def _compute_show_to_refund(self):
        for one in self:
            if 'to_refund' not in self.env['stock.move']._fields:
                continue
            one.show_to_refund = True

    def _prepare_return_picking(self, picking_dict, moves):
        """Extend to add more values if needed"""
        picking_type = self.env['stock.picking.type'].browse(
            picking_dict.get('picking_type_id'))
        return_picking_type = (
            picking_type.return_picking_type_id or
            picking_type.return_picking_type_id)
        picking_dict.update({
            'move_lines': [(6, 0, moves.ids)],
            'move_line_ids': [
                (6, 0, moves.mapped('move_line_ids').ids)],
            'picking_type_id': return_picking_type.id,
            'state': 'draft',
            'origin': _("Return of %s") % picking_dict.get('origin'),
            'location_id': self.return_from_location.id,
            'location_dest_id': self.return_to_location.id,
            'stock_return_request_id': self.id,
        })
        return picking_dict

    def _create_picking(self, pickings, picking_moves):
        """Create return pickings with the proper moves"""
        return_pickings = self.env['stock.picking']
        for picking in pickings:
            picking_dict = picking.copy_data({
                'origin': picking.name,
                'printed': False,
            })[0]
            moves = picking_moves.filtered(
                lambda x:
                    x.origin_returned_move_id.picking_id == picking)
            new_picking = return_pickings.create(
                self._prepare_return_picking(picking_dict, moves))
            new_picking.message_post_with_view(
                'mail.message_origin_link',
                values={'self': new_picking, 'origin': picking},
                subtype_id=self.env.ref('mail.mt_note').id
            )
            return_pickings += new_picking
        return return_pickings

    def _prepare_move_default_values(self, line, qty, move):
        """Extend this method to add values to return move"""
        vals = {
            'product_id': line.product_id.id,
            'product_uom_qty': qty,
            'product_uom': line.product_uom_id.id,
            'state': 'draft',
            'location_id': line.request_id.return_from_location.id,
            'location_dest_id': line.request_id.return_to_location.id,
            'origin_returned_move_id': move.id,
            'procure_method': 'make_to_stock',
        }
        if self.show_to_refund:
            vals['to_refund'] = line.request_id.to_refund
        return vals

    def _prepare_move_line_values(self, line, return_move, qty):
        """Extend to add values to the move lines with lots"""
        return {
            'product_id': line.product_id.id,
            'product_uom_id': line.product_uom_id.id,
            'lot_id': line.lot_id.id,
            'location_id': return_move.location_id.id,
            'location_dest_id': return_move.location_dest_id.id,
            'qty_done': qty,
        }

    def action_confirm(self):
        """Wrapper for multi. Avoid recompute as it delays the pickings
           creation"""
        with self.env.norecompute():
            for one in self:
                one._action_confirm()
        self.recompute()

    def _action_confirm(self):
        """Get moves and then try to reserve quantities. Fail if the quantites
           can't be assigned"""
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_("Add some products to return"))
        returnable_moves = self.line_ids._get_returnable_move_ids()
        return_moves = self.env['stock.move']
        failed_moves = []
        done_moves = {}
        for line in returnable_moves.keys():
            for qty, move in returnable_moves[line]:
                if move not in done_moves:
                    vals = self._prepare_move_default_values(line, qty, move)
                    return_move = move.copy(vals)
                else:
                    return_move = done_moves[move]
                    return_move.product_uom_qty += qty
                done_moves.setdefault(move, self.env['stock.move'])
                done_moves[move] += return_move
                return_move._action_confirm()
                # We need to be deterministic with lots to avoid autoassign
                # thus we create manually the line
                if line.lot_id:
                    # We try to reserve the stock manually so we ensure there's
                    # enough to make the return.
                    if return_move.location_id.usage == 'internal':
                        try:
                            self.env['stock.quant']._update_reserved_quantity(
                                line.product_id, return_move.location_id, qty,
                                lot_id=line.lot_id, strict=True)
                        except UserError:
                            failed_moves.append((line, return_move))
                    vals = self._prepare_move_line_values(
                        line, return_move, qty)
                    return_move.write({
                        'move_line_ids': [(0, 0, vals)],
                    })
                    return_moves += return_move
                    line.returnable_move_ids += return_move
                # If not lots, just try standard assign
                else:
                    return_move._action_assign()
                    if return_move.state == 'assigned':
                        return_move.quantity_done = qty
                        return_moves += return_move
                        line.returnable_move_ids += return_move
                    else:
                        failed_moves.append((line, return_move))
                        break
        if failed_moves:
            failed_moves_str = "\n".join(
                ["{}: {} {:.2f}".format(
                    x[0].product_id.display_name,
                    x[0].lot_id.name or '\t',
                    x[0].quantity) for x in failed_moves]
            )
            raise ValidationError(_(
                "It wasn't possible to assign stock for this returns:\n"
                "%s" % failed_moves_str))
        # Finish move traceability
        for move in return_moves:
            vals = {}
            origin_move = move.origin_returned_move_id
            move_orig_to_link = origin_move.move_dest_ids.mapped(
                'returned_move_ids')
            move_dest_to_link = origin_move.move_orig_ids.mapped(
                'returned_move_ids')
            vals['move_orig_ids'] = [
                (4, m.id) for m in move_orig_to_link | origin_move]
            vals['move_dest_ids'] = [
                (4, m.id) for m in move_dest_to_link]
            move.write(vals)
        # Make return pickings and link to the proper moves.
        origin_pickings = return_moves.mapped(
            'origin_returned_move_id.picking_id')
        self.returned_picking_ids = self._create_picking(
            origin_pickings, return_moves)
        self.state = 'confirmed'

    def action_validate(self):
        """Wrapper for multi"""
        for one in self:
            one._action_validate()

    def _action_validate(self):
        self.returned_picking_ids.action_done()
        self.state = 'done'

    def action_cancel_to_draft(self):
        """Set to draft again"""
        self.filtered(lambda x: x.state == 'cancel').write({'state': 'draft'})

    def action_cancel(self):
        """Cancel request and the associated pickings. We can set it to
           draft again."""
        self.filtered(lambda x: x.state == 'draft').write({'state': 'cancel'})
        confirmed = self.filtered(lambda x: x.state == 'confirmed')
        for return_request in confirmed:
            return_request.mapped('returned_picking_ids').action_cancel()
            return_request.state = 'cancel'

    @api.model
    def create(self, vals):
        if 'name' not in vals or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'stock.return.request') or _('New')
        return super().create(vals)

    def action_view_pickings(self):
        """Display returned pickings"""
        action = self.env.ref('stock.action_picking_tree_all')
        result = action.read()[0]
        result['context'] = {}
        pickings = self.mapped('returned_picking_ids')
        if not pickings or len(pickings) > 1:
            result['domain'] = "[('id', 'in', %s)]" % (pickings.ids)
        elif len(pickings) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pickings.id
        return result

    def do_print_return_request(self):
        return self.env.ref(
            'stock_return_request'
            '.action_report_stock_return_request').report_action(self)


class StockReturnRequestLine(models.Model):
    _name = 'stock.return.request.line'
    _description = 'Product to search for returns'

    request_id = fields.Many2one(
        comodel_name='stock.return.request',
        string='Return Request',
        ondelete='cascade',
        required=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        domain=[('type', '=', 'product')],
    )
    product_uom_id = fields.Many2one(
        comodel_name='product.uom',
        related='product_id.uom_id',
        readonly=True,
    )
    tracking = fields.Selection(
        related='product_id.tracking',
        readonly=True,
    )
    lot_id = fields.Many2one(
        comodel_name='stock.production.lot',
        string='Lot / Serial',
    )
    quantity = fields.Float(
        string='Quantiy to return',
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
    )
    max_quantity = fields.Float(
        string='Maximum available quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )
    returnable_move_ids = fields.Many2many(
        comodel_name='stock.move',
        string='Returnable Move Lines',
        copy=False,
        readonly=True,
    )

    def _get_moves_domain(self):
        """Domain constructor for moves search"""
        self.ensure_one()
        domain = [
            ('state', '=', 'done'),
            ('origin_returned_move_id', '=', False),
            ('qty_returnable', '>', 0),
            ('product_id', '=', self.product_id.id),
            ('picking_id.partner_id', 'child_of',
                self.request_id.partner_id.commercial_partner_id.id),
            ('move_line_ids.lot_id', '=', self.lot_id.id),
        ]
        if self.request_id.from_date:
            domain += [('date', '>=', self.request_id.from_date)]
        if self.request_id.picking_types:
            domain += [
                ('picking_id.picking_type_id', 'in',
                    self.request_id.picking_types.ids)]
        return_type = self.request_id.return_type
        if return_type != 'internal':
            domain += [
                ('picking_id.partner_id', 'child_of',
                    self.request_id.partner_id.commercial_partner_id.id)]
        # Search for movements coming delivered to that location
        if return_type in ['internal', 'customer']:
            domain += [
                ('location_dest_id', '=',
                    self.request_id.return_from_location.id)]
        # Return to supplier. Search for moves that came from that location
        else:
            domain += [
                ('location_id', '=',
                    self.request_id.return_to_location.id)]
        return domain

    def _get_returnable_move_ids(self):
        """Gets returnable stock.moves for the given request conditions

        :returns: a dict with request lines as keys containing a list of tuples
                  with qty returnable for a given move as the move itself
        :rtype: dictionary
        """
        moves_for_return = {}
        stock_move_obj = self.env['stock.move']
        # Avoid lines with quantity to 0.0
        for line in self.filtered('quantity'):
            moves_for_return[line] = []
            precision = line.product_uom_id.rounding
            moves = stock_move_obj.search(
                line._get_moves_domain(),
                order=line.request_id.return_order)
            # Add moves up to desired quantity
            qty_to_complete = line.quantity
            for move in moves:
                qty_returned = 0
                return_moves = move.returned_move_ids.filtered(
                    lambda x: x.state == 'done')
                # Don't count already returned
                if return_moves:
                    qty_returned = -sum(
                        return_moves.mapped(
                            'move_line_ids').filtered(
                                lambda x: x.lot_id == line.lot_id).mapped(
                                    'qty_done'))
                quantity_done = sum(move.mapped(
                    'move_line_ids').filtered(
                        lambda x: x.lot_id == line.lot_id).mapped('qty_done'))
                qty_remaining = quantity_done - qty_returned
                # We add the move to the list if there are units that haven't
                # been returned
                if float_compare(
                        qty_remaining, 0.0, precision_rounding=precision) > 0:
                    qty_to_return = min(qty_to_complete, qty_remaining)
                    moves_for_return[line] += [(qty_to_return, move)]
                    qty_to_complete -= qty_to_return
                if float_is_zero(qty_to_complete,
                                 precision_rounding=precision):
                    break
            if qty_to_complete:
                qty_found = line.quantity - qty_to_complete
                raise ValidationError(_(
                    "Not enough moves to return this product.\n"
                    "It wasn't possible to find enough moves to return %f %s"
                    "of %s. A maximum of %f can be returned." % (
                        line.quantity, line.product_uom_id.name,
                        line.product_id.display_name, qty_found)))
        return moves_for_return

    @api.model
    def create(self, values):
        res = super().create(values)
        existing = self.search([
            ('product_id', '=', res.product_id.id),
            ('request_id.state', 'in', ['draft', 'confirm']),
            ('request_id.return_from_location', '=',
                res.request_id.return_from_location.id),
            ('request_id.return_to_location', '=',
                res.request_id.return_to_location.id),
            ('request_id.partner_id', 'child_of',
                res.request_id.partner_id.commercial_partner_id.id),
            ('lot_id', '=', res.lot_id.id),
        ])
        if len(existing) > 1:
            raise UserError(_("""
                You cannot have two open Stock Return Requests with the same
                product (%s), locations (%s, %s) partner (%s) and lot.\n
                Please first validate the first return request with this
                product before creating a new one.
                """) % (res.product_id.display_name,
                        res.return_from_location.display_name,
                        res.return_to_location.display_name,
                        res.request_id.partner_id.name))
        return res

    @api.onchange('product_id', 'lot_id')
    def onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id
        request = self.request_id
        if request.return_type == 'customer':
            return
        search_args = [
            ('location_id', '=', request.return_from_location.id),
            ('product_id', '=', self.product_id.id),
        ]
        if self.lot_id:
            search_args.append(('lot_id', '=', self.lot_id.id))
        else:
            search_args.append(('lot_id', '=', False))
        res = self.env['stock.quant'].read_group(search_args, ['quantity'], [])
        max_quantity = res[0]['quantity']
        self.max_quantity = max_quantity
