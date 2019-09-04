# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import OrderedDict

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

        for operation in self.operations_by_loc[locations]:
            if operation.product_id:
                product_id = operation.product_id.id
                products[product_id] = operation.product_id
                carrier[product_id] = (
                    operation.picking_id.carrier_id and
                    operation.picking_id.carrier_id.partner_id.name or ''
                )
                qty = product_qty.setdefault(product_id, 0.0)
                product_qty[product_id] = qty + operation.product_qty
            elif operation.package_id:
                package = operation.package_id
                quants = package.quant_ids
                for quant in quants:
                    product_id = quant.product_id.id
                    products[product_id] = quant.product_id
                    carrier[product_id] = (
                        operation.picking_id.carrier_id and
                        operation.picking_id.carrier_id.partner_id.name or ''
                    )
                    qty = product_qty.setdefault(product_id, 0.0)
                    product_qty[product_id] = qty + operation.product_qty

        # sort product by default_code
        products = OrderedDict(sorted(
            products.items(),
            key=lambda product: (product[1].default_code, product[1].id)
        ))

        for product_id in products:
            yield (
                products[product_id], product_qty[product_id],
                carrier[product_id]
            )
