.. code-block:: python

      self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    product,
                    1,
                    uom,
                    customer_location,
                    "procurement",
                    "procurement",
                    company,
                    {"location_id": output_location},
                )
            ]
        )
