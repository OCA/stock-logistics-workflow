Odoo allows you to create batches of pickings by hand or automatically by
specifying some criteria on the picking type definition.

The approach in this addon is slightly different. It doesn't depend on the
picking type and is triggered on demand by the user with the use of a
specialized wizard.

The creation of the batch is based on the following criteria:

* A list of picking types to consider
* A list of stock device types available to the operator to process the batch.
* A maximum number of lines in the batch

Stock device types
##################

A stock device type is a new concept that allows to define a type of device that
can be used by an operator to process operations into the warehouse (like
a forklift, a compartmentalized trolleys, ...).

Depending on the device type, the resources available to complete the job
will be different. A this stage, 3 main criteria are considered:

* The maximum weight that can be handled by the device
* The maximum volume that can be handled by the device
* The number of bins/compartments available on the device

In addition to these criteria, 2 others criteria can be defined that will
be evaluated to select the appropriate device type a the start of the
batch creation process if more than one device type is available:

* A minimum picking volume to consider the device type,
* A sequence to define the order in which the device type will be
  considered.
