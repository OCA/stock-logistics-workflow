To configure this module, you need to:

1.  Go to a *Inventory \> Configuration \> Operation Types*.
2.  Set 'auto create lot' option for this operation type.
3.  Go to a *Inventory \> Master Data \> Products*.
4.  Set 'auto create lot' option for the products you need.


It's possible to configure by code a way to force the setting of the auto lot when
printing the detailed operation labels. To do so, pass the context key `force_auto_lot`
to the report. This is a simple example with a server action, but it can be done with
overriding methods as well:

```xml
     <record id="action_print_detailed_operation" model="ir.actions.server">
          <field name="name">Print detailed operations</field>
          <field name="model_id" ref="stock.model_stock_move_line" />
          <field
                name="binding_model_id"
                ref="stock.model_stock_move_line"
          />
          <field name="binding_view_types">list</field>
          <field name="state">code</field>
          <field name="code">
     if records:
          report = env["ir.actions.report"].sudo()._get_report("my_custom_module.my_custom_report_xml_id")
          action = report.with_context(force_auto_lot=True).report_action(records.ids)
          </field>
     </record>
