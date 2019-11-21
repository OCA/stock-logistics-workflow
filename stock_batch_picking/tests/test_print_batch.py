# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from .common import BatchPickingCommon
from ..report.print_batch import PrintBatch


class PrintBatchSorted(PrintBatch):

    def get_sorted_batch_pickings(self, pickings):
        return pickings.sorted(key=lambda o: o.product_id.id, reverse=True)


class TestPrintBatch(BatchPickingCommon):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestPrintBatch, self).setUp()
        (self.picking | self.picking2).action_assign()
        # unsorted print
        self.print_unsorted = PrintBatch(
            self.env.cr, self.env.uid, "test", self.env.context)
        self.print_unsorted.set_context([self.batch], None, self.batch.ids)
        # sorted print
        self.print_sorted = PrintBatchSorted(
            self.env.cr, self.env.uid, "test", self.env.context)
        self.print_sorted.set_context([self.batch], None, self.batch.ids)

    def test_print_batch_sort(self):
        ops = self.print_unsorted.objects[0].operations_by_loc.values()[0]
        ops_sorted = self.print_sorted.objects[0].operations_by_loc.values()[0]
        ops_ids = [o.id for o in ops]
        ops_sorted_ids = [o.id for o in ops_sorted]
        self.assertNotEqual(ops_ids, ops_sorted_ids)
        ops.sort(key=lambda o: o.product_id.id, reverse=True)
        self.assertEqual(ops_sorted, ops)
