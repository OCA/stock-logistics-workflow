# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from os.path import commonprefix


class BatchAggregation(object):
    """ Group operations from a single batch by source and dest locations
    """

    def __init__(self, batch_id, operations_by_loc):
        self.batch_id = batch_id
        self.operations_by_loc = operations_by_loc

    def exists(self):
        return False

    @property
    def picker_id(self):
        return self.batch_id.picker_id

    @property
    def batch_name(self):
        return self.batch_id.name

    @property
    def batch_notes(self):
        return self.batch_id.notes or u''

    def __hash__(self):
        return hash(self.batch_id.id)

    def __eq__(self, other):
        return self.batch_id.id == other.batch_id.id

    def iter_locations(self):
        """ Iterate over operations grouped by (loc_source, loc_dest)
        and return informations to display in report for these locs.

        Informations are like:
        (
            (loc_source_name, loc_dest_name),
            (
                (product1, product1_qty, product1_carrier)
                (product2, product2_qty, product2_carrier)
                [...]
            )
        )
        """
        for locations in self.operations_by_loc:
            offset = commonprefix(locations).rfind('/') + 1
            display_locations = tuple(
                loc[offset:].strip() for loc in locations
            )
            yield display_locations, self._product_quantity(locations)

    def _product_quantity(self, locations):
        """ Iterate over the different products concerned by the operations for
        the specified locations with their total quantity, sorted by product
        default_code

        locations: a tuple (source_location, dest_location)
        """
        products = {}
        product_qty = {}
        carrier = {}
        operations = self.operations_by_loc[locations]
        for operation in operations:
            p_code = operation.product_id.default_code
            products[p_code] = operation.product_id
            carrier[p_code] = (
                operation.picking_id.carrier_id and
                operation.picking_id.carrier_id.partner_id.name or ''
            )
            if p_code not in product_qty:
                product_qty[p_code] = operation.product_qty
            else:
                product_qty[p_code] += operation.product_qty
        for p_code in sorted(products):
            yield products[p_code], product_qty[p_code], carrier[p_code]
