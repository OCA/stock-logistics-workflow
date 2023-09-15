* Enable multi-step routes and location
* In warehouse, enable flag “Inter-warehouse transfers” and set:
    * receipt destination location (eg: “WH2/Stock”)
    * receipt operation type (eg: “WH2: Receipts”)
    * partner in picking (eg: “My Company (San Francisco), WH2”)
* Note: this must be done for all warehouses sending or receiving internal transfers.
* Create or open an existing “internal” operation type; enable field “Use for Inter-warehouse transfer”.
* Boolean "Disable Merge Picking Moves" is also available if you wish to maintain a 1 to 1 relation between outgoing pickings and incoming ones.
