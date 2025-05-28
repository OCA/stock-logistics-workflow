Further modules need to implement this on stock.picking model:

``` python
def init(self):
      """
      This has to be called in every overriding module
      """
      self._create_index_for_grouping()


@api.model
def _get_index_for_grouping_fields(self):
      """
      This tuple is intended to be overriden in order to add fields
      used in groupings
      """
      return [
          "partner_id",
          "location_id",
          "location_dest_id",
          "picking_type_id",
      ]
```
