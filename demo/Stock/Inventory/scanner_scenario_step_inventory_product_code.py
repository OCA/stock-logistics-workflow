# flake8: noqa
# Use <m> or <message> to retrieve the data transmitted by the scanner.
# Use <t> or <terminal> to retrieve the running terminal browse record.
# Put the returned action code in <act>, as a single character.
# Put the returned result or message in <res>, as a list of strings.
# Put the returned value in <val>, as an integer

from datetime import datetime

# No current inventory, create a new one
if not terminal.tmp_val1:
    stock_inventory_obj = env['stock.inventory']
    stock_inventory_id = stock_inventory_obj.create({
        'name': '%s : %s' % (terminal.code, datetime.today().strftime('%Y-%m-%d %H:%M:%S')),
    })
    terminal.write({'tmp_val1': stock_inventory_id.id})
elif tracer == 'location' and terminal.tmp_val2:
    stock_location_obj = env['stock.location']
    stock_inventory_line_obj = env['stock.inventory.line']

    stock_inventory_id = int(terminal.tmp_val1)
    default_code = terminal.tmp_val2
    quantity = float(terminal.tmp_val3)
    location = stock_location_obj.search([('name', '=', message)])[0]

    product = model.search([('default_code', '=', default_code)])[0]

    stock_inventory_line_obj.create({
        'inventory_id': stock_inventory_id,
        'product_id': product.id,
        'product_uom_id': product.uom_id.id,
        'product_qty': quantity,
        'location_id': location.id,
    })

    terminal.write({'tmp_val2': '', 'tmp_val3': ''})

act = 'T'
res = [
    _('Product code ?'),
]
