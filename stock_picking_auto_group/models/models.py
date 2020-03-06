# -*- coding: utf-8 -*-
#
# Copyright 2020 Ryan Cole (www.ryanc.me)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class StockPickingType(models.Model):
	_inherit = 'stock.picking.type'

	create_procurement_group = fields.Boolean(string='Create Group', help='Automatically create procurement groups for stock transfers originating from this picking type', default=False)


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	@api.model
	def create(self, values):
		# copied from official Odoo code. we need the name field to generate a procurement group,
		# but the default create() is not easily overridable in this case.
		defaults = self.default_get(['name', 'picking_type_id'])
		if values.get('name', '/') == '/' and defaults.get('name', '/') == '/' and values.get('picking_type_id', defaults.get('picking_type_id')):
			values['name'] = self.env['stock.picking.type'].browse(values.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()


		#_logger.warn(str(values))
		picking_type_id = self.env['stock.picking.type'].browse(values['picking_type_id'])
		if picking_type_id.create_procurement_group:
			moves_nogroup = []

			# this might not be strictly necessary - it is very unlikely (impossible?) 
			# that _some_ moves have a group, and _some_ don't.
			for stock_move_data in values.get('move_lines', []):

				# move lines come in the x2x-update format:
				# e.g. tuple(0, 0, {values})
				if not stock_move_data[2].get('group_id', False):
					moves_nogroup.append(stock_move_data)

			if len(moves_nogroup) > 0:
				procurement_group = self.env['procurement.group'].create({'name': values.get('name', False), 'move_type': 'direct'})

				# assign it
				for move in moves_nogroup:
					move[2]['group_id'] = procurement_group.id

		return super(StockPicking, self).create(values)

	@api.multi
	def write(self, values):
		for record in self:
			if record.picking_type_id.create_procurement_group:

				# ensure that new lines inherit the parent stock.picking's group
				for stock_move_data in values.get('move_lines', []):
					if not stock_move_data[2].get('group_id', False):
						stock_move_data[2]['group_id'] = record.group_id.id

		super(StockPicking, self).write(values)