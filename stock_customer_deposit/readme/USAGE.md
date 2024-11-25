To use this module, you need to:

Create Customer deposits:

1. Go to Sales > Quotations.
2. Create new quotation to the desired customer.
3. Activate **customer deposit** in quotation.
4. Add storable product in order lines.
5. Add quantity you will keep as a deposit.
6. Discount will be applied following Odoo rules.
7. *Confirm* quotation.
8. Sale is now ready for invoicing.
9. A picking will be created. This picking is an operation Customer Deposit and it's **internal** operation.
10. Click on smart button with delivery.
11. Set quantity done in operations or click on **Set Quantities**.
12. Update location destination if it's necessary in operations detailed.
13. Click on **Validate**.

View Customer deposits:

1. Go to Inventory > Reporting > Locations.
2. Filter the owner by the customer you created the order.
3. Go to Sales > Customers.
4. A smart button with deposits is shown if customer has deposits in some warehouse.

Deliver customer deposits:

1. Go to Sales > Quotation.
2. Create a new quotation.
3. Select customer who has a deposit in your warehouse.
4. In page Other Info choose warehouse where deposit is located. (Only if multi-warehouse is activated)
5. Smart button **Deposits** with deposits is displayed if the customer has deposits in the chosen warehouse.
6. Add line with product in deposit.
7. As a product in deposit, a button **Customer deposit** will appear. If you do not have enough in deposit, button will be grey. If you click on the button **Customer deposit**, you can view the deposits for that product.
8. You will only be able to confirm the order if you use less quantity than you have in the deposit.
9. If you try to confirm the order with more quantity than you have in deposit, a validation error will show.
10. Check the deposit line has 100% discount.


