# -*- coding: utf-8 -*-
# © 2011 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp import fields
from openerp import api

import logging
logger = logging.getLogger('stock_scanner')


class ScannerScenarioCustom(models.Model):
    _name = 'scanner.scenario.custom'
    _description = 'Temporary value for scenario'

    _rec_name = "scenario_id"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    scenario_id = fields.Many2one(
        'scanner.scenario',
        string='Scenario',
        required=False,
        ondelete='cascade',
        help='Values used for this scenario.')
    scanner_id = fields.Many2one(
        'scanner.hardware',
        string='Scanner',
        required=False,
        ondelete='cascade',
        help='Values used for this scanner.')
    model = fields.Char(
        string='Model',
        required=True,
        help='Model used for these data.')
    res_id = fields.Integer(
        string='Values id',
        default=0,
        required=True,
        help='ID of the model source.')
    char_val1 = fields.Char(
        string='Char Value 1',
        default='',
        required=False,
        help='Temporary char value.')
    char_val2 = fields.Char(
        string='Char Value 2',
        default='',
        required=False,
        help='Temporary char value.')
    char_val3 = fields.Char(
        string='Char Value 3',
        default='',
        required=False,
        help='Temporary char value.')
    char_val4 = fields.Char(
        string='Char Value 4',
        default='',
        required=False,
        help='Temporary char value.')
    char_val5 = fields.Char(
        string='Char Value 5',
        default='',
        required=False,
        help='Temporary char value.')
    int_val1 = fields.Integer(
        string='Int Value 1',
        default=0,
        required=False,
        help='Temporary int value.')
    int_val2 = fields.Integer(
        string='Int Value 2',
        default=0,
        required=False,
        help='Temporary int value.')
    int_val3 = fields.Integer(
        string='Int Value 3',
        default=0,
        required=False,
        help='Temporary int value.')
    int_val4 = fields.Integer(
        string='Int Value 4',
        default=0,
        required=False,
        help='Temporary int value.')
    int_val5 = fields.Integer(
        string='Int Value 5',
        default=0,
        required=False,
        help='Temporary int value.')
    float_val1 = fields.Float(
        string='Float Value 1',
        default=0.0,
        required=False,
        help='Temporary float value.')
    float_val2 = fields.Float(
        string='Float Value 2',
        default=0.0,
        required=False,
        help='Temporary float value.')
    float_val3 = fields.Float(
        string='Float Value 3',
        default=0.0,
        required=False,
        help='Temporary float value.')
    float_val4 = fields.Float(
        string='Float Value 4',
        default=0.0,
        required=False,
        help='Temporary float value.')
    float_val5 = fields.Float(
        string='Float Value 5',
        default=0.0,
        required=False,
        help='Temporary float value.')
    text_val = fields.Text(
        string='Text',
        default='',
        required=False,
        help='Temporary text value.')

    @api.model
    def _get_domain(self, scenario, scanner):
        """
        Create a domain to find custom values.
        Use the fields shared_custom of scenario and scanner
        """
        # Domain if custom values are shared
        if scenario.shared_custom is True:
            return [
                ('scenario_id', '=', scenario.id),
                ('scanner_id.reference_document', '=',
                 scanner.reference_document),
                ('scanner_id.warehouse_id', '=', scanner.warehouse_id.id)]

        # Default domain
        return [
            ('scenario_id', '=', scenario.id),
            ('scanner_id', '=', scanner.id),
        ]

    @api.model
    def _get_values(self, scenario, scanner, model='', res_id=None,
                    domain=None):
        """
        Returns read customs line
        @param domain : list of tuple for search method
        """
        # Get the default search domain
        search_domain = self._get_domain(scenario, scanner)

        # Add custom values in search domain
        if domain is not None:
            search_domain.extend(domain)

        # Add model in search domain, if any
        if model:
            search_domain.append(('model', '=', model))

        # Add res_id in search domain, if any
        if res_id:
            search_domain.append(('res_id', '=', res_id))

        # Search for values
        ids = self.search(search_domain)

        # If ids were found, return data from these ids
        if ids:
            return self.read(ids, [])

        # No id found, return an empty list
        return []

    @api.model
    def _set_values(self, values):
        """
        values is a dict, from a 'read' function
        Get id in values and delete some fields
        """
        # Copy values to let original dict unchanged
        vals = values.copy()

        # Get id from values, in a list
        ids = [values.get('id', None)]

        # Remove unwanted fields from vals
        for key in ['id', 'scenario_id', 'scanner_id', 'model', 'res_id']:
            if key in vals:
                del vals[key]

        # Write new values
        return self.write(ids, vals)

    @api.model
    def _remove_values(self, scenario, scanner):
        """
        Unlink all the line links from current scenario
        """
        scanner_hardware_obj = self.env['scanner.hardware']
        scanner_ids = []

        # If custom values are shared, search for other hardware using the same
        if scenario.shared_custom is True:
            scanner_ids = scanner_hardware_obj.search([
                ('scenario_id', '=', scenario.id),
                ('warehouse_id', '=', scanner.warehouse_id.id),
                ('reference_document', '=', scanner.reference_document),
                ('id', '!=', scanner.id),
            ])

        # Search for values attached to the current scenario
        values_attached = self.search([
            ('scenario_id', '=', scenario.id),
            ('scanner_id', '=', scanner.id),
        ])

        # If other scanners are on the current scenario, attach the first
        if scanner_ids:
            return values_attached.write({'scanner_id': scanner_ids.id})

        # Else, delete the current custom values
        return values_attached.unlink()
