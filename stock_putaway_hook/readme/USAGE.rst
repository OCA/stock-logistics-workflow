The modules that implement a new strategy have to follow the following steps.
The module ``stock_putaway_by_route`` should be used as reference.

Add the field to match on ``stock.putaway.rule`` in the model and in the view.
In the view, the field must have ``options="{'exclusive_selection': True}"``,
which will allow this module to dynamically build dynamic attrs, restricting the
selection of more than one field. (defining the readonly and required attrs in the view is therefore useless).

Add the strategy key, named after the new field name, in ``StockLocation._putaway_strategies``. Example:

::

  class StockLocation(models.Model):
      _inherit = "stock.location"

      @property
      def _putaway_strategies(self):
          strategies = super()._putaway_strategies
          return strategies + ["route_id"]

Pass the value to match with the putaway rule field in the context, in every
method calling ``StockLocation._get_putaway_strategy``. The name of the key in
the context is:``_putaway_<KEY>``, where KEY is the name of the new field on the
putaway rule. The value can be a unit, a recordset of any length or a
list/tuple. In latter cases, the putaway rule is selected if its field match any
value in the list/recordset.
